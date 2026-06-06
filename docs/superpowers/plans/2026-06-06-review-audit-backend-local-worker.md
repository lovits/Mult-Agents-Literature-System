# Review Audit Backend and Local Worker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the dependency-free Phase 2A backend foundation that turns a deterministic review audit into a persisted, traceable, recoverable local job without implementing the frontend or introducing FastAPI/RQ dependencies.

**Architecture:** `services/api` owns application use cases and SQLite persistence; `services/worker` owns queued-job execution and calls `packages/evireview_core`. HTTP routes and Redis/RQ remain adapters for a later dependency-approved increment. Raw evidence and weakness payloads are stored only in the local SQLite dev database, while committed fixtures remain small and license-safe.

**Tech Stack:** Python 3 standard library, `sqlite3`, dataclasses, JSON, `unittest`, existing `evireview_core`.

---

## Scope Check

Included:

- SQLite dev-mode schema for runs, jobs, inputs, results, and trace events.
- Application service for creating and reading review-audit runs.
- Local worker for claiming queued jobs and executing `run_deterministic_review_audit`.
- Recoverable state transitions: `created -> queued -> running -> succeeded|failed`.
- Tests for persistence, lifecycle, cross-paper isolation inherited from core, failure recording, and restart recovery.
- Documentation of the future FastAPI/RQ adapter boundary.

Excluded:

- Frontend.
- FastAPI, Pydantic, Uvicorn, SQLAlchemy, Alembic, Redis, RQ, Celery.
- Provider/GLM execution.
- Qdrant/dense retrieval.
- Changes to experiment data or reports.

## File Structure

Create:

```text
services/
  api/
    app/
      __init__.py
      repositories/
        __init__.py
        sqlite_run_repository.py
      schemas/
        __init__.py
        runs.py
      services/
        __init__.py
        review_audit_service.py
    README.md
  worker/
    __init__.py
    tasks/
      __init__.py
      review_audit.py
    README.md

tests/
  backend/
    __init__.py
    test_sqlite_run_repository.py
    test_review_audit_service.py
    test_local_review_audit_worker.py
```

Modify:

```text
docs/progress/evireview_current_progress_2026-05-30.md
```

## Shared Commands

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. python3 -m unittest discover -s tests/backend -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. python3 -m unittest discover -s tests/evireview_core -v
PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q services/api services/worker tests/backend
git diff --check
```

---

### Task 1: Run and Job Schemas

**Files:**
- Create: `services/api/app/schemas/runs.py`
- Create: `tests/backend/test_review_audit_service.py`

- [ ] Write failing tests for valid lifecycle values and request normalization.
- [ ] Verify failure because `app.schemas.runs` does not exist.
- [ ] Implement dataclasses `ReviewAuditRequest`, `RunRecord`, `JobRecord`, and lifecycle constants.
- [ ] Verify the focused schema tests pass.

The request schema must accept:

```python
ReviewAuditRequest(
    paper_id="p1",
    weaknesses=[Weakness(...)],
    evidence_blocks=[EvidenceBlock(...)],
    top_k=5,
    finding_top_k=3,
)
```

It must reject empty `paper_id`, non-positive `top_k`, and cross-paper inputs.

### Task 2: SQLite Run Repository

**Files:**
- Create: `services/api/app/repositories/sqlite_run_repository.py`
- Create: `tests/backend/test_sqlite_run_repository.py`

- [ ] Write failing tests for schema creation, run/job persistence, result persistence, event ordering, and recovery of a running job.
- [ ] Verify failure because repository does not exist.
- [ ] Implement SQLite schema and repository methods.
- [ ] Verify focused repository tests pass.

Required tables:

```text
runs(run_id, paper_id, status, config_json, input_json, result_json, error, created_at, updated_at)
jobs(job_id, run_id, status, progress, error, created_at, updated_at)
job_events(event_id, job_id, event_type, payload_json, created_at)
```

Required repository behavior:

- Enable foreign keys.
- Use explicit transactions.
- Store JSON with deterministic key ordering.
- Recover stale `running` jobs to `queued` on worker startup.
- Never silently overwrite a succeeded result.

### Task 3: Review Audit Application Service

**Files:**
- Create: `services/api/app/services/review_audit_service.py`
- Modify: `tests/backend/test_review_audit_service.py`

- [ ] Write failing tests for creating a queued run/job and reading run status/findings/trace.
- [ ] Verify failure because service does not exist.
- [ ] Implement service orchestration without importing worker or HTTP libraries.
- [ ] Verify focused service tests pass.

The service must:

- Generate run/job IDs.
- Persist request inputs.
- Return serializable dictionaries suitable for a future FastAPI route.
- Expose `get_run`, `get_findings`, and `get_trace`.

### Task 4: Local Review Audit Worker

**Files:**
- Create: `services/worker/tasks/review_audit.py`
- Create: `tests/backend/test_local_review_audit_worker.py`

- [ ] Write failing tests for queued job success, failure recording, and startup recovery.
- [ ] Verify failure because worker task does not exist.
- [ ] Implement `run_next_job(repository)` and `recover_and_run(repository)`.
- [ ] Verify focused worker tests pass.

Worker rules:

- Claim one queued job at a time.
- Transition job and run to `running`.
- Rehydrate core dataclasses from stored input.
- Call `run_deterministic_review_audit`.
- Persist result before marking succeeded.
- Record failure context without deleting input or prior trace.

### Task 5: Backend Boundary Documentation

**Files:**
- Create: `services/api/README.md`
- Create: `services/worker/README.md`
- Modify: `docs/progress/evireview_current_progress_2026-05-30.md`

- [ ] Document how to run backend tests.
- [ ] Document why FastAPI/RQ are deferred.
- [ ] Document that no API key is accepted or stored.
- [ ] Record Phase 2A completion and remaining Phase 2B dependencies.

### Task 6: Final Verification

- [ ] Run backend tests.
- [ ] Run core regression tests.
- [ ] Run compileall.
- [ ] Run `git diff --check`.
- [ ] Run the existing secret scan excluding `.git` and `.omx`.
- [ ] Confirm no frontend files, experiment data, or experiment reports changed.
- [ ] Commit with Lore protocol and push.

## Inputs Needed From User

No user-provided input is required for Phase 2A.

Before Phase 2B, obtain explicit approval to add and install:

```text
FastAPI
Pydantic
Uvicorn
Redis
RQ
```

PostgreSQL, SQLAlchemy, Alembic, Qdrant, provider API keys, and frontend dependencies remain later decisions.
