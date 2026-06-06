from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evireview_core.domain.models import EvidenceBlock, Weakness


class ReviewAuditSchemaTest(unittest.TestCase):
    def test_request_rejects_cross_paper_inputs(self) -> None:
        from app.schemas.runs import ReviewAuditRequest

        with self.assertRaisesRegex(ValueError, "same paper"):
            ReviewAuditRequest(
                paper_id="p1",
                weaknesses=[Weakness("w1", "p2", "Missing ablation.", "experiment")],
                evidence_blocks=[EvidenceBlock("b1", "p1", "Experiments", "experiment", "Ablation results.")],
            )

    def test_request_rejects_non_positive_top_k(self) -> None:
        from app.schemas.runs import ReviewAuditRequest

        with self.assertRaisesRegex(ValueError, "top_k"):
            ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[], top_k=0)


class ReviewAuditServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.repositories.sqlite_run_repository import SQLiteRunRepository
        from app.services.review_audit_service import ReviewAuditService

        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.service = ReviewAuditService(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_review_audit_queues_run_and_job(self) -> None:
        from app.schemas.runs import ReviewAuditRequest

        request = ReviewAuditRequest(
            paper_id="p1",
            weaknesses=[Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")],
            evidence_blocks=[EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper reports no ablation.")],
            top_k=2,
            finding_top_k=1,
        )

        created = self.service.create_review_audit(request)

        self.assertEqual(created["run"]["status"], "queued")
        self.assertEqual(created["job"]["status"], "queued")
        self.assertEqual(created["run"]["paper_id"], "p1")

    def test_service_reads_findings_and_trace(self) -> None:
        from app.schemas.runs import ReviewAuditRequest

        created = self.service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        run_id = created["run"]["run_id"]
        job_id = created["job"]["job_id"]
        claimed = self.repository.claim_next_job()
        self.repository.save_result(
            run_id,
            job_id,
            claimed["attempt_token"],
            {"ranked_findings": [{"weakness_id": "w1"}]},
        )

        self.assertEqual(self.service.get_findings(run_id), [{"weakness_id": "w1"}])
        self.assertEqual([event["event_type"] for event in self.service.get_trace(run_id)], ["queued", "running", "succeeded"])


if __name__ == "__main__":
    unittest.main()
