# FastAPI and RQ Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add real HTTP and Redis/RQ adapters around the completed review-audit application/service layer without implementing the frontend or duplicating core workflow logic.

**Architecture:** FastAPI routes validate HTTP payloads and call `ReviewAuditService`; a queue adapter enqueues only the persisted `job_id`; the RQ task reopens SQLite and executes the existing local worker. SQLite remains the source of truth for run/job lifecycle and trace, while Redis/RQ is only the delivery mechanism.

**Tech Stack:** FastAPI, Pydantic, Uvicorn, HTTPX/TestClient, redis-py, RQ, SQLite, existing `evireview_core`.

---

## Scope

Included:

- Dependency manifests for API and worker.
- FastAPI app factory, settings, dependencies, health route, review-audit run/job routes.
- Pydantic HTTP schemas that map to existing domain/application schemas.
- RQ enqueue adapter and RQ task entrypoint.
- Unit/API tests and a local Redis integration test.
- Run instructions and progress documentation.

Excluded:

- Frontend.
- PostgreSQL/SQLAlchemy/Alembic.
- SSE streaming; ordered trace polling is the Phase 2B fallback.
- GLM/provider execution.
- Qdrant.

## Tasks

### Task 1: Dependencies and Settings

- Create `services/api/requirements.txt` and `services/worker/requirements.txt`.
- Create environment-backed settings for SQLite path, Redis URL, and queue name.
- Test defaults and environment overrides.

### Task 2: FastAPI Schemas and App

- Create Pydantic request/response schemas.
- Create app factory and dependency wiring.
- Add `GET /health`.
- Add `POST /api/runs/review-audit`, `GET /api/runs/{run_id}`, trace/findings routes, and `GET /api/jobs/{job_id}`.
- Convert missing resources to HTTP 404 and validation failures to HTTP 422.

### Task 3: Queue Adapter and RQ Task

- Create queue protocol plus RQ implementation.
- Enqueue only persisted `job_id`; never serialize raw paper/evidence payloads into Redis.
- Create RQ task that reopens the configured SQLite repository and executes one matching queued job.
- Keep an inline queue adapter for deterministic API tests and Redis-unavailable local fallback.

### Task 4: Verification and Documentation

- Run API/backend/core tests.
- Start local Redis and run RQ enqueue integration test.
- Run compileall, diff check, and secret scan.
- Confirm no frontend or experiment data/report changes.
- Commit and push.

## Inputs Needed

No additional user input is required. Dependency approval was provided on 2026-06-06.
