# Persisted Paper Review Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create review-audit runs directly from imported paper assets without requiring clients or run inputs to duplicate evidence-block text.

**Architecture:** Add a paper-scoped audit endpoint that snapshots the imported paper's ordered evidence-block IDs into the queued run. The worker resolves that immutable ID set from SQLite at execution time, preserving the existing deterministic core workflow and legacy inline-evidence endpoint.

**Tech Stack:** Python 3.14, FastAPI, Pydantic, SQLite, Redis/RQ, existing `evireview_core`, `unittest`.

---

## Scope Boundaries

- Keep `POST /api/runs/review-audit` backward compatible for inline evidence.
- Add `POST /api/papers/{paper_id}/review-audit` for persisted paper evidence.
- Persist only evidence-block IDs in paper-scoped run input; do not duplicate evidence text.
- Resolve every snapshotted block ID before running; fail explicitly if assets were replaced or deleted.
- Do not add frontend, external model calls, PDF ingestion, authentication, or new dependencies.

## File Structure

- Modify `services/api/app/schemas/http.py`: strict paper-scoped audit input containing weaknesses and ranking controls only.
- Modify `services/api/app/repositories/sqlite_run_repository.py`: ordered evidence-block ID snapshot and exact ID resolution.
- Modify `services/api/app/services/review_audit_service.py`: paper-scoped audit creation and shared delivery compensation.
- Modify `services/api/app/api/routes/papers.py`: paper-scoped review-audit endpoint.
- Modify `services/worker/tasks/review_audit.py`: resolve inline evidence or persisted evidence IDs.
- Modify focused tests under `tests/backend` and `tests/api`.

### Task 1: Lock persisted evidence resolution

**Files:**
- Modify: `tests/backend/test_sqlite_run_repository.py`
- Modify: `tests/backend/test_local_review_audit_worker.py`
- Modify: `services/api/app/repositories/sqlite_run_repository.py`
- Modify: `services/worker/tasks/review_audit.py`

- [ ] **Step 1: Write failing repository and worker tests**

Assert the repository returns imported evidence block IDs in stable order and resolves the exact requested ID order. Assert the worker executes a queued payload containing `evidence_block_ids` without inline `evidence_blocks`, and fails rather than silently shrinking the evidence set when an ID is missing.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest \
  tests.backend.test_sqlite_run_repository \
  tests.backend.test_local_review_audit_worker -v
```

Expected: FAIL because evidence ID snapshot/resolution methods and worker support do not exist.

- [ ] **Step 3: Implement minimal repository and worker support**

Add `list_evidence_block_ids(paper_id)` and `get_evidence_blocks_by_ids(paper_id, block_ids)`. Preserve requested order and raise `KeyError` if any ID is absent. In the worker, prefer inline `evidence_blocks` when present for backward compatibility; otherwise resolve `evidence_block_ids`.

- [ ] **Step 4: Run tests to verify GREEN**

Run the Task 1 command again.

Expected: PASS.

### Task 2: Create paper-scoped audit service

**Files:**
- Modify: `tests/backend/test_review_audit_service.py`
- Modify: `services/api/app/services/review_audit_service.py`

- [ ] **Step 1: Write failing service tests**

Assert paper-scoped audit creation snapshots evidence IDs, stores no evidence text in run input, enqueues only the job ID, rejects unknown papers, validates cross-paper weaknesses, and compensates queue delivery failure.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.backend.test_review_audit_service -v
```

Expected: FAIL because `create_from_paper_and_enqueue` does not exist.

- [ ] **Step 3: Implement shared creation/delivery path**

Add a paper-scoped service method accepting `paper_id`, weaknesses, `top_k`, and `finding_top_k`. Validate with `ReviewAuditRequest` using resolved blocks, then persist a compact payload with `evidence_block_ids`. Extract queue delivery compensation so both endpoint styles retain identical behavior.

- [ ] **Step 4: Run service tests to verify GREEN**

Run the Task 2 command again.

Expected: PASS.

### Task 3: Expose paper-scoped audit API

**Files:**
- Modify: `tests/api/test_fastapi_papers.py`
- Modify: `services/api/app/schemas/http.py`
- Modify: `services/api/app/api/routes/papers.py`

- [ ] **Step 1: Write failing API tests**

Assert `POST /api/papers/{paper_id}/review-audit` accepts weaknesses and ranking controls only, returns 202, rejects cross-paper weaknesses with 422, returns 404 for unknown papers, and never accepts or returns evidence text.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.api.test_fastapi_papers -v
```

Expected: FAIL because the route and request schema do not exist.

- [ ] **Step 3: Implement strict schema and route**

Add `PersistedPaperReviewAuditInput` with `extra="forbid"`, weaknesses, `top_k`, and `finding_top_k`. Route through `ReviewAuditService`; translate missing paper to 404, invalid request to 422, and queue failure to a redacted 503.

- [ ] **Step 4: Run API tests to verify GREEN**

Run the Task 3 command again.

Expected: PASS.

### Task 4: Verify the complete Phase 2D increment

**Files:**
- Create: `docs/progress/agent_rag_refactor_phase_2d_2026-06-06.md`
- Modify: `services/api/README.md`

- [ ] **Step 1: Run complete automated verification**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/api -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/backend -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest discover -s tests/evireview_core -v
EVIREVIEW_REDIS_INTEGRATION=1 EVIREVIEW_REDIS_URL=redis://localhost:6379/15 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.integration.test_redis_rq_enqueue -v
.venv/bin/python -m compileall -q packages/evireview_core services/api services/worker
.venv/bin/python -m pip check
git diff --check
```

Expected: all tests and checks pass.

- [ ] **Step 2: Restart API and worker, then run real HTTP verification**

Import a Markdown paper, create a paper-scoped audit without evidence text, wait for RQ success, and generate/read its report. Inspect SQLite run input to confirm it contains `evidence_block_ids` and no `evidence_blocks`.

- [ ] **Step 3: Run secret scan**

Run a repository scan for committed provider-key assignments and known credential fragments.

Expected: no matches.

- [ ] **Step 4: Update progress documentation, create a Lore commit, and push**

Document the compact reference contract, compatibility path, verification evidence, and remaining reproducibility risk when imported assets are replaced before a queued run executes.
