from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from redis import Redis
from rq import Queue, SimpleWorker

from app.queue.rq_queue import RQQueueAdapter
from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.services.paper_service import PaperService
from app.services.report_service import ReportService
from app.services.review_audit_service import ReviewAuditService


@unittest.skipUnless(
    os.getenv("EVIREVIEW_MINIMAX_INTEGRATION") == "1"
    and os.getenv("MINIMAX_API_KEY")
    and os.getenv("EVIREVIEW_QDRANT_INTEGRATION") == "1"
    and os.getenv("EVIREVIEW_REDIS_INTEGRATION") == "1",
    "requires MiniMax key, Redis, and Qdrant",
)
class MiniMaxBackendAcceptanceTest(unittest.TestCase):
    def test_hosted_generation_and_verification_complete_full_backend_chain(self) -> None:
        connection = Redis.from_url(os.environ["EVIREVIEW_REDIS_URL"])
        connection.flushdb()
        queue = Queue("evireview-minimax-acceptance", connection=connection)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sqlite_path = root / "minimax-acceptance.sqlite3"
            repository = SQLiteRunRepository(sqlite_path)
            repository.initialize()
            PaperService(repository).import_markdown(
                "minimax-acceptance-paper",
                "MiniMax Acceptance Paper",
                (
                    "# Method\nThe system uses a retrieval planner and evidence verifier.\n\n"
                    "# Experiments\nThe evaluation compares BM25 and dense retrieval on one dataset. "
                    "No ablation study or robustness analysis is reported.\n\n"
                    "# Limitations\nThe study is limited to a small evaluation corpus."
                ),
            )
            service = ReviewAuditService(repository, RQQueueAdapter(queue, str(sqlite_path)))
            created = service.create_from_paper_and_enqueue(
                "minimax-acceptance-paper",
                [],
                retriever="qdrant_sparse",
                weakness_generator="minimax",
                verifier="minimax",
                finding_top_k=3,
            )

            SimpleWorker([queue], connection=connection).work(burst=True)
            run = repository.get_run(created["run"]["run_id"])
            report_service = ReportService(repository, root / "reports")
            report = report_service.create_for_run(run["run_id"])
            markdown = report_service.get_markdown(report["report_id"])

        self.assertEqual(run["status"], "succeeded")
        self.assertEqual(run["result"]["weakness_generator"], "minimax")
        self.assertEqual(run["result"]["verifier"], "minimax")
        self.assertGreater(len(run["result"]["weaknesses"]), 0)
        self.assertTrue(all(item["verifier"] == "minimax_evidence_judge" for item in run["result"]["verification"].values()))
        self.assertIn("Auxiliary Decision Signal", markdown)
        self.assertEqual(queue.count, 0)
        connection.flushdb()


if __name__ == "__main__":
    unittest.main()
