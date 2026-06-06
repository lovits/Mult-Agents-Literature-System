from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import PersistedPaperReviewAuditRequest
from app.services.review_audit_service import ReviewAuditService


class ExperimentManifestServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.services.experiment_manifest_service import ExperimentManifestService

        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.service = ExperimentManifestService(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_snapshot_connects_dataset_paper_version_run_config_and_report_without_raw_input(self) -> None:
        self.repository.create_run_and_job(
            "run-1",
            "job-1",
            {
                "paper_id": "p1",
                "paper_version_id": "version-1",
                "evidence_source": "persisted_paper_version",
                "evidence_block_ids": ["b1"],
                "weaknesses": [{"weakness_text": "sensitive weakness text"}],
                "top_k": 5,
                "finding_top_k": 3,
            },
        )
        claimed = self.repository.claim_job("job-1")
        self.repository.save_result("run-1", "job-1", claimed["attempt_token"], {"ranked_findings": []})
        self.repository.create_report("report-1", "run-1", "p1", "silver diagnostic", "/internal/report.md")
        manifest = self.service.create("PeerQA Retrieval", "PeerQA-XT", "500-v1", {"retriever": "hierarchical"})
        self.service.attach_run(manifest["manifest_id"], "run-1")

        snapshot = self.service.get(manifest["manifest_id"])
        entry = snapshot["runs"][0]

        self.assertEqual(snapshot["dataset_version"], "500-v1")
        self.assertEqual(snapshot["config"], {"retriever": "hierarchical"})
        self.assertEqual(entry["paper_version_id"], "version-1")
        self.assertEqual(entry["run_config"]["top_k"], 5)
        self.assertEqual(entry["status"], "succeeded")
        self.assertEqual(entry["reports"][0]["report_id"], "report-1")
        self.assertNotIn("artifact_path", str(snapshot))
        self.assertNotIn("sensitive weakness text", str(snapshot))
        self.assertNotIn("input_json", str(snapshot))

    def test_batch_attaches_created_run_when_queue_delivery_fails(self) -> None:
        class FailingQueue:
            def enqueue(self, job_id: str) -> str:
                raise RuntimeError(f"private failure for {job_id}")

        from app.services.experiment_manifest_service import ExperimentManifestService

        self.repository.replace_paper_assets("p1", "Paper", [], [], version_id="version-1")
        service = ExperimentManifestService(self.repository, ReviewAuditService(self.repository, FailingQueue()))
        manifest = service.create("Batch Audit", "PeerReview", "v1", {})

        result = service.schedule_paper_audits(
            manifest["manifest_id"],
            [PersistedPaperReviewAuditRequest(paper_id="p1", weaknesses=[])],
        )

        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["results"][0]["error_code"], "queue_unavailable")
        snapshot = service.get(manifest["manifest_id"])
        self.assertEqual(snapshot["runs"][0]["status"], "failed")
        self.assertNotIn("private failure", str(result))


if __name__ == "__main__":
    unittest.main()
