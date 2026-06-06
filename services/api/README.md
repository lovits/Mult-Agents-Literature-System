# EviReview API Application Layer

This directory currently contains the dependency-free Phase 2A backend application layer. It is not an HTTP server yet.

Implemented boundaries:

- `app.schemas.runs`: review-audit input and lifecycle contracts.
- `app.repositories.sqlite_run_repository`: local SQLite dev-mode persistence for runs, jobs, results, and trace events.
- `app.services.review_audit_service`: application use cases suitable for future FastAPI route handlers.

The application layer never accepts or stores provider API keys. The current workflow executes only the deterministic `silver diagnostic` core pipeline.

Run backend tests from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/evireview_core:services/api:. python3 -m unittest discover -s tests/backend -v
```

Phase 2B will add FastAPI request/response adapters only after dependency approval. HTTP handlers must call the service layer rather than repository or core functions directly.
