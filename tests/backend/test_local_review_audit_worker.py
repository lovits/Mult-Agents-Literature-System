from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import ReviewAuditRequest
from app.services.review_audit_service import ReviewAuditService
from evireview_core.domain.models import EvidenceBlock, Weakness
from services.worker.tasks.review_audit import recover_and_run, run_next_job


class LocalReviewAuditWorkerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.service = ReviewAuditService(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_worker_executes_queued_review_audit(self) -> None:
        created = self.service.create_review_audit(
            ReviewAuditRequest(
                paper_id="p1",
                weaknesses=[Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major")],
                evidence_blocks=[
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper has limited ablation baselines.")
                ],
            )
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "succeeded")
        self.assertEqual(len(self.service.get_findings(created["run"]["run_id"])), 1)

    def test_worker_records_invalid_input_failure(self) -> None:
        self.repository.create_run_and_job(
            "run-bad",
            "job-bad",
            {"paper_id": "p1", "weaknesses": [{"paper_id": "p1"}], "evidence_blocks": [], "top_k": 5, "finding_top_k": 3},
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "failed")
        self.assertIn("weakness_id", self.repository.get_run("run-bad")["error"])

    def test_worker_recovers_running_job_before_execution(self) -> None:
        created = self.service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        self.repository.claim_next_job(lease_seconds=-1)

        results = recover_and_run(self.repository)

        self.assertEqual(results[0]["status"], "succeeded")
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "succeeded")

    def test_worker_does_not_recover_active_running_job(self) -> None:
        created = self.service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        self.repository.claim_next_job()

        results = recover_and_run(self.repository)

        self.assertEqual(results, [])
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "running")


if __name__ == "__main__":
    unittest.main()
