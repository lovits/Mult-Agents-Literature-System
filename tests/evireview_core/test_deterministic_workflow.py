from __future__ import annotations

import unittest
from pathlib import Path

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.io.jsonl import read_jsonl
from evireview_core.workflow.deterministic import run_deterministic_review_audit


class DeterministicWorkflowTest(unittest.TestCase):
    def test_workflow_returns_retrieval_verification_and_ranking(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major"),
            Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        blocks = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The ablation baseline removes the reranker."),
            EvidenceBlock("b2", "p1", "Introduction", "introduction", "The paper motivates agent retrieval."),
        ]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(len(result["retrieval"]), 2)
        self.assertEqual(len(result["verification"]), 2)
        self.assertGreaterEqual(len(result["ranked_findings"]), 1)

    def test_workflow_runs_on_committed_jsonl_fixtures(self) -> None:
        fixture_dir = Path(__file__).resolve().parent / "fixtures"
        weaknesses = [Weakness.from_dict(row) for row in read_jsonl(fixture_dir / "sample_weaknesses.jsonl")]
        blocks = [EvidenceBlock.from_dict(row) for row in read_jsonl(fixture_dir / "sample_blocks.jsonl")]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["workflow"], "deterministic_review_audit_v1")
        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(result["metric_boundary"], "silver diagnostic")

    def test_workflow_controls_final_finding_count_separately(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major"),
            Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        blocks = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper has limited ablation baselines."),
            EvidenceBlock("b2", "p1", "Introduction", "introduction", "The motivation is unclear."),
        ]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=1, finding_top_k=1)

        self.assertEqual(len(result["ranked_findings"]), 1)


if __name__ == "__main__":
    unittest.main()
