from __future__ import annotations

from pathlib import Path
from typing import Any

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from services.worker.tasks.review_audit import run_job


def execute_review_audit_job(sqlite_path: str, job_id: str) -> dict[str, Any]:
    repository = SQLiteRunRepository(Path(sqlite_path))
    repository.initialize()
    result = run_job(repository, job_id)
    if result is None:
        raise RuntimeError(f"queued job not found: {job_id}")
    return result
