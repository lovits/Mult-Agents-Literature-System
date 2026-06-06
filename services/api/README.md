# EviReview API Application Layer

This directory contains the Phase 2A application layer, Phase 2B FastAPI/RQ adapter, and Phase 2C backend paper/report assets.

Implemented boundaries:

- `app.schemas.runs`: review-audit input and lifecycle contracts.
- `app.repositories.sqlite_run_repository`: local SQLite dev-mode persistence for runs, jobs, results, and trace events.
- `app.services.review_audit_service`: application use cases suitable for future FastAPI route handlers.
- `app.services.paper_service`: Markdown paper parsing and persisted evidence-block construction.
- `app.services.report_service`: persisted Markdown report generation for completed review audits.
- `app.main:create_app`: FastAPI application factory.
- `app.queue.rq_queue`: Redis/RQ delivery adapter.

The API never accepts or stores provider API keys. Raw weakness/evidence inputs are persisted in SQLite for worker use and are not returned by run endpoints. The current workflow executes only the deterministic `silver diagnostic` core pipeline.

Phase 2C routes:

- `POST /api/papers/import`
- `POST /api/papers/{paper_id}/review-audit`
- `GET /api/papers/{paper_id}`
- `GET /api/papers/{paper_id}/sections`
- `GET /api/papers/{paper_id}/evidence-blocks`
- `POST /api/runs/{run_id}/report`
- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/markdown`

The paper-scoped review-audit endpoint snapshots ordered evidence-block IDs into the run input. It does not require the client to send evidence text, and the worker fails explicitly if any snapshotted evidence block is no longer available.

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
