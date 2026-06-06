from __future__ import annotations

from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import ReviewAuditRequest


class ReviewAuditService:
    def __init__(self, repository: SQLiteRunRepository) -> None:
        self.repository = repository

    def create_review_audit(self, request: ReviewAuditRequest) -> dict[str, dict]:
        run_id = f"run-{uuid4().hex}"
        job_id = f"job-{uuid4().hex}"
        self.repository.create_run_and_job(run_id, job_id, request.to_payload())
        return {
            "run": self.repository.get_run(run_id),
            "job": self.repository.get_job(job_id),
        }

    def get_run(self, run_id: str) -> dict:
        return self.repository.get_run(run_id)

    def get_findings(self, run_id: str) -> list[dict]:
        result = self.repository.get_run(run_id).get("result") or {}
        return list(result.get("ranked_findings", []))

    def get_trace(self, run_id: str) -> list[dict]:
        job = self.repository.get_job_for_run(run_id)
        return self.repository.list_events(job["job_id"])
