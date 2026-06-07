from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from services.worker.tasks.review_audit import run_job


class RecordingQueue:
    def __init__(self) -> None:
        self.job_ids: list[str] = []

    def enqueue(self, job_id: str) -> str:
        self.job_ids.append(job_id)
        return f"delivery-{job_id}"


class FailingQueue:
    def enqueue(self, job_id: str) -> str:
        raise ConnectionError(f"redis unavailable for {job_id}")


class FastApiRunsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings = Settings(
            sqlite_path=Path(self.temp_dir.name) / "api.sqlite3",
            redis_url="redis://localhost:6379/15",
            queue_name="test",
        )
        self.queue = RecordingQueue()
        self.app = create_app(self.settings, self.queue)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_create_run_enqueues_only_persisted_job_id(self) -> None:
        response = self.client.post(
            "/api/runs/review-audit",
            json={
                "paper_id": "p1",
                "weaknesses": [
                    {
                        "weakness_id": "w1",
                        "paper_id": "p1",
                        "weakness_text": "The paper has limited ablation baselines.",
                        "category": "experiment",
                        "severity": "major",
                    }
                ],
                "evidence_blocks": [
                    {
                        "block_id": "b1",
                        "paper_id": "p1",
                        "section_path": "Experiments",
                        "section_type": "experiment",
                        "text": "The paper has limited ablation baselines.",
                    }
                ],
                "top_k": 2,
                "finding_top_k": 1,
            },
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertEqual(self.queue.job_ids, [payload["job"]["job_id"]])
        self.assertNotIn("weaknesses", payload)
        self.assertNotIn("input_json", payload["run"])
        self.assertNotIn("result_json", payload["run"])
        self.assertNotIn("attempt_token", payload["job"])

    def test_create_run_rejects_unknown_graph_profile(self) -> None:
        response = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": [], "graph_profile": "missing"},
        )

        self.assertEqual(response.status_code, 422)

    def test_create_run_rejects_unknown_component_names(self) -> None:
        for field in ("query_planner", "retriever", "weakness_generator", "verifier"):
            response = self.client.post(
                "/api/runs/review-audit",
                json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": [], field: "missing"},
            )
            self.assertEqual(response.status_code, 422)

    def test_create_run_persists_provider_generator_without_accepting_credentials(self) -> None:
        response = self.client.post(
            "/api/runs/review-audit",
            json={
                "paper_id": "p1",
                "weaknesses": [],
                "evidence_blocks": [
                    {
                        "block_id": "b1",
                        "paper_id": "p1",
                        "section_path": "Experiments",
                        "section_type": "experiment",
                        "text": "Only one baseline is evaluated.",
                    }
                ],
                "weakness_generator": "minimax",
            },
        )
        rejected = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": [], "weakness_generator": "minimax", "api_key": "secret"},
        )

        self.assertEqual(response.status_code, 202)
        run_id = response.json()["run"]["run_id"]
        self.assertEqual(self.app.state.repository.load_input(run_id)["weakness_generator"], "minimax")
        self.assertEqual(rejected.status_code, 422)

    def test_run_job_then_read_run_findings_trace_and_job(self) -> None:
        created = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": []},
        ).json()
        run_id = created["run"]["run_id"]
        job_id = created["job"]["job_id"]

        result = run_job(self.app.state.repository, job_id)

        self.assertEqual(result["status"], "succeeded")
        run_payload = self.client.get(f"/api/runs/{run_id}").json()
        self.assertEqual(run_payload["status"], "succeeded")
        self.assertNotIn("input_json", run_payload)
        self.assertEqual(self.client.get(f"/api/runs/{run_id}/findings").json(), [])
        self.assertEqual(self.client.get(f"/api/jobs/{job_id}").json()["status"], "succeeded")
        events = self.client.get(f"/api/runs/{run_id}/trace").json()
        self.assertEqual([event["event_type"] for event in events], ["queued", "running", "succeeded"])
        agent_trace = self.client.get(f"/api/runs/{run_id}/agent-trace").json()
        self.assertEqual(
            [event["node"] for event in agent_trace],
            [
                "generate_or_import_weaknesses",
                "plan_weakness_queries",
                "retrieve_evidence",
                "verify_weaknesses",
                "deduplicate_weaknesses",
                "rank_findings",
            ],
        )

    def test_workspace_read_model_combines_weakness_evidence_results_and_trace(self) -> None:
        imported = self.client.post(
            "/api/papers/import",
            json={
                "paper_id": "p1",
                "title": "Workspace Paper",
                "markdown": "# Experiments\nThe paper reports only one baseline and no ablation.",
            },
        ).json()
        created = self.client.post(
            "/api/papers/p1/review-audit",
            json={
                "weaknesses": [
                    {
                        "weakness_id": "w1",
                        "paper_id": "p1",
                        "weakness_text": "The paper lacks an ablation.",
                        "category": "experiment",
                        "severity": "major",
                    }
                ],
                "finding_top_k": 1,
            },
        ).json()
        run_job(self.app.state.repository, created["job"]["job_id"])

        response = self.client.get(f"/api/runs/{created['run']['run_id']}/workspace")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["paper"]["active_version_id"], imported["active_version_id"])
        self.assertEqual(payload["run"]["paper_version_id"], imported["active_version_id"])
        self.assertEqual(payload["weaknesses"][0]["weakness_text"], "The paper lacks an ablation.")
        self.assertIn("The paper reports only one baseline", payload["evidence_blocks"][0]["text"])
        self.assertEqual(payload["metric_boundary"], "silver diagnostic")
        self.assertEqual([event["event_type"] for event in payload["trace"]], ["queued", "running", "succeeded"])
        self.assertNotIn("input_json", response.text)
        self.assertNotIn("artifact_path", response.text)
        self.assertNotIn("attempt_token", response.text)

    def test_workspace_static_application_is_served(self) -> None:
        response = self.client.get("/workspace/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("EviReview Paper Workspace", response.text)
        self.assertIn("/workspace/app.js", response.text)

    def test_missing_resource_returns_404(self) -> None:
        response = self.client.get("/api/runs/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get("/api/runs/missing/agent-trace").status_code, 404)

    def test_cross_paper_request_returns_422(self) -> None:
        response = self.client.post(
            "/api/runs/review-audit",
            json={
                "paper_id": "p1",
                "weaknesses": [
                    {"weakness_id": "w1", "paper_id": "p2", "weakness_text": "Missing.", "category": "other"}
                ],
                "evidence_blocks": [],
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_enqueue_failure_marks_persisted_job_failed_without_exposing_details(self) -> None:
        app = create_app(self.settings, FailingQueue())
        client = TestClient(app, raise_server_exceptions=False)

        response = client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": []},
        )

        self.assertEqual(response.status_code, 503)
        job = app.state.repository.get_job_for_run(app.state.repository.list_runs()[0]["run_id"])
        self.assertEqual(job["status"], "failed")
        self.assertNotIn("redis unavailable", response.text)

    def test_public_run_job_and_trace_redact_internal_error_and_payload_json(self) -> None:
        created = self.client.post(
            "/api/runs/review-audit",
            json={"paper_id": "p1", "weaknesses": [], "evidence_blocks": []},
        ).json()
        run_id = created["run"]["run_id"]
        job_id = created["job"]["job_id"]
        claimed = self.app.state.repository.claim_job(job_id)
        self.app.state.repository.mark_failed(
            run_id,
            job_id,
            claimed["attempt_token"],
            "sensitive-internal-raw-input-fragment",
        )

        run = self.client.get(f"/api/runs/{run_id}").json()
        job = self.client.get(f"/api/jobs/{job_id}").json()
        trace = self.client.get(f"/api/runs/{run_id}/trace").json()

        self.assertEqual(run["error"], "internal_error")
        self.assertEqual(job["error"], "internal_error")
        self.assertNotIn("sensitive-internal", str(trace))
        self.assertTrue(all("payload_json" not in event for event in trace))


if __name__ == "__main__":
    unittest.main()
