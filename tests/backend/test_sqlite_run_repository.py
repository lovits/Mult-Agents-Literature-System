from __future__ import annotations

import tempfile
import unittest
import sqlite3
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository


class SQLiteRunRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.input_payload = {
            "paper_id": "p1",
            "weaknesses": [],
            "evidence_blocks": [],
            "top_k": 5,
            "finding_top_k": 3,
        }

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_and_read_run_job_and_events(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)

        run = self.repository.get_run("run-1")
        job = self.repository.get_job("job-1")
        events = self.repository.list_events("job-1")

        self.assertEqual(run["status"], "queued")
        self.assertEqual(job["status"], "queued")
        self.assertEqual(events[0]["event_type"], "queued")

    def test_claim_next_job_marks_job_running(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)

        claimed = self.repository.claim_next_job()

        self.assertEqual(claimed["job_id"], "job-1")
        self.assertTrue(claimed["attempt_token"])
        self.assertEqual(self.repository.get_job("job-1")["status"], "running")
        self.assertEqual(self.repository.get_run("run-1")["status"], "running")

    def test_recover_running_jobs_does_not_requeue_active_lease(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        self.repository.claim_next_job()

        recovered = self.repository.recover_running_jobs()

        self.assertEqual(recovered, 0)
        self.assertEqual(self.repository.get_job("job-1")["status"], "running")
        self.assertEqual(self.repository.get_run("run-1")["status"], "running")

    def test_recover_running_jobs_requeues_expired_lease(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        self.repository.claim_next_job(lease_seconds=-1)

        recovered = self.repository.recover_running_jobs()

        self.assertEqual(recovered, 1)
        self.assertEqual(self.repository.get_job("job-1")["status"], "queued")
        self.assertEqual(self.repository.get_run("run-1")["status"], "queued")

    def test_succeeded_result_is_not_overwritten(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        claimed = self.repository.claim_next_job()
        self.repository.save_result("run-1", "job-1", claimed["attempt_token"], {"ranked_findings": []})

        with self.assertRaisesRegex(RuntimeError, "succeeded"):
            self.repository.save_result(
                "run-1",
                "job-1",
                claimed["attempt_token"],
                {"ranked_findings": [{"weakness_id": "other"}]},
            )

        self.assertFalse(self.repository.mark_failed("run-1", "job-1", claimed["attempt_token"], "late failure"))
        self.assertEqual(self.repository.get_run("run-1")["status"], "succeeded")
        self.assertEqual(self.repository.get_job("job-1")["status"], "succeeded")

    def test_result_rejects_mismatched_run_and_job(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        self.repository.create_run_and_job("run-2", "job-2", {**self.input_payload, "paper_id": "p2"})
        claimed = self.repository.claim_next_job()

        with self.assertRaisesRegex(RuntimeError, "matching running"):
            self.repository.save_result("run-1", "job-2", claimed["attempt_token"], {"ranked_findings": []})

        self.assertEqual(self.repository.get_run("run-1")["status"], "running")
        self.assertEqual(self.repository.get_job("job-2")["status"], "queued")

    def test_late_attempt_cannot_overwrite_reclaimed_job(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        first = self.repository.claim_next_job(lease_seconds=-1)
        self.repository.recover_running_jobs()
        second = self.repository.claim_next_job()

        with self.assertRaisesRegex(RuntimeError, "current attempt"):
            self.repository.save_result("run-1", "job-1", first["attempt_token"], {"ranked_findings": []})
        self.assertFalse(self.repository.mark_failed("run-1", "job-1", first["attempt_token"], "late failure"))

        self.repository.save_result("run-1", "job-1", second["attempt_token"], {"ranked_findings": []})
        self.assertEqual(self.repository.get_run("run-1")["status"], "succeeded")

    def test_snapshot_and_resolve_evidence_block_ids_preserve_order(self) -> None:
        self.repository.replace_paper_assets(
            "p1",
            "Paper",
            [],
            [
                {
                    "block_id": "b1",
                    "paper_id": "p1",
                    "ordinal": 0,
                    "section_path": "Abstract",
                    "section_type": "abstract",
                    "text": "First.",
                    "score": 0.0,
                },
                {
                    "block_id": "b2",
                    "paper_id": "p1",
                    "ordinal": 1,
                    "section_path": "Experiments",
                    "section_type": "experiment",
                    "text": "Second.",
                    "score": 0.0,
                },
            ],
        )

        self.assertEqual(self.repository.list_evidence_block_ids("p1"), ["b1", "b2"])
        resolved = self.repository.get_evidence_blocks_by_ids("p1", ["b2", "b1"])
        self.assertEqual([item["block_id"] for item in resolved], ["b2", "b1"])

        with self.assertRaises(KeyError):
            self.repository.get_evidence_blocks_by_ids("p1", ["b1", "missing"])

    def test_versioned_evidence_is_immutable_when_active_assets_change(self) -> None:
        original = {
            "block_id": "b1",
            "paper_id": "p1",
            "ordinal": 0,
            "section_path": "Abstract",
            "section_type": "abstract",
            "text": "Original.",
            "score": 0.0,
        }
        changed = {**original, "block_id": "b2", "text": "Changed."}

        self.repository.replace_paper_assets("p1", "Paper", [], [original], version_id="version-1")
        self.repository.replace_paper_assets("p1", "Paper", [], [changed], version_id="version-2")

        self.assertEqual(self.repository.get_active_paper_version("p1")["version_id"], "version-2")
        self.assertEqual([item["version_id"] for item in self.repository.list_paper_versions("p1")], ["version-1", "version-2"])
        self.assertEqual(
            self.repository.get_version_evidence_blocks_by_ids("p1", "version-1", ["b1"])[0]["text"],
            "Original.",
        )
        with self.assertRaises(KeyError):
            self.repository.get_version_evidence_blocks_by_ids("p1", "version-1", ["b2"])

    def test_initialize_backfills_pre_version_paper_assets(self) -> None:
        path = Path(self.temp_dir.name) / "legacy.sqlite3"
        with sqlite3.connect(path) as connection:
            connection.executescript(
                """
                CREATE TABLE papers (
                    paper_id TEXT PRIMARY KEY, title TEXT NOT NULL, source_type TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE paper_sections (
                    section_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL, section_type TEXT NOT NULL, text TEXT NOT NULL
                );
                CREATE TABLE evidence_blocks (
                    block_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL, section_type TEXT NOT NULL, text TEXT NOT NULL, score REAL NOT NULL
                );
                INSERT INTO papers VALUES ('legacy', 'Legacy Paper', 'markdown', '2026-01-01', '2026-01-01');
                INSERT INTO paper_sections VALUES ('s1', 'legacy', 0, 'Abstract', 'abstract', 'Legacy section.');
                INSERT INTO evidence_blocks VALUES ('b1', 'legacy', 0, 'Abstract', 'abstract', 'Legacy evidence.', 0.0);
                """
            )
        repository = SQLiteRunRepository(path)

        repository.initialize()

        paper = repository.get_paper("legacy")
        self.assertTrue(paper["active_version_id"].startswith("version-"))
        self.assertEqual(
            repository.list_version_evidence_blocks("legacy", paper["active_version_id"])[0]["text"],
            "Legacy evidence.",
        )

    def test_experiment_manifest_persists_ordered_idempotent_run_membership(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        self.repository.create_run_and_job("run-2", "job-2", {**self.input_payload, "paper_id": "p2"})

        self.repository.create_experiment_manifest(
            "experiment-1",
            "PeerQA Retrieval",
            "PeerQA-XT",
            "500-v1",
            {"top_k": 5},
        )
        self.repository.attach_run_to_experiment("experiment-1", "run-2")
        self.repository.attach_run_to_experiment("experiment-1", "run-1")
        self.repository.attach_run_to_experiment("experiment-1", "run-2")

        manifest = self.repository.get_experiment_manifest("experiment-1")
        self.assertEqual(manifest["dataset_version"], "500-v1")
        self.assertEqual(manifest["config"], {"top_k": 5})
        self.assertEqual(self.repository.list_experiment_run_ids("experiment-1"), ["run-2", "run-1"])

        with self.assertRaises(KeyError):
            self.repository.attach_run_to_experiment("experiment-1", "missing")

    def test_lists_reports_for_run(self) -> None:
        self.repository.create_run_and_job("run-1", "job-1", self.input_payload)
        self.repository.create_report("report-1", "run-1", "p1", "silver diagnostic", "/internal/report.md")

        reports = self.repository.list_reports_for_run("run-1")

        self.assertEqual([item["report_id"] for item in reports], ["report-1"])


if __name__ == "__main__":
    unittest.main()
