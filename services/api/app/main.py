from __future__ import annotations

from fastapi import FastAPI
from redis import Redis
from rq import Queue

from app.api.routes.runs import router as runs_router
from app.core.config import Settings
from app.queue.base import JobQueue
from app.queue.rq_queue import RQQueueAdapter
from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.services.review_audit_service import ReviewAuditService


def create_app(settings: Settings | None = None, queue: JobQueue | None = None) -> FastAPI:
    resolved = settings or Settings.from_env()
    repository = SQLiteRunRepository(resolved.sqlite_path)
    repository.initialize()
    resolved_queue = queue or RQQueueAdapter(
        Queue(resolved.queue_name, connection=Redis.from_url(resolved.redis_url)),
        str(resolved.sqlite_path),
    )

    app = FastAPI(title="EviReview API", version="0.1.0")
    app.state.settings = resolved
    app.state.repository = repository
    app.state.service = ReviewAuditService(repository, resolved_queue)
    app.state.queue = resolved_queue

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(runs_router, prefix="/api")
    return app
