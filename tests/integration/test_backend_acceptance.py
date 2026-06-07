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
from evireview_core.domain.models import Weakness


@unittest.skipUnless(
    os.getenv("EVIREVIEW_QDRANT_INTEGRATION") == "1" and os.getenv("EVIREVIEW_REDIS_INTEGRATION") == "1",
    "requires local Redis and Qdrant",
)
class BackendAcceptanceTest(unittest.TestCase):
    def test_mineru_asset_runs_through_rq_qdrant_audit_and_report(self) -> None:
        connection = Redis.from_url(os.environ["EVIREVIEW_REDIS_URL"])
        connection.flushdb()
        queue = Queue("evireview-backend-acceptance", connection=connection)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sqlite_path = root / "acceptance.sqlite3"
            repository = SQLiteRunRepository(sqlite_path)
            repository.initialize()
            paper_service = PaperService(repository)
            imported = paper_service.import_mineru_markdown(
                "acceptance-paper",
                "Acceptance Paper",
                "---\nsource: MinerU\npdf: acceptance.pdf\n---\n\n# Experiments\nThe evaluation reports no ablation study.",
                "acceptance.pdf",
            )
            audit_service = ReviewAuditService(repository, RQQueueAdapter(queue, str(sqlite_path)))
            created = audit_service.create_from_paper_and_enqueue(
                "acceptance-paper",
                [Weakness("w1", "acceptance-paper", "The evaluation lacks an ablation study.", "experiment", "major")],
                retriever="qdrant_sparse",
                finding_top_k=1,
            )

            SimpleWorker([queue], connection=connection).work(burst=True)
            run = repository.get_run(created["run"]["run_id"])
            report_service = ReportService(repository, root / "reports")
            report = report_service.create_for_run(run["run_id"])
            markdown = report_service.get_markdown(report["report_id"])

        self.assertEqual(imported["source_type"], "mineru_markdown")
        self.assertEqual(run["status"], "succeeded")
        self.assertEqual(run["result"]["retrieval"]["w1"][0]["retriever"], "qdrant_sparse")
        self.assertEqual(
            [item["node"] for item in run["result"]["agent_trace"]][-4:],
            ["verify_weaknesses", "deduplicate_weaknesses", "rank_findings", "classify_auxiliary_decision"],
        )
        self.assertTrue(run["result"]["auxiliary_decision"]["not_for_decision"])
        self.assertIn("Auxiliary Decision Signal", markdown)
        self.assertIn("do not use as an automated paper decision", markdown)
        self.assertEqual(queue.count, 0)
        connection.flushdb()


if __name__ == "__main__":
    unittest.main()
