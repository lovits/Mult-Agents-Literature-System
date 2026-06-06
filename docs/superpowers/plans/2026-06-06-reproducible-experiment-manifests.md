# Reproducible Experiment Manifests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add experiment manifests that connect dataset versions, experiment-level configuration, immutable paper versions, audit runs, and generated reports.

**Architecture:** Persist lightweight experiment metadata and run membership in SQLite. Build manifest snapshots in a dedicated service by joining each run's immutable input/config with current lifecycle status and any generated reports; public responses exclude raw evidence, internal paths, queue tokens, and errors.

**Tech Stack:** Python 3.14, FastAPI, Pydantic, SQLite, existing EviReview services, `unittest`.

---

## Scope Boundaries

- Create, list, and read experiment manifests.
- Attach existing audit runs to a manifest.
- Snapshot dataset identity/version, experiment config, paper version, run config/status, and report metadata.
- Reject duplicate run membership and cross-dataset assumptions are left to the caller.
- Do not create batch runs, modify completed runs, add frontend, external models, or new dependencies.

## File Structure

- Modify `services/api/app/repositories/sqlite_run_repository.py`: manifest and membership persistence plus report lookup by run.
- Create `services/api/app/services/experiment_manifest_service.py`: public reproducibility snapshot assembly.
- Create `services/api/app/api/routes/experiments.py`: manifest HTTP endpoints.
- Modify `services/api/app/schemas/http.py`: strict manifest input schemas.
- Modify `services/api/app/main.py`: service/router wiring.
- Create focused tests under `tests/backend` and `tests/api`.

### Task 1: Persist experiment manifests and membership

**Files:**
- Modify: `tests/backend/test_sqlite_run_repository.py`
- Modify: `services/api/app/repositories/sqlite_run_repository.py`

- [ ] **Step 1: Write failing repository tests**

Assert manifest creation persists dataset name/version and config, run attachment preserves insertion order, duplicate attachment is idempotent, unknown runs are rejected, and reports can be listed by run.

- [ ] **Step 2: Run test to verify RED**

Run: `PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.backend.test_sqlite_run_repository -v`

Expected: FAIL because manifest persistence methods do not exist.

- [ ] **Step 3: Implement minimal tables and repository methods**

Add `experiment_manifests` and `experiment_manifest_runs`. Implement create/get/list/attach/list-run-IDs and `list_reports_for_run`.

- [ ] **Step 4: Run test to verify GREEN**

Run the Task 1 command again.

Expected: PASS.

### Task 2: Assemble public reproducibility snapshots

**Files:**
- Create: `tests/backend/test_experiment_manifest_service.py`
- Create: `services/api/app/services/experiment_manifest_service.py`

- [ ] **Step 1: Write failing service tests**

Assert a manifest snapshot includes dataset version, experiment config, run ID/status/config, paper ID/version, evidence source, and report metadata while excluding raw run input, evidence text, internal errors, and artifact paths.

- [ ] **Step 2: Run test to verify RED**

Run: `PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.backend.test_experiment_manifest_service -v`

Expected: FAIL because the service does not exist.

- [ ] **Step 3: Implement snapshot service**

Create manifests with generated IDs, attach runs, and assemble public entries from repository run/config/input/report data using an allowlist.

- [ ] **Step 4: Run test to verify GREEN**

Run the Task 2 command again.

Expected: PASS.

### Task 3: Expose experiment manifest APIs

**Files:**
- Create: `tests/api/test_fastapi_experiments.py`
- Modify: `services/api/app/schemas/http.py`
- Create: `services/api/app/api/routes/experiments.py`
- Modify: `services/api/app/main.py`
- Modify: `services/api/README.md`

- [ ] **Step 1: Write failing API tests**

Assert create/list/get/attach endpoints work, strict request validation rejects extra fields, missing manifest/run returns 404, and public responses do not expose raw inputs or artifact paths.

- [ ] **Step 2: Run test to verify RED**

Run: `PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.api.test_fastapi_experiments -v`

Expected: FAIL because routes and schemas do not exist.

- [ ] **Step 3: Implement schemas, routes, and app wiring**

Add strict manifest create input and attach-run route. Translate missing resources to 404 and duplicate membership to an idempotent success.

- [ ] **Step 4: Run test to verify GREEN**

Run the Task 3 command again.

Expected: PASS.

### Task 4: Verify Phase 2F

**Files:**
- Create: `docs/progress/agent_rag_refactor_phase_2f_2026-06-06.md`

- [ ] **Step 1: Run complete automated verification**

Run API, backend, core, and Redis/RQ integration tests, followed by compileall, pip check, diff check, and secret scan.

- [ ] **Step 2: Restart API and run real manifest verification**

Create a manifest for a named dataset version, attach the completed Phase 2E version-bound run, and verify the manifest snapshot includes its immutable paper version, run config/status, and report without raw evidence.

- [ ] **Step 3: Update progress documentation, create a Lore commit, and push**

Document manifest semantics, verification evidence, and the remaining absence of batch scheduling.
