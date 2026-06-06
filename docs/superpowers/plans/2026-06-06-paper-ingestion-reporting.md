# Paper Ingestion and Audit Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backend-only Markdown paper ingestion pipeline and persisted, traceable review-audit Markdown reports on top of the existing Agent-RAG run service.

**Architecture:** Keep domain transformations in `evireview_core`, persistence in the existing SQLite repository, orchestration in focused API services, and HTTP translation in dedicated FastAPI routers. Runtime artifacts live under ignored `storage/`; public API responses expose research evidence and report content but never raw run inputs, provider errors, attempt tokens, or queue payloads.

**Tech Stack:** Python 3.14, FastAPI, Pydantic, SQLite, existing `evireview_core` Markdown parser, `unittest`.

---

## Scope Boundaries

- Implement Markdown text ingestion only. PDF/MinerU ingestion remains a later adapter.
- Reuse `iter_sections` and `chunk_text`; do not add parsing or storage dependencies.
- Store papers, parsed sections, evidence blocks, and report metadata in SQLite.
- Store generated Markdown reports under `storage/reports/`.
- Label every generated report as `silver diagnostic`.
- Do not add frontend screens, provider calls, manual annotation, or experiment-data migrations.

## File Structure

- Create `packages/evireview_core/evireview_core/reporting/markdown_report.py`: deterministic Markdown rendering from a completed run and trace.
- Create `packages/evireview_core/evireview_core/reporting/__init__.py`: public reporting export.
- Create `services/api/app/services/paper_service.py`: Markdown-to-sections/evidence-block orchestration.
- Create `services/api/app/services/report_service.py`: completed-run-to-report orchestration and artifact write.
- Create `services/api/app/api/routes/papers.py`: paper import/read endpoints.
- Create `services/api/app/api/routes/reports.py`: report create/read endpoints.
- Modify `services/api/app/repositories/sqlite_run_repository.py`: paper, section, evidence-block, and report persistence.
- Modify `services/api/app/schemas/http.py`: strict paper import and report response schemas.
- Modify `services/api/app/main.py`: wire services and routers.
- Create focused tests under `tests/evireview_core`, `tests/backend`, and `tests/api`.

### Task 1: Lock Markdown report behavior

**Files:**
- Create: `tests/evireview_core/test_markdown_report.py`
- Create: `packages/evireview_core/evireview_core/reporting/__init__.py`
- Create: `packages/evireview_core/evireview_core/reporting/markdown_report.py`

- [ ] **Step 1: Write the failing report-rendering test**

Assert that the renderer includes the run/paper identity, `silver diagnostic` boundary, ranked finding fields, evidence identifiers, and queued/running/succeeded trace summary while omitting internal errors.

- [ ] **Step 2: Run the test to verify RED**

Run: `PYTHONPATH=packages/evireview_core .venv/bin/python -m unittest tests.evireview_core.test_markdown_report -v`

Expected: FAIL because `evireview_core.reporting` does not exist.

- [ ] **Step 3: Implement the minimal deterministic renderer**

Expose `render_review_audit_markdown(run, trace) -> str`. Render only public run/result fields supplied by the service and never interpolate `error`, raw input JSON, or event payload JSON.

- [ ] **Step 4: Run the test to verify GREEN**

Run: `PYTHONPATH=packages/evireview_core .venv/bin/python -m unittest tests.evireview_core.test_markdown_report -v`

Expected: PASS.

### Task 2: Persist imported paper assets

**Files:**
- Modify: `services/api/app/repositories/sqlite_run_repository.py`
- Create: `tests/backend/test_paper_service.py`
- Create: `services/api/app/services/paper_service.py`

- [ ] **Step 1: Write failing paper-service tests**

Assert that importing Markdown persists one paper, ordered sections, and deterministic evidence blocks; re-importing the same `paper_id` replaces prior derived assets atomically; short valid sections remain usable evidence.

