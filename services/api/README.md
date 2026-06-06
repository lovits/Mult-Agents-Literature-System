# EviReview API Application Layer

This directory contains the Phase 2A application layer and Phase 2B FastAPI adapter.

Implemented boundaries:

- `app.schemas.runs`: review-audit input and lifecycle contracts.
- `app.repositories.sqlite_run_repository`: local SQLite dev-mode persistence for runs, jobs, results, and trace events.
- `app.services.review_audit_service`: application use cases suitable for future FastAPI route handlers.
- `app.main:create_app`: FastAPI application factory.
- `app.queue.rq_queue`: Redis/RQ delivery adapter.

The API never accepts or stores provider API keys. Raw weakness/evidence inputs are persisted in SQLite for worker use and are not returned by run endpoints. The current workflow executes only the deterministic `silver diagnostic` core pipeline.

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
