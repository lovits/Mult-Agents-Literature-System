# Phase 3 Paper Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start formal Phase 3 by delivering a browser-usable three-column Paper Workspace over the existing version-bound review-audit backend.

**Architecture:** Add a dedicated public workspace read model that joins a run's weaknesses, selected immutable-version evidence, retrieval, verification, ranking, trace, and reports. Serve a dependency-free static frontend from FastAPI so Phase 3 starts without adding packages; keep the API contract suitable for a later Next.js client.

**Tech Stack:** Python 3.14, FastAPI/Starlette static files, SQLite, Redis/RQ, HTML, CSS, vanilla JavaScript, `unittest`, browser QA.

---

## Scope Boundaries

- Add paper listing, paper-run listing, and run workspace read APIs.
- Add a same-origin `/workspace/` application.
- Support empty, queued/running, failed, and succeeded runs.
- Show metric boundary prominently.
- Do not add dependencies, authentication, project CRUD, experiment dashboard, or Qdrant.

### Task 1: Lock Phase 3 API and static-hosting contracts

- [x] Write failing API tests for paper listing, paper-run listing, workspace read model, redaction, and `/workspace/`.
- [x] Run focused API tests and confirm RED.

### Task 2: Implement public workspace read model

- [x] Add repository/service methods for papers and paper runs.
- [x] Assemble a white-listed run workspace response with version-bound evidence.
- [x] Add routes and static frontend mount.
- [x] Run focused and complete backend tests until GREEN.

### Task 3: Implement the three-column Paper Workspace

- [x] Build stable paper/run navigation.
- [x] Build weakness/finding list, evidence viewer, verifier/ranker detail, trace, and report export.
- [x] Handle empty/loading/error states without layout shifts.
- [x] Verify desktop and mobile layouts in the browser.

### Task 4: Validate and document Phase 3

- [x] Run full automated verification and secret scan.
- [x] Complete the autoresearch architect-validation artifact.
- [x] Write Phase 3 progress documentation.
- [x] Create a Lore commit and push `main`.
