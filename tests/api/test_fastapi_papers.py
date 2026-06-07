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

    def test_list_papers_and_paper_runs_for_workspace_navigation(self) -> None:
        self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# Experiments\nEvidence."},
        )
        created = self.client.post(
            "/api/papers/paper-1/review-audit",
            json={"weaknesses": []},
        ).json()

        papers = self.client.get("/api/papers")
        runs = self.client.get("/api/papers/paper-1/runs")

        self.assertEqual(papers.status_code, 200)
        self.assertEqual(papers.json()[0]["paper_id"], "paper-1")
        self.assertEqual(runs.status_code, 200)
        self.assertEqual(runs.json()[0]["run_id"], created["run"]["run_id"])
        self.assertNotIn("input_json", runs.text)

    def test_paper_request_validation_and_missing_resource(self) -> None:
        invalid = self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# A\nText", "extra": True},
        )

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(self.client.get("/api/papers/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/papers/missing/runs").status_code, 404)

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

    def test_create_review_audit_from_imported_paper_without_evidence_text(self) -> None:
        self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# Experiments\nNo ablation is reported."},
        )

        response = self.client.post(
            "/api/papers/paper-1/review-audit",
            json={
                "weaknesses": [
                    {
                        "weakness_id": "w1",
                        "paper_id": "paper-1",
                        "weakness_text": "The paper lacks an ablation.",
                        "category": "experiment",
                    }
                ],
                "finding_top_k": 1,
            },
        )

        self.assertEqual(response.status_code, 202)
        self.assertNotIn("evidence", response.text)

    def test_create_provider_generated_audit_from_imported_paper(self) -> None:
        self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# Experiments\nOnly one baseline is evaluated."},
        )

        response = self.client.post(
            "/api/papers/paper-1/review-audit",
            json={"weakness_generator": "minimax"},
        )

        self.assertEqual(response.status_code, 202)

    def test_persisted_paper_audit_validates_scope_and_missing_paper(self) -> None:
        self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Agent RAG", "markdown": "# Experiments\nNo ablation is reported."},
        )

        invalid_scope = self.client.post(
            "/api/papers/paper-1/review-audit",
            json={
                "weaknesses": [
                    {"weakness_id": "w1", "paper_id": "paper-2", "weakness_text": "Missing.", "category": "other"}
                ]
            },
        )
        inline_evidence = self.client.post(
            "/api/papers/paper-1/review-audit",
            json={"weaknesses": [], "evidence_blocks": []},
        )

        self.assertEqual(invalid_scope.status_code, 422)
        self.assertEqual(inline_evidence.status_code, 422)
        self.assertEqual(self.client.post("/api/papers/missing/review-audit", json={"weaknesses": []}).status_code, 404)

    def test_lists_immutable_versions_and_historical_evidence(self) -> None:
        first = self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Paper", "markdown": "# Abstract\nOriginal evidence."},
        ).json()
        second = self.client.post(
            "/api/papers/import",
            json={"paper_id": "paper-1", "title": "Paper", "markdown": "# Abstract\nChanged evidence."},
        ).json()

        paper = self.client.get("/api/papers/paper-1").json()
        versions = self.client.get("/api/papers/paper-1/versions").json()
        historical = self.client.get(
            f"/api/papers/paper-1/versions/{first['active_version_id']}/evidence-blocks"
        ).json()

        self.assertEqual(paper["active_version_id"], second["active_version_id"])
        self.assertEqual(len(versions), 2)
        self.assertIn("Original evidence.", historical[0]["text"])
        self.assertNotIn("ordinal", historical[0])
        self.assertEqual(
            self.client.get("/api/papers/paper-1/versions/missing/evidence-blocks").status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()
