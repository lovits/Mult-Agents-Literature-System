# Immutable Paper Asset Versions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make imported paper evidence immutable and bind paper-scoped review audits to the exact asset version active when the run is created.

**Architecture:** Preserve the existing mutable paper/section/evidence tables as the current-view compatibility layer, while adding immutable version metadata, versioned sections/evidence blocks, and an active-version pointer. Paper-scoped audits persist `paper_version_id`; workers resolve evidence from that immutable version so later re-imports cannot change or invalidate historical runs.

**Tech Stack:** Python 3.14, FastAPI, Pydantic, SQLite, Redis/RQ, existing `evireview_core`, `unittest`.

---

## Scope Boundaries

- Keep existing paper import, current paper read, inline audit, report, and queue APIs compatible.
- Create deterministic version IDs from paper identity, title, and Markdown content.
- Re-importing identical content reuses the same immutable version.
- Re-importing changed content creates a new version and changes only the active pointer/current-view tables.
- Bind new paper-scoped audits to an immutable `paper_version_id`.
- Do not migrate old Phase 2D runs retroactively, add frontend, external models, PDF ingestion, or new dependencies.

## File Structure

- Modify `services/api/app/repositories/sqlite_run_repository.py`: immutable version schema, active pointer, versioned asset writes/reads.
- Modify `services/api/app/services/paper_service.py`: deterministic version creation and version reads.
- Modify `services/api/app/services/review_audit_service.py`: persist active version ID in paper-scoped audit input.
- Modify `services/worker/tasks/review_audit.py`: resolve versioned evidence when `paper_version_id` exists.
- Modify `services/api/app/api/routes/papers.py`: version metadata and version evidence endpoints.
- Modify focused tests under `tests/backend` and `tests/api`.

### Task 1: Persist immutable paper versions

**Files:**
- Modify: `tests/backend/test_paper_service.py`
- Modify: `tests/backend/test_sqlite_run_repository.py`
- Modify: `services/api/app/repositories/sqlite_run_repository.py`
- Modify: `services/api/app/services/paper_service.py`

- [ ] **Step 1: Write failing version persistence tests**

Assert first import creates one active version, identical re-import reuses it, changed re-import creates a second version, current-view assets change, and the first version's evidence remains readable and unchanged.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest \
  tests.backend.test_paper_service \
  tests.backend.test_sqlite_run_repository -v
```

Expected: FAIL because version metadata and immutable asset methods do not exist.

- [ ] **Step 3: Implement immutable version schema and import path**

Add `paper_versions`, `paper_active_versions`, `paper_version_sections`, and `paper_version_evidence_blocks`. Extend `replace_paper_assets` to atomically insert immutable assets with `INSERT OR IGNORE`, update the active pointer, and replace current-view assets. Generate deterministic `version_id` in `PaperService`.

- [ ] **Step 4: Run tests to verify GREEN**

Run the Task 1 command again.

Expected: PASS.

### Task 2: Bind audits and workers to immutable versions

**Files:**
- Modify: `tests/backend/test_review_audit_service.py`
- Modify: `tests/backend/test_local_review_audit_worker.py`
- Modify: `services/api/app/services/review_audit_service.py`
- Modify: `services/worker/tasks/review_audit.py`

- [ ] **Step 1: Write failing audit-version tests**

Assert paper-scoped audit input stores the active `paper_version_id`. Create a queued audit, re-import changed paper content before worker execution, then assert the worker succeeds using the original version evidence.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest \
  tests.backend.test_review_audit_service \
  tests.backend.test_local_review_audit_worker -v
```

Expected: FAIL because audits and workers do not use immutable versions.

- [ ] **Step 3: Implement version-bound audit execution**

Store `paper_version_id` in paper-scoped run input. Resolve `evidence_block_ids` from `paper_version_evidence_blocks` when the version ID exists; retain Phase 2D and inline fallbacks for old runs.

- [ ] **Step 4: Run tests to verify GREEN**

Run the Task 2 command again.

Expected: PASS.

### Task 3: Expose version inspection APIs

**Files:**
- Modify: `tests/api/test_fastapi_papers.py`
- Modify: `services/api/app/api/routes/papers.py`
- Modify: `services/api/README.md`

- [ ] **Step 1: Write failing API tests**

Assert current paper metadata includes `active_version_id`; `GET /api/papers/{paper_id}/versions` lists immutable versions; and `GET /api/papers/{paper_id}/versions/{version_id}/evidence-blocks` reads historical evidence without internal ordinals.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.api.test_fastapi_papers -v
```

Expected: FAIL because version inspection routes do not exist.

- [ ] **Step 3: Implement version inspection routes**

Route reads through `PaperService`. Return 404 for missing paper or version and never expose mutable-table ordinals.

- [ ] **Step 4: Run tests to verify GREEN**

Run the Task 3 command again.

Expected: PASS.

### Task 4: Verify the complete Phase 2E increment

**Files:**
- Create: `docs/progress/agent_rag_refactor_phase_2e_2026-06-06.md`

- [ ] **Step 1: Run complete automated verification**

Run API, backend, core, and explicit Redis/RQ integration tests, followed by compileall, pip check, diff check, and secret scan.

- [ ] **Step 2: Restart API and worker, then run real version-drift verification**

Import version A, create a paper-scoped queued audit while the worker is stopped, import version B, restart the worker, and verify the run succeeds with version A. Read both historical version evidence endpoints and confirm they differ.

- [ ] **Step 3: Update progress documentation, create a Lore commit, and push**

Document immutable version semantics, compatibility behavior, verification evidence, and remaining storage-retention risks.
