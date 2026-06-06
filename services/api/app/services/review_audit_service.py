from __future__ import annotations

from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.queue.base import JobQueue
from app.schemas.runs import ReviewAuditRequest


class QueueDeliveryError(RuntimeError):
    pass


class ReviewAuditService:
    def __init__(self, repository: SQLiteRunRepository, queue: JobQueue | None = None) -> None:
        self.repository = repository
        self.queue = queue

    def create_review_audit(self, request: ReviewAuditRequest) -> dict[str, dict]:
        run_id = f"run-{uuid4().hex}"
        job_id = f"job-{uuid4().hex}"
        self.repository.create_run_and_job(run_id, job_id, request.to_payload())
        return {
            "run": self._public_run(self.repository.get_run(run_id)),
            "job": self._public_job(self.repository.get_job(job_id)),
        }

    def create_and_enqueue(self, request: ReviewAuditRequest) -> dict:
        if self.queue is None:
            raise QueueDeliveryError("queue is not configured")
        created = self.create_review_audit(request)
        try:
            delivery_id = self.queue.enqueue(created["job"]["job_id"])
        except Exception as exc:
            self.repository.mark_delivery_failed(created["run"]["run_id"], created["job"]["job_id"], str(exc))
            raise QueueDeliveryError("queue delivery failed") from exc
        return {**created, "delivery_id": delivery_id}

    def get_run(self, run_id: str) -> dict:
        return self._public_run(self.repository.get_run(run_id))

    def get_job(self, job_id: str) -> dict:
        return self._public_job(self.repository.get_job(job_id))

    def get_findings(self, run_id: str) -> list[dict]:
        result = self.repository.get_run(run_id).get("result") or {}
        return list(result.get("ranked_findings", []))

    def get_trace(self, run_id: str) -> list[dict]:
        job = self.repository.get_job_for_run(run_id)
        return [self._public_event(event) for event in self.repository.list_events(job["job_id"])]

    @staticmethod
    def _public_run(run: dict) -> dict:
        hidden = {"config_json", "input_json", "result_json", "result"}
        public = {key: value for key, value in run.items() if key not in hidden}
        if public.get("error"):
            public["error"] = "internal_error"
        return public

    @staticmethod
    def _public_job(job: dict) -> dict:
        hidden = {"attempt_token", "lease_expires_at"}
        public = {key: value for key, value in job.items() if key not in hidden}
        if public.get("error"):
            public["error"] = "internal_error"
        return public

    @staticmethod
    def _public_event(event: dict) -> dict:
        payload = event.get("payload") or {}
        public_payload = {"progress": payload["progress"]} if "progress" in payload else {}
        return {
            "event_id": event["event_id"],
            "job_id": event["job_id"],
            "event_type": event["event_type"],
            "payload": public_payload,
            "created_at": event["created_at"],
        }
