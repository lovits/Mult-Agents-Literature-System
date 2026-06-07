# EviReview API Application Layer

This directory contains the Phase 2A application layer, Phase 2B FastAPI/RQ adapter, and Phase 2C backend paper/report assets.

Implemented boundaries:

- `app.schemas.runs`: review-audit input and lifecycle contracts.
- `app.repositories.sqlite_run_repository`: local SQLite dev-mode persistence for runs, jobs, results, and trace events.
- `app.services.review_audit_service`: application use cases suitable for future FastAPI route handlers.
- `app.services.paper_service`: Markdown paper parsing and persisted evidence-block construction.
- `app.services.report_service`: persisted Markdown report generation for completed review audits.
- `app.main:create_app`: FastAPI application factory.
- `app.queue.rq_queue`: Redis/RQ delivery adapter.

The API never accepts or stores provider API keys. Raw weakness/evidence inputs are persisted in SQLite for worker use and are not returned by run endpoints. Review-audit requests may explicitly select `weakness_generator=minimax` and `verifier=minimax`; provider credentials remain worker environment variables.

Phase 2C routes:

- `POST /api/papers/import`
- `POST /api/papers/{paper_id}/review-audit`
- `GET /api/papers/{paper_id}`
- `GET /api/papers/{paper_id}/sections`
- `GET /api/papers/{paper_id}/evidence-blocks`
- `GET /api/papers/{paper_id}/versions`
- `GET /api/papers/{paper_id}/versions/{version_id}/evidence-blocks`
- `POST /api/runs/{run_id}/report`
- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/markdown`
- `POST /api/experiments`
- `GET /api/experiments`
- `GET /api/experiments/{manifest_id}`
- `POST /api/experiments/{manifest_id}/runs/{run_id}`
- `POST /api/experiments/{manifest_id}/paper-audits`
- `GET /api/papers`
- `GET /api/papers/{paper_id}/runs`
- `GET /api/runs/{run_id}/workspace`
- `GET /api/runs/{run_id}/agent-trace`
- `GET /workspace/`

The paper-scoped review-audit endpoint snapshots the active immutable paper version and ordered evidence-block IDs into the run input. It does not require the client to send evidence text, and later paper re-imports do not alter historical runs. Existing pre-version paper assets are backfilled into an initial immutable version during repository initialization.

Experiment manifests connect a named dataset version and experiment-level configuration to existing audit runs. Manifest snapshots expose immutable paper versions, run configuration/status, and report metadata without returning raw run inputs, evidence text, or internal artifact paths.

The manifest-scoped paper-audit endpoint schedules 1 to 100 persisted-paper audits with ordered partial-success results. Each run snapshots the paper version active at scheduling time and is attached to the manifest, including runs whose queue delivery failed after persistence. Item failures return stable public error codes rather than internal exception details.

Phase 3 starts with a dependency-free Paper Workspace served at `/workspace/`. Its dedicated workspace read model exposes the selected run's public weakness/evidence/verification/ranking/trace/report chain while excluding persistence columns, artifact paths, queue tokens, and internal errors. This local research workspace intentionally has no authentication and must not be exposed as a public service.

The backend review audit now executes through an explicit dependency-free Agent-RAG graph with `generate_or_import_weaknesses`, `plan_weakness_queries`, `retrieve_evidence`, `verify_weaknesses`, and `rank_findings` nodes. The stable deterministic workflow entrypoint remains compatible with existing experiment callers, while `/api/runs/{run_id}/agent-trace` exposes only node name, status, and error type for backend observability.

Install and run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r services/api/requirements.txt
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/uvicorn app.main:create_app --factory --reload
```

Run API and backend tests:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/api -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/backend -v
```

HTTP handlers call the service layer rather than repository or core functions directly.