- [ ] **Step 2: Run the tests to verify RED**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.backend.test_paper_service -v`

Expected: FAIL because `PaperService` and paper persistence methods do not exist.

- [ ] **Step 3: Implement schema and service**

Add `papers`, `paper_sections`, and `evidence_blocks` tables. Add repository methods for atomic replacement and ordered reads. Build deterministic section and block IDs from paper identity, ordinal, section path, and normalized text; use `chunk_text(..., min_tokens=1)` so short research sections are retained.

- [ ] **Step 4: Run backend tests to verify GREEN**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.backend.test_paper_service tests.backend.test_sqlite_run_repository -v`

Expected: PASS.

### Task 3: Expose paper asset APIs

**Files:**
- Modify: `services/api/app/schemas/http.py`
- Create: `services/api/app/api/routes/papers.py`
- Modify: `services/api/app/main.py`
- Create: `tests/api/test_fastapi_papers.py`

- [ ] **Step 1: Write failing API tests**

Assert `POST /api/papers/import` returns counts without echoing Markdown, and the paper, sections, and evidence-block endpoints return persisted assets. Assert unknown papers return 404 and extra request fields return 422.

- [ ] **Step 2: Run the tests to verify RED**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.api.test_fastapi_papers -v`

Expected: FAIL with 404 for missing routes.

- [ ] **Step 3: Implement strict request schema and router**

Add `PaperImportInput` with `extra="forbid"` and non-empty identifiers/title/Markdown. Route every operation through `PaperService`; translate `KeyError` to 404.

- [ ] **Step 4: Run the API tests to verify GREEN**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.api.test_fastapi_papers -v`

Expected: PASS.

### Task 4: Persist and expose completed audit reports

**Files:**
- Modify: `services/api/app/repositories/sqlite_run_repository.py`
- Create: `services/api/app/services/report_service.py`
- Create: `services/api/app/api/routes/reports.py`
- Modify: `services/api/app/main.py`
- Create: `tests/backend/test_report_service.py`
- Create: `tests/api/test_fastapi_reports.py`

- [ ] **Step 1: Write failing report-service and API tests**

Assert reports can only be created for succeeded runs, write Markdown beneath the configured storage root, persist metadata, and can be read through metadata and Markdown endpoints. Assert missing resources return 404, incomplete runs return 409, and internal errors never appear.

- [ ] **Step 2: Run the tests to verify RED**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.backend.test_report_service tests.api.test_fastapi_reports -v`

Expected: FAIL because report persistence, service, and routes do not exist.

- [ ] **Step 3: Implement report persistence and service**

Add a `reports` table, repository CRUD methods, and `ReportService`. Derive `storage_root` from the SQLite parent, write reports atomically, and return public metadata plus Markdown only through the explicit content endpoint.

- [ ] **Step 4: Run report tests to verify GREEN**

Run: `PYTHONPATH=services/api:packages/evireview_core .venv/bin/python -m unittest tests.backend.test_report_service tests.api.test_fastapi_reports -v`

Expected: PASS.

### Task 5: Verify the complete backend increment

**Files:**
- Modify: `docs/progress/agent_rag_refactor_progress_2026-06-06.md` or create it if absent.

- [ ] **Step 1: Run all automated tests**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/api -v
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/backend -v
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/evireview_core -v
.venv/bin/python -m compileall -q packages/evireview_core services/api services/worker
.venv/bin/python -m pip check
git diff --check
```

Expected: all tests pass, compile/pip/diff checks produce no errors.

- [ ] **Step 2: Restart local API and worker**

Restart the persistent Uvicorn and RQ processes so the running app loads Phase 2C routes.

- [ ] **Step 3: Run real HTTP verification**

Import a sample Markdown paper, read sections/evidence blocks, create a review-audit using imported blocks, wait for RQ success, create a report, and read its Markdown. Verify `/docs` and `/health`.

- [ ] **Step 4: Run secret scan**

Run:

```bash
rg -n "(GLM|ZHIPU|ZAI)_API_KEY\\s*=\\s*['\\\"]?[A-Za-z0-9._-]{12,}" . --glob '!.git/**'
```

Expected: exit code 1 with no output.

- [ ] **Step 5: Update progress documentation, create a Lore commit, and push**

Document implemented routes, verification evidence, simplifications, and remaining risks. Commit with constraints that Phase 2C is Markdown-only, silver-diagnostic-only, backend-only, and contains no provider credentials.
