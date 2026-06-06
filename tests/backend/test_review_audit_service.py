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

    def test_service_compensates_enqueue_failure(self) -> None:
        class FailingQueue:
            def enqueue(self, job_id: str) -> str:
                raise ConnectionError("redis unavailable")

        from app.schemas.runs import ReviewAuditRequest
        from app.services.review_audit_service import QueueDeliveryError, ReviewAuditService

        service = ReviewAuditService(self.repository, FailingQueue())

        with self.assertRaises(QueueDeliveryError):
            service.create_and_enqueue(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))

        job = self.repository.get_job_for_run(self.repository.list_runs()[0]["run_id"])
        self.assertEqual(job["status"], "failed")

    def test_create_from_paper_snapshots_ids_without_evidence_text(self) -> None:
        class RecordingQueue:
            def __init__(self) -> None:
                self.job_ids: list[str] = []

            def enqueue(self, job_id: str) -> str:
                self.job_ids.append(job_id)
                return f"delivery-{job_id}"

        from app.services.review_audit_service import ReviewAuditService

        self.repository.replace_paper_assets(
            "p1",
            "Paper",
            [],
            [
                {
                    "block_id": "b1",
                    "paper_id": "p1",
                    "ordinal": 0,
                    "section_path": "Experiments",
                    "section_type": "experiment",
                    "text": "Sensitive evidence text.",
                    "score": 0.0,
                }
            ],
            version_id="version-1",
        )
        queue = RecordingQueue()
        service = ReviewAuditService(self.repository, queue)

        created = service.create_from_paper_and_enqueue(
            "p1",
            [Weakness("w1", "p1", "Missing ablation.", "experiment")],
            top_k=2,
            finding_top_k=1,
        )

        stored = self.repository.load_input(created["run"]["run_id"])
        self.assertEqual(stored["evidence_block_ids"], ["b1"])
        self.assertEqual(stored["paper_version_id"], "version-1")
        self.assertNotIn("evidence_blocks", stored)
        self.assertNotIn("Sensitive evidence text", str(stored))
        self.assertEqual(queue.job_ids, [created["job"]["job_id"]])

    def test_create_from_paper_rejects_missing_paper_and_cross_paper_weakness(self) -> None:
        class RecordingQueue:
            def enqueue(self, job_id: str) -> str:
                return f"delivery-{job_id}"

        from app.services.review_audit_service import ReviewAuditService

        service = ReviewAuditService(self.repository, RecordingQueue())

        with self.assertRaises(KeyError):
            service.create_from_paper_and_enqueue("missing", [])

        self.repository.replace_paper_assets("p1", "Paper", [], [])
        with self.assertRaisesRegex(ValueError, "same paper"):
            service.create_from_paper_and_enqueue(
                "p1",
                [Weakness("w1", "p2", "Missing.", "other")],
            )

    def test_missing_queue_does_not_persist_orphaned_run(self) -> None:
        from app.schemas.runs import ReviewAuditRequest
        from app.services.review_audit_service import QueueDeliveryError

        self.repository.replace_paper_assets("p1", "Paper", [], [])

        with self.assertRaises(QueueDeliveryError):
            self.service.create_and_enqueue(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        with self.assertRaises(QueueDeliveryError):
            self.service.create_from_paper_and_enqueue("p1", [])

        self.assertEqual(self.repository.list_runs(), [])


if __name__ == "__main__":
    unittest.main()
