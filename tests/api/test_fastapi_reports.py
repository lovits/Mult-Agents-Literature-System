from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from services.worker.tasks.review_audit import run_job


class RecordingQueue:
    def enqueue(self, job_id: str) -> str:
        return f"delivery-{job_id}"


class FastApiReportsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        settings = Settings(
            sqlite_path=Path(self.temp_dir.name) / "api.sqlite3",
            redis_url="redis://localhost:6379/15",
            queue_name="test",
        )
        self.app = create_app(settings, RecordingQueue())
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_and_read_completed_run_report(self) -> None:
        created = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "paper-1", "weaknesses": [], "evidence_blocks": []},
        ).json()
        run_job(self.app.state.repository, created["job"]["job_id"])

        response = self.client.post(f"/api/runs/{created['run']['run_id']}/report")

        self.assertEqual(response.status_code, 201)
        report = response.json()
        self.assertEqual(report["metric_boundary"], "silver diagnostic")
        self.assertNotIn("artifact_path", report)
        self.assertEqual(self.client.get(f"/api/reports/{report['report_id']}").json(), report)
        markdown = self.client.get(f"/api/reports/{report['report_id']}/markdown")
        self.assertEqual(markdown.status_code, 200)
        self.assertIn("silver diagnostic", markdown.text)

    def test_incomplete_and_missing_reports_have_public_errors(self) -> None:
        created = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "paper-1", "weaknesses": [], "evidence_blocks": []},
        ).json()

        self.assertEqual(self.client.post(f"/api/runs/{created['run']['run_id']}/report").status_code, 409)
        self.assertEqual(self.client.get("/api/reports/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/reports/missing/markdown").status_code, 404)


if __name__ == "__main__":
    unittest.main()
