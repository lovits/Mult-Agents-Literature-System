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


class FastApiExperimentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(
            Settings(
                sqlite_path=Path(self.temp_dir.name) / "api.sqlite3",
                redis_url="redis://localhost:6379/15",
                queue_name="test",
            ),
            RecordingQueue(),
        )
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_list_get_and_attach_existing_run(self) -> None:
        run = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": []},
        ).json()["run"]
        created = self.client.post(
            "/api/experiments",
            json={
                "name": "PeerQA Retrieval",
                "dataset_name": "PeerQA-XT",
                "dataset_version": "500-v1",
                "config": {"retriever": "hierarchical"},
            },
        )
        manifest = created.json()

        attached = self.client.post(f"/api/experiments/{manifest['manifest_id']}/runs/{run['run_id']}")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(attached.status_code, 200)
        self.assertEqual(len(self.client.get("/api/experiments").json()), 1)
        snapshot = self.client.get(f"/api/experiments/{manifest['manifest_id']}").json()
        self.assertEqual(snapshot["runs"][0]["run_id"], run["run_id"])
        self.assertNotIn("input_json", str(snapshot))

    def test_manifest_validation_and_missing_resources(self) -> None:
        invalid = self.client.post(
            "/api/experiments",
            json={"name": "x", "dataset_name": "d", "dataset_version": "v", "config": {}, "extra": True},
        )
        created = self.client.post(
            "/api/experiments",
            json={"name": "x", "dataset_name": "d", "dataset_version": "v", "config": {}},
        ).json()

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(self.client.get("/api/experiments/missing").status_code, 404)
        self.assertEqual(self.client.post(f"/api/experiments/{created['manifest_id']}/runs/missing").status_code, 404)

    def test_manifest_rejects_secret_like_config_keys(self) -> None:
        response = self.client.post(
            "/api/experiments",
            json={
                "name": "x",
                "dataset_name": "d",
                "dataset_version": "v",
                "config": {"provider": {"api_key": "must-not-be-stored"}},
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertNotIn("must-not-be-stored", response.text)


if __name__ == "__main__":
    unittest.main()
