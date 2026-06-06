# Phase 2H Unified Metrics Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one reproducible metrics aggregation and export path for backend experiment manifests and historical experiment JSON artifacts.

**Architecture:** Add a dependency-free metric record and deterministic JSON/CSV/Markdown renderers to `evireview_core.evaluation`. Keep artifact-specific parsing in an experiment adapter registry, and add manifest-run aggregation to `ExperimentManifestService` plus a public API endpoint. A CLI composes both sources and writes thesis-ready outputs without modifying source metrics.

**Tech Stack:** Python standard library, dataclasses, JSON, CSV, Markdown, FastAPI, SQLite, unittest.

---

## File Structure

Create:

- `packages/evireview_core/evireview_core/evaluation/__init__.py`
- `packages/evireview_core/evireview_core/evaluation/metrics.py`
- `packages/evireview_core/evireview_core/evaluation/export.py`
- `tests/evireview_core/test_metric_export.py`
- `code/experiments/evireview_a/src/metric_adapter_registry.py`
- `code/experiments/evireview_a/src/export_unified_metrics.py`
- `tests/experiments/test_metric_adapter_registry.py`
- `docs/progress/agent_rag_refactor_phase_2h_2026-06-07.md`

Modify:

- `services/api/app/services/experiment_manifest_service.py`
- `services/api/app/api/routes/experiments.py`
- `tests/backend/test_experiment_manifest_service.py`
- `tests/api/test_fastapi_experiments.py`
- `docs/design/agent_rag_frontend_backend_refactor_architecture_2026-06-02.md`

## Task 1: Stable Metric Contract And Exporters

- [ ] Write failing tests proving a metric record requires dataset/task/method/metric/value/boundary/source artifact and deterministic exporters preserve those fields.
- [ ] Run `PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_metric_export -v` and confirm RED.
- [ ] Implement `MetricRecord`, boundary validation, stable sorting, and JSON/CSV/Markdown renderers.
- [ ] Re-run the focused test and confirm GREEN.

## Task 2: Historical Artifact Adapter Registry

- [ ] Write failing tests using temporary PeerQA-XT and reviewer coverage JSON artifacts.
- [ ] Confirm RED because the registry does not exist.
- [ ] Implement explicit adapters plus recursive numeric metric extraction.
- [ ] Require every adapter to assign dataset, task, module, method, boundary, and source artifact.
- [ ] Cover current retrieval, verifier, ranker, generation, and auxiliary classification metrics artifacts.
- [ ] Confirm focused adapter tests pass.

## Task 3: Manifest Run Aggregation And API

- [ ] Write failing backend tests for run status, verification support, and ranked-finding metrics.
- [ ] Write failing API test for `GET /api/experiments/{manifest_id}/metrics`.
- [ ] Implement manifest aggregation using the shared metric contract.
- [ ] Add the public endpoint; do not expose inputs, evidence text, internal paths, or errors.
- [ ] Confirm backend and API focused tests pass.

## Task 4: Unified CLI And Thesis Outputs

- [ ] Implement `export_unified_metrics.py` to combine historical adapters and optional SQLite manifests.
- [ ] Write:
  - `code/experiments/evireview_a/data/unified_metrics.json`
  - `code/experiments/evireview_a/data/unified_metrics.csv`
  - `code/experiments/evireview_a/reports/unified_metrics.md`
- [ ] Verify all records include metric boundary and source artifact.
- [ ] Update Phase 2H progress and architecture documents.

## Task 5: Verification And Handoff To Phase 2H-B

- [ ] Run core, backend, API, and Redis/RQ integration tests.
- [ ] Run `compileall`, `git diff --check`, and secret scan.
- [ ] Create `.omx/specs/autoresearch-phase2h-experiment-optimization/` mission, sandbox, and validator result seed for Phase 2H-B.
- [ ] Commit and push Phase 2H-A before starting experiment optimization.

