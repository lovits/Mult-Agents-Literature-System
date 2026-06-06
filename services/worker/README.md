# EviReview Local Worker

The local worker executes persisted review-audit jobs without Redis or RQ.

Current behavior:

- Recovers stale `running` jobs to `queued` after a local restart.
- Claims one queued job at a time.
- Issues a unique attempt token for every claim so a late worker cannot overwrite a reclaimed job.
- Rehydrates weaknesses and evidence blocks from SQLite.
- Calls `evireview_core.workflow.run_deterministic_review_audit`.
- Persists results or failure context and trace events.

The worker does not call hosted providers and does not read or store API keys.

Import the local worker with:

```python
from services.worker.tasks.review_audit import recover_and_run, run_next_job
```

Phase 2B wraps the same task function with RQ while preserving SQLite as the lifecycle source of truth.

The local worker currently uses a fixed five-minute lease and does not renew leases with a heartbeat. Increase or renew the lease before using it for workflows that can exceed five minutes.

Run the RQ worker:

```bash
redis-server
PYTHONPATH=packages/evireview_core:services/api:. .venv/bin/rq worker evireview --url redis://localhost:6379/0
```

RQ receives only the SQLite path and persisted `job_id`; raw weakness/evidence payloads are not copied into Redis.
