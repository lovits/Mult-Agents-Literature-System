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


class FailingQueue:
    def enqueue(self, job_id: str) -> str:
        raise RuntimeError(f"private queue failure for {job_id}")


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

    def _create_manifest(self) -> dict:
        return self.client.post(
            "/api/experiments",
            json={"name": "Batch Audit", "dataset_name": "PeerReview", "dataset_version": "v1", "config": {}},
        ).json()

    def _import_paper(self, paper_id: str, markdown: str = "# Paper\n\n## Experiments\n\nSensitive evidence.") -> dict:
        return self.client.post(
            "/api/papers/import",
            json={"paper_id": paper_id, "title": f"Paper {paper_id}", "markdown": markdown},
        ).json()

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

    def test_batch_schedules_version_bound_paper_audits_with_partial_success(self) -> None:
        manifest = self._create_manifest()
        imported = self._import_paper("p1")

        response = self.client.post(
            f"/api/experiments/{manifest['manifest_id']}/paper-audits",
            json={
                "items": [
                    {"paper_id": "p1", "weaknesses": [], "top_k": 2, "finding_top_k": 1},
                    {"paper_id": "missing", "weaknesses": []},
                ]
            },
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertEqual(payload["requested_count"], 2)
        self.assertEqual(payload["scheduled_count"], 1)
        self.assertEqual(payload["failed_count"], 1)
        self.assertEqual(payload["results"][0]["status"], "scheduled")
        self.assertEqual(payload["results"][1]["error_code"], "paper_not_found")
        self.assertNotIn("Sensitive evidence", response.text)

        snapshot = self.client.get(f"/api/experiments/{manifest['manifest_id']}").json()
        self.assertEqual(len(snapshot["runs"]), 1)
        self.assertEqual(snapshot["runs"][0]["paper_version_id"], imported["active_version_id"])
        self.assertEqual(snapshot["runs"][0]["run_config"]["top_k"], 2)
        stored = self.app.state.repository.load_input(snapshot["runs"][0]["run_id"])
        self.assertNotIn("evidence_blocks", stored)
        self.assertNotIn("Sensitive evidence", str(stored))

    def test_batch_rejects_more_than_one_hundred_items(self) -> None:
        manifest = self._create_manifest()

        response = self.client.post(
            f"/api/experiments/{manifest['manifest_id']}/paper-audits",
            json={"items": [{"paper_id": f"p{index}", "weaknesses": []} for index in range(101)]},
        )

        self.assertEqual(response.status_code, 422)

    def test_batch_attaches_delivery_failed_run_without_leaking_queue_error(self) -> None:
        app = create_app(
            Settings(
                sqlite_path=Path(self.temp_dir.name) / "failing.sqlite3",
                redis_url="redis://localhost:6379/15",
                queue_name="test",
            ),
            FailingQueue(),
        )
        client = TestClient(app)
        manifest = client.post(
            "/api/experiments",
            json={"name": "Batch Audit", "dataset_name": "PeerReview", "dataset_version": "v1", "config": {}},
        ).json()
        client.post(
            "/api/papers/import",
            json={"paper_id": "p1", "title": "Paper", "markdown": "# Paper\n\n## Method\n\nEvidence."},
        )

        response = client.post(
            f"/api/experiments/{manifest['manifest_id']}/paper-audits",
            json={"items": [{"paper_id": "p1", "weaknesses": []}]},
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["results"][0]["error_code"], "queue_unavailable")
        self.assertNotIn("private queue failure", response.text)
        snapshot = client.get(f"/api/experiments/{manifest['manifest_id']}").json()
        self.assertEqual(len(snapshot["runs"]), 1)
        self.assertEqual(snapshot["runs"][0]["status"], "failed")

    def test_manifest_metrics_endpoint_returns_public_metric_records(self) -> None:
        manifest = self._create_manifest()

        response = self.client.get(f"/api/experiments/{manifest['manifest_id']}/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["metric"], "run_count")
        self.assertEqual(response.json()[0]["metric_boundary"], "silver")
        self.assertNotIn("input_json", response.text)


if __name__ == "__main__":
    unittest.main()
