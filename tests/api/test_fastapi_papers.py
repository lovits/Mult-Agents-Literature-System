from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class RecordingQueue:
    def enqueue(self, job_id: str) -> str:
        return f"delivery-{job_id}"


class FastApiPapersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        settings = Settings(
            sqlite_path=Path(self.temp_dir.name) / "api.sqlite3",
            redis_url="redis://localhost:6379/15",
            queue_name="test",
        )
        self.client = TestClient(create_app(settings, RecordingQueue()))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_import_and_read_paper_assets_without_echoing_markdown(self) -> None:
        response = self.client.post(
            "/api/papers/import",
            json={
                "paper_id": "paper-1",
                "title": "Agent RAG",
                "markdown": "# Abstract\nA concise claim.\n\n# Experiments\nThree baselines are evaluated.",
            },
        )

        self.assertEqual(response.status_code, 201)
        imported = response.json()
        self.assertEqual(imported["section_count"], 2)
        self.assertNotIn("markdown", imported)
        self.assertEqual(self.client.get("/api/papers/paper-1").json()["title"], "Agent RAG")
        self.assertEqual(len(self.client.get("/api/papers/paper-1/sections").json()), 2)
        self.assertEqual(len(self.client.get("/api/papers/paper-1/evidence-blocks").json()), 2)

    def test_paper_request_validation_and_missing_resource(self) -> None:
        invalid = self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# A\nText", "extra": True},
        )

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(self.client.get("/api/papers/missing").status_code, 404)

    def test_imported_evidence_blocks_can_be_submitted_to_review_audit(self) -> None:
        self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# Experiments\nNo ablation is reported."},
        )
        blocks = self.client.get("/api/papers/paper-1/evidence-blocks").json()

        response = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "paper-1", "weaknesses": [], "evidence_blocks": blocks},
        )

        self.assertEqual(response.status_code, 202)


if __name__ == "__main__":
    unittest.main()
