# EviReview-Lite Full-stack Agent RAG Architecture

Date: 2026-05-30

## 1. Reference Projects

This design is derived from high-adoption open-source AI/RAG systems:

| Project | What to borrow | Notes |
| --- | --- | --- |
| Dify | workflow / agent / RAG separation, web app + API + worker service shape | https://github.com/langgenius/dify |
| RAGFlow | document parsing, chunk visualization, grounded citations, RAG + agent context engine | https://github.com/infiniflow/ragflow |
| Open WebUI | SvelteKit + Python/FastAPI split, local-first AI UI pattern | https://github.com/open-webui/open-webui |
| AnythingLLM | monorepo layout with frontend, server, collector, vector DB adapters | https://github.com/Mintplex-Labs/anything-llm |
| LangGraph | explicit graph/state-machine orchestration for resilient agents | https://github.com/langchain-ai/langgraph |
| Haystack | modular retrieval/routing/generation pipelines | https://github.com/deepset-ai/haystack |
| Qdrant | vector DB with payload filtering and production API | https://github.com/qdrant/qdrant |

## 2. Recommended Stack

### Frontend

Use `Next.js + TypeScript + Tailwind CSS + shadcn/ui`.

Rationale:

1. Dify uses the Next.js ecosystem, and it is a good fit for workflow-heavy dashboards.
2. The thesis product needs tables, review workspaces, evidence panels, filters, uploads, and report pages; React/Next has stronger component and data-table ecosystem than a smaller UI stack.
3. Next.js can start as an SPA-style app and later add server-side rendering only where useful.

Frontend libraries:

- `Next.js`
- `TypeScript`
- `Tailwind CSS`
- `shadcn/ui`
- `TanStack Query` for API cache and async states
- `TanStack Table` for weakness/evidence/result tables
- `Zustand` for lightweight UI state
- `react-pdf` or browser PDF viewer integration for source paper preview
- `react-markdown` for rendered reports

### Backend

Use `FastAPI + Pydantic + SQLAlchemy + Alembic + Celery/RQ + Redis`.

Rationale:

1. The existing experiments are Python, so keeping backend and research pipeline in Python avoids wrapping Python logic through a Node server.
2. Open WebUI uses a Python/FastAPI backend with a separate frontend dev server; this matches AI application ergonomics.
3. Agent/RAG tasks are long-running and should not block request handlers, so ingestion, embedding, retrieval evaluation, and verifier jobs should run in workers.

Backend libraries:

- `FastAPI` for REST API and SSE streaming
- `Pydantic` for request/response schemas
- `SQLAlchemy` + `Alembic` for relational persistence
- `PostgreSQL` for app metadata
- `Redis` for cache, job state, and Celery broker
- `Celery` or `RQ` for async jobs
- `structlog` or standard `logging` with JSON formatter

### Agent RAG

Use `LangGraph + LlamaIndex-style data abstractions + Qdrant + BM25`.

Rationale:

1. LangGraph is a good fit for EviReview because the workflow is not a one-shot chain; it has explicit states: ingest paper, extract weaknesses, retrieve evidence, verify, rank, report.
2. Haystack-style modular pipelines are worth copying conceptually: separate retriever, reranker, generator, verifier, and router nodes.
3. Qdrant gives vector search plus metadata filters for `paper_id`, `section_type`, `claim_type`, `dataset`, and `experiment_id`.
4. BM25 should remain in the system. Your experiments already show lexical retrieval is a useful baseline, and academic text often benefits from hybrid retrieval.

Agent/RAG components:

- parser: PDF/Markdown to structured sections
- indexer: chunks, claims, figures/tables metadata
- retriever: BM25 + vector + hybrid fusion
- verifier: checks weakness against retrieved evidence
- ranker: severity, support, novelty, section confidence
- reporter: Markdown/PDF audit report
- evaluator: SubstanReview / CLAIMCHECK / local OpenReview benchmark runners

## 3. System Architecture

```text
Browser
  |
  v
Next.js Frontend
  |-- upload paper / select dataset
  |-- paper workspace
  |-- weakness table
  |-- evidence viewer
  |-- verifier trace
  |-- experiment dashboard
  |
  v
FastAPI Backend
  |-- auth/session API
  |-- project/paper/review API
  |-- job API
  |-- report API
  |-- SSE streaming API
  |
  +--> PostgreSQL
  |      |-- users/projects/papers/reviews/jobs/results
  |
  +--> Redis
  |      |-- queue/cache/job progress
  |
  +--> Worker Service
  |      |-- ingestion jobs
  |      |-- embedding jobs
  |      |-- retrieval jobs
  |      |-- verifier jobs
  |      |-- report jobs
  |
  +--> Agent RAG Engine
         |-- LangGraph workflow
         |-- retriever adapters
         |-- verifier nodes
         |-- evaluator nodes
         |
         +--> Qdrant vector store
         +--> local BM25 index
         +--> object storage / local files
         +--> LLM provider
```

## 4. Repository Layout

Recommended monorepo:

