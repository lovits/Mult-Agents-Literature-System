from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository


class ReportServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.services.report_service import ReportService

        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.repository = SQLiteRunRepository(root / "backend.sqlite3")
        self.repository.initialize()
        self.service = ReportService(self.repository, root / "reports")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _succeed_run(self) -> str:
        self.repository.create_run_and_job(
            "run-1",
            "job-1",
            {"paper_id": "paper-1", "weaknesses": [], "evidence_blocks": [], "top_k": 5, "finding_top_k": 3},
        )
        claimed = self.repository.claim_job("job-1")
        self.repository.save_result(
            "run-1",
            "job-1",
            claimed["attempt_token"],
            {
                "metric_boundary": "silver diagnostic",
                "weakness_count": 0,
                "evidence_block_count": 0,
                "ranked_findings": [],
                "verification": {},
            },
        )
        return "run-1"

    def test_create_report_for_succeeded_run_persists_metadata_and_markdown(self) -> None:
        report = self.service.create_for_run(self._succeed_run())

        self.assertEqual(report["run_id"], "run-1")
        self.assertEqual(report["metric_boundary"], "silver diagnostic")
        self.assertNotIn("artifact_path", report)
        self.assertIn("# Review Audit Report", self.service.get_markdown(report["report_id"]))
        self.assertEqual(self.service.get_report(report["report_id"])["report_id"], report["report_id"])

    def test_incomplete_run_is_rejected(self) -> None:
        self.repository.create_run_and_job(
            "run-queued",
            "job-queued",
            {"paper_id": "paper-1", "weaknesses": [], "evidence_blocks": [], "top_k": 5, "finding_top_k": 3},
        )

        with self.assertRaisesRegex(RuntimeError, "succeeded"):
            self.service.create_for_run("run-queued")


if __name__ == "__main__":
    unittest.main()
