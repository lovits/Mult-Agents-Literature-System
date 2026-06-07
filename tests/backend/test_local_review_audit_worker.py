from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import ReviewAuditRequest
from app.services.review_audit_service import ReviewAuditService
from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.workflow.state import WeaknessGenerationResult
from services.worker.tasks.review_audit import recover_and_run, run_next_job


class LocalReviewAuditWorkerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.service = ReviewAuditService(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_worker_executes_queued_review_audit(self) -> None:
        created = self.service.create_review_audit(
            ReviewAuditRequest(
                paper_id="p1",
                weaknesses=[Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major")],
                evidence_blocks=[
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper has limited ablation baselines.")
                ],
            )
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "succeeded")
        self.assertEqual(len(self.service.get_findings(created["run"]["run_id"])), 1)
        stored_result = self.repository.get_run(created["run"]["run_id"])["result"]
        self.assertEqual(
            [item["node"] for item in stored_result["agent_trace"]],
            [
                "generate_or_import_weaknesses",
                "plan_weakness_queries",
                "retrieve_evidence",
                "verify_weaknesses",
                "deduplicate_weaknesses",
                "rank_findings",
                "classify_auxiliary_decision",
            ],
        )

    def test_worker_records_invalid_input_failure(self) -> None:
        self.repository.create_run_and_job(
            "run-bad",
            "job-bad",
            {"paper_id": "p1", "weaknesses": [{"paper_id": "p1"}], "evidence_blocks": [], "top_k": 5, "finding_top_k": 3},
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "failed")
        self.assertIn("weakness_id", self.repository.get_run("run-bad")["error"])

    def test_worker_executes_requested_graph_profile(self) -> None:
        self.repository.create_run_and_job(
            "run-profile",
            "job-profile",
            {
                "paper_id": "p1",
                "weaknesses": [
                    Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major").to_dict()
                ],
                "evidence_blocks": [
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper reports results.").to_dict()
                ],
                "graph_profile": "no_verifier",
            },
        )

        run_next_job(self.repository)
        result = self.repository.get_run("run-profile")["result"]

        self.assertEqual(result["graph_profile"], "no_verifier")
        self.assertEqual(result["agent_trace"][3]["node"], "assume_supported")

    def test_worker_executes_selected_query_planner_and_retriever(self) -> None:
        self.repository.create_run_and_job(
            "run-components",
            "job-components",
            {
                "paper_id": "p1",
                "weaknesses": [Weakness("w1", "p1", "Evaluation is incomplete.", "experiment", "major").to_dict()],
                "evidence_blocks": [
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "Ablation baseline evaluation.").to_dict()
                ],
                "query_planner": "category_expansion",
                "retriever": "bm25",
            },
        )

        run_next_job(self.repository)
        result = self.repository.get_run("run-components")["result"]

        self.assertEqual(result["query_planner"], "category_expansion")
        self.assertEqual(result["retriever"], "bm25")
        self.assertEqual(result["agent_trace"][2]["retriever"], "bm25")

    def test_worker_executes_injected_hosted_retriever(self) -> None:
        self.repository.create_run_and_job(
            "run-qdrant",
            "job-qdrant",
            {
                "paper_id": "p1",
                "weaknesses": [Weakness("w1", "p1", "Missing ablation.", "experiment", "major").to_dict()],
                "evidence_blocks": [
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "No ablation is reported.").to_dict()
                ],
                "retriever": "qdrant_sparse",
            },
        )

        def retriever_factory(name, blocks):
            self.assertEqual(name, "qdrant_sparse")
            self.assertEqual(blocks[0].block_id, "b1")

            def retrieve(_weakness, _query, docs, _top_k):
                from evireview_core.retrieval.bm25 import RetrievedEvidence

                doc = docs[0]
                return [RetrievedEvidence(doc.block_id, doc.paper_id, doc.section_path, doc.section_type, doc.text, 1, 1.0, name)]

            return retrieve

        result = run_next_job(self.repository, retriever_factory=retriever_factory)
        stored = self.repository.get_run("run-qdrant")["result"]

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(stored["retriever"], "qdrant_sparse")
        self.assertEqual(stored["retrieval"]["w1"][0]["retriever"], "qdrant_sparse")

    def test_worker_executes_selected_minimax_weakness_generator(self) -> None:
        self.repository.create_run_and_job(
            "run-generated",
            "job-generated",
            {
                "paper_id": "p1",
                "weaknesses": [],
                "evidence_blocks": [
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "Only one baseline is evaluated.").to_dict()
                ],
                "weakness_generator": "minimax",
            },
        )

        def generator_factory(name: str):
            self.assertEqual(name, "minimax")

            def generate(_state):
                return WeaknessGenerationResult(
                    weaknesses=[
                        Weakness("generated-1", "p1", "The evaluation uses only one baseline.", "experiment", "major")
                    ],
                    metadata={"provider_name": "minimax", "model_name": "MiniMax-M2.7", "is_silver": True},
                )

            return generate

        result = run_next_job(self.repository, generator_factory=generator_factory)
        stored = self.repository.get_run("run-generated")["result"]

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(stored["weakness_generator"], "minimax")
        self.assertEqual(stored["weakness_count"], 1)
        self.assertEqual(stored["weaknesses"][0]["weakness_id"], "generated-1")
        self.assertEqual(stored["generation_metadata"]["provider_name"], "minimax")

    def test_worker_executes_selected_minimax_verifier(self) -> None:
        self.repository.create_run_and_job(
            "run-verified",
            "job-verified",
            {
                "paper_id": "p1",
                "weaknesses": [Weakness("w1", "p1", "Missing ablation.", "experiment", "major").to_dict()],
                "evidence_blocks": [
                    EvidenceBlock("b1", "p1", "Experiments", "experiment", "No ablation is reported.").to_dict()
                ],
                "verifier": "minimax",
            },
        )

        def verifier_factory(name: str):
            self.assertEqual(name, "minimax")

            def verify(weakness, evidence):
                return VerificationResult(
                    weakness_id=weakness.weakness_id,
                    label="Supported",
                    support_score=0.9,
                    evidence_block_ids=tuple(item.block_id for item in evidence),
                    rationale="Provider judgment.",
                    verifier="fake_minimax_judge",
                )

            return verify

        result = run_next_job(self.repository, verifier_factory=verifier_factory)
        stored = self.repository.get_run("run-verified")["result"]

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(stored["verifier"], "minimax")
        self.assertEqual(stored["verification"]["w1"]["verifier"], "fake_minimax_judge")

    def test_worker_recovers_running_job_before_execution(self) -> None:
        created = self.service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        self.repository.claim_next_job(lease_seconds=-1)

        results = recover_and_run(self.repository)

        self.assertEqual(results[0]["status"], "succeeded")
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "succeeded")

    def test_worker_does_not_recover_active_running_job(self) -> None:
        created = self.service.create_review_audit(ReviewAuditRequest(paper_id="p1", weaknesses=[], evidence_blocks=[]))
        self.repository.claim_next_job()

        results = recover_and_run(self.repository)

        self.assertEqual(results, [])
        self.assertEqual(self.service.get_run(created["run"]["run_id"])["status"], "running")

    def test_worker_resolves_persisted_evidence_block_ids(self) -> None:
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
                    "text": "The paper has limited ablation baselines.",
                    "score": 0.0,
                }
            ],
        )
        self.repository.create_run_and_job(
            "run-ref",
            "job-ref",
            {
                "paper_id": "p1",
                "weaknesses": [
                    Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major").to_dict()
                ],
                "evidence_block_ids": ["b1"],
                "top_k": 5,
                "finding_top_k": 3,
            },
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(self.repository.get_run("run-ref")["result"]["evidence_block_count"], 1)

    def test_worker_fails_when_snapshotted_evidence_is_missing(self) -> None:
        self.repository.create_run_and_job(
            "run-missing",
            "job-missing",
            {
                "paper_id": "p1",
                "weaknesses": [],
                "evidence_block_ids": ["missing"],
                "top_k": 5,
                "finding_top_k": 3,
            },
        )

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "failed")
        self.assertIn("evidence block", self.repository.get_run("run-missing")["error"])

    def test_worker_uses_immutable_version_after_paper_reimport(self) -> None:
        original = {
            "block_id": "b-original",
            "paper_id": "p1",
            "ordinal": 0,
            "section_path": "Experiments",
            "section_type": "experiment",
            "text": "The original paper lacks an ablation study.",
            "score": 0.0,
        }
        changed = {**original, "block_id": "b-changed", "text": "The changed paper includes an ablation study."}
        self.repository.replace_paper_assets("p1", "Paper", [], [original], version_id="version-1")
        self.repository.create_run_and_job(
            "run-versioned",
            "job-versioned",
            {
                "paper_id": "p1",
                "paper_version_id": "version-1",
                "weaknesses": [
                    Weakness("w1", "p1", "The paper lacks an ablation study.", "experiment", "major").to_dict()
                ],
                "evidence_block_ids": ["b-original"],
                "evidence_source": "persisted_paper_version",
                "top_k": 5,
                "finding_top_k": 3,
            },
        )
        self.repository.replace_paper_assets("p1", "Paper", [], [changed], version_id="version-2")

        result = run_next_job(self.repository)

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(self.repository.get_run("run-versioned")["result"]["evidence_block_count"], 1)


if __name__ == "__main__":
    unittest.main()
