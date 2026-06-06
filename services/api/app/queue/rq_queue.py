from __future__ import annotations

from rq import Queue

from services.worker.rq_tasks.review_audit import execute_review_audit_job


class RQQueueAdapter:
    def __init__(self, queue: Queue, sqlite_path: str) -> None:
        self.queue = queue
        self.sqlite_path = sqlite_path

    def enqueue(self, job_id: str) -> str:
        delivery_id = f"rq-{job_id}"
        job = self.queue.enqueue(
            execute_review_audit_job,
            self.sqlite_path,
            job_id,
            job_id=delivery_id,
        )
        return str(job.id)
