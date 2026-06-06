# Batch Experiment Scheduling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Schedule bounded batches of immutable-version paper review audits directly from an experiment manifest.

**Architecture:** Extend the existing experiment service as the orchestration boundary between manifests and the review-audit service. Each batch item resolves the paper's active immutable version through the existing audit path, creates one queued run, and attaches every created run to the manifest; item-level failures use stable public error codes and do not roll back successful items.

**Tech Stack:** Python 3.14, FastAPI, Pydantic, SQLite, existing Redis/RQ adapter, `unittest`.

---

## Scope Boundaries

- Add one manifest-scoped batch scheduling endpoint.
- Accept 1 to 100 paper audit items per request.
- Bind each scheduled item to the paper version active at creation time.
- Preserve partial success and return ordered per-item results.
- Attach queue-delivery-failed runs when a run was already persisted.
- Do not accept raw evidence text, provider credentials, dataset file paths, or external model configuration.
- Do not add frontend, metrics aggregation, exports, or new dependencies.

## File Structure

- Modify `tests/api/test_fastapi_experiments.py`: lock batch API behavior, validation, version binding, and redaction.
- Modify `tests/backend/test_experiment_manifest_service.py`: lock orchestration and failed-run membership behavior.
- Modify `services/api/app/schemas/http.py`: add strict bounded batch request schemas.
- Modify `services/api/app/services/review_audit_service.py`: preserve the run ID on queue-delivery failures.
- Modify `services/api/app/services/experiment_manifest_service.py`: orchestrate partial-success scheduling and manifest attachment.
- Modify `services/api/app/api/routes/experiments.py`: expose the batch endpoint and map missing manifests.
- Modify `services/api/app/main.py`: inject the review-audit service into the experiment service.
- Create `docs/progress/agent_rag_refactor_phase_2g_2026-06-06.md`: record delivered behavior and verification.

### Task 1: Lock the batch HTTP contract

- [x] Write API tests for all-success scheduling, mixed missing-paper/success scheduling, immutable paper-version snapshots, raw-evidence exclusion, stable queue failure errors, and the 100-item bound.
- [x] Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/python -m unittest tests.api.test_fastapi_experiments -v`.
- [x] Confirm RED because the batch schema and endpoint do not exist.

### Task 2: Implement minimal scheduling orchestration

- [x] Add strict batch schemas with `extra="forbid"` and `min_length=1, max_length=100`.
- [x] Preserve `run_id` on queue-delivery errors without exposing internal queue messages.
- [x] Add ordered partial-success scheduling to `ExperimentManifestService`.
- [x] Add the manifest-scoped endpoint and dependency wiring.
- [x] Re-run the focused API and backend tests until GREEN.

### Task 3: Verify and document Phase 2G

- [x] Run all API, backend, core, and Redis/RQ integration tests.
- [x] Run compileall, dependency, diff, and secret checks.
- [x] Exercise the live endpoint against the local API and verify version-bound manifest membership.
- [x] Write the Phase 2G progress document.
- [x] Create a Lore-protocol commit and push `main`.