```text
apps/
  web/
    app/
      (dashboard)/
        projects/
        papers/
        experiments/
        reports/
      api-client/
      layout.tsx
      page.tsx
    components/
      paper/
      weakness/
      evidence/
      verifier/
      experiments/
      common/
    lib/
      api.ts
      query.ts
      routes.ts
      formatters.ts
    stores/
      workspace-store.ts
    styles/
    package.json

services/
  api/
    app/
      main.py
      core/
        config.py
        logging.py
        security.py
      api/
        routes/
          projects.py
          papers.py
          reviews.py
          jobs.py
          rag.py
          reports.py
          experiments.py
        deps.py
      schemas/
      models/
      repositories/
      services/
      db/
        migrations/
    pyproject.toml

  worker/
    worker.py
    tasks/
      ingest.py
      index.py
      retrieve.py
      verify.py
      evaluate.py
      report.py

packages/
  evireview_core/
    parsers/
      markdown_parser.py
      pdf_parser.py
      section_parser.py
    rag/
      chunking.py
      bm25.py
      vector_store.py
      hybrid_retriever.py
      reranker.py
    agents/
      graph.py
      state.py
      nodes/
        extract_weaknesses.py
        retrieve_evidence.py
        verify_support.py
        rank_findings.py
        write_report.py
    evaluation/
      substanreview.py
      claimcheck.py
      metrics.py
    reporting/
      markdown.py
      citations.py
    types.py

infra/
  docker-compose.yml
  Dockerfile.api
  Dockerfile.worker
  Dockerfile.web
  nginx.conf
  qdrant/
  postgres/

docs/
  design/
  research/
  api/

code/
  experiments/
    evireview_a/
      src/
      data/
      reports/
```

Keep the current `code/experiments/evireview_a` as the research sandbox. Move stable logic into `packages/evireview_core` only after it has passed experiments.

## 5. Backend Architecture

Use a layered backend:

```text
API Route -> Service -> Repository -> Database
                 |
                 +-> Job Queue
                 +-> Agent RAG Engine
```

Rules:

1. Routes only validate input and return response schemas.
2. Services hold business logic: create project, ingest paper, run verifier, generate report.
3. Repositories isolate SQL queries.
4. Worker tasks call the same services/core modules as API, not duplicated scripts.
5. Agent graph nodes must be pure enough to test with local JSON fixtures.

Core API resources:

- `Project`
- `Paper`
- `PaperSection`
- `Review`
- `Weakness`
- `EvidenceBlock`
- `RetrievalRun`
- `VerifierRun`
- `Finding`
- `Report`
- `ExperimentRun`
- `Job`

## 6. Frontend Architecture

Main pages:

```text
/projects
/projects/:id
/papers/:paperId
/papers/:paperId/workspace
/experiments
/experiments/:runId
/reports/:reportId
```

Primary UI surfaces:

1. Project dashboard: papers, status, latest runs.
2. Paper workspace: left paper outline, center evidence/section viewer, right weakness/verifier panel.
3. Weakness table: category, severity, support label, evidence count, confidence.
4. Evidence viewer: retrieved chunks with source section and citation.
5. Verifier trace: query, retrieved evidence, decision, rationale, failure mode.
6. Experiment dashboard: SubstanReview/CLAIMCHECK/local OpenReview metrics.
7. Report page: generated audit report with export.

Frontend state split:

- Server state: TanStack Query.
- Local UI state: Zustand.
- Form state: React Hook Form + Zod.
- Long job state: SSE from FastAPI, with polling fallback.

## 7. Agent RAG Workflow

Use a LangGraph state machine:

```text
START
  -> parse_paper
  -> extract_claims_and_sections
  -> extract_or_import_weaknesses
  -> retrieve_candidate_evidence
  -> rerank_evidence
  -> verify_support
  -> classify_failure_mode
  -> rank_findings
  -> write_audit_report
  -> END
```

Graph state:

```python
class ReviewAuditState(TypedDict):
    project_id: str
    paper_id: str
    review_id: str | None
    sections: list[PaperSection]
    claims: list[PaperClaim]
    weaknesses: list[Weakness]
    evidence_candidates: dict[str, list[EvidenceBlock]]
    verifier_results: list[VerifierResult]
    ranked_findings: list[Finding]
    report_markdown: str | None
    errors: list[str]
```

Verifier labels:

- `Supported`
- `Partially Supported`
- `Mentioned but Not Problem`
- `Generic / Vague`
- `Unsupported`
- `Contradicted`

Evaluation modes:

- SubstanReview: review-internal substantiation benchmark.
- CLAIMCHECK: paper-claim grounded weakness benchmark.
- Local OpenReview: end-to-end application dataset.

## 8. Storage Design

PostgreSQL:

- app metadata
- job status
- paper/review records
- weakness/evidence/verifier results
- report metadata

Qdrant:

- evidence chunks
- paper claims
- review weakness embeddings
- metadata payloads:
  - `paper_id`
  - `project_id`
  - `section_type`
  - `source`
  - `dataset`
  - `run_id`

Local/object storage:

- uploaded PDFs
- parsed Markdown
- generated reports
- experiment artifacts

Redis:

- job queue
- progress events
- short-lived cache

## 9. MVP Scope

Build this first:

1. Next.js dashboard and paper workspace.
2. FastAPI project/paper/job/report APIs.
3. Worker for Markdown ingestion, chunking, BM25 retrieval, Qdrant indexing.
4. Agent graph with retrieval -> verification -> report.
5. Experiment dashboard reading existing JSON metrics.
6. Docker Compose for web, api, worker, postgres, redis, qdrant.

Defer:

- multi-user RBAC
- visual workflow builder
- collaborative annotation UI
- multimodal figure/table understanding
- full PDF layout editor
- Kubernetes deployment

## 10. Recommended First Implementation Milestones

1. Create `apps/web`, `services/api`, `services/worker`, `packages/evireview_core`.
2. Move stable experiment code from `code/experiments/evireview_a/src/common.py` into `packages/evireview_core`.
3. Add Docker Compose with PostgreSQL, Redis, Qdrant.
4. Implement paper upload/import and job progress.
5. Implement `ReviewAuditState` and a minimal LangGraph workflow.
6. Connect frontend workspace to one completed verifier run.
7. Add experiment dashboard for SubstanReview and CLAIMCHECK reports.
