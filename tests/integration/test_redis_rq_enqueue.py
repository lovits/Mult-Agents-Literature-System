from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from redis import Redis
from rq import Queue, SimpleWorker

from app.queue.rq_queue import RQQueueAdapter
from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import ReviewAuditRequest
from app.services.review_audit_service import ReviewAuditService


@unittest.skipUnless(os.getenv("EVIREVIEW_REDIS_INTEGRATION") == "1", "requires local Redis integration opt-in")
class RedisRqEnqueueIntegrationTest(unittest.TestCase):
    def test_rq_adapter_enqueues_and_worker_executes_persisted_job(self) -> None:
        connection = Redis.from_url(os.environ["EVIREVIEW_REDIS_URL"])
        connection.flushdb()
        queue = Queue("evireview-integration", connection=connection)
        with tempfile.TemporaryDirectory() as tmp:
            sqlite_path = Path(tmp) / "backend.sqlite3"
            repository = SQLiteRunRepository(sqlite_path)
            repository.initialize()
            service = ReviewAuditService(repository)
            created = service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
            adapter = RQQueueAdapter(queue, str(sqlite_path))

            delivery_id = adapter.enqueue(created["job"]["job_id"])
            SimpleWorker([queue], connection=connection).work(burst=True)

            self.assertEqual(delivery_id, f"rq-{created['job']['job_id']}")
            self.assertEqual(service.get_run(created["run"]["run_id"])["status"], "succeeded")
        self.assertEqual(queue.count, 0)
        connection.flushdb()


if __name__ == "__main__":
    unittest.main()
