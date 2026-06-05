from __future__ import annotations

import unittest

from evireview_core.domain.models import Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.heuristic import verify_with_heuristics
from evireview_core.verification.labels import VerifierLabel


class HeuristicVerifierTest(unittest.TestCase):
    def test_verifier_marks_partially_supported_when_evidence_overlaps(self) -> None:
        weakness = Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major")
        evidence = [
            RetrievedEvidence(
                block_id="b1",
                paper_id="p1",
                section_path="Experiments",
                section_type="experiment",
                text="The paper has limited ablation baselines for the reranker and reports accuracy.",
                rank=1,
                score=2.0,
                retriever="bm25",
            )
        ]

        result = verify_with_heuristics(weakness, evidence)

        self.assertEqual(result.label, VerifierLabel.PARTIALLY_SUPPORTED.value)
        self.assertGreater(result.support_score, 0.0)
        self.assertEqual(result.evidence_block_ids, ("b1",))

    def test_verifier_marks_contradicted_when_missing_claim_is_present(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")
        evidence = [
            RetrievedEvidence(
                block_id="b1",
                paper_id="p1",
                section_path="Experiments",
                section_type="experiment",
                text="The paper includes ablation baselines for the reranker and reports accuracy.",
                rank=1,
                score=2.0,
                retriever="bm25",
            )
        ]

        result = verify_with_heuristics(weakness, evidence)

        self.assertEqual(result.label, VerifierLabel.CONTRADICTED.value)
        self.assertGreater(result.support_score, 0.0)
        self.assertEqual(result.evidence_block_ids, ("b1",))

    def test_verifier_does_not_contradict_negated_presence_evidence(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")
        evidence = [
            RetrievedEvidence(
                block_id="b1",
                paper_id="p1",
                section_path="Experiments",
                section_type="experiment",
                text="The paper does not include ablation baselines.",
                rank=1,
                score=2.0,
                retriever="bm25",
            )
        ]

        result = verify_with_heuristics(weakness, evidence)

        self.assertNotEqual(result.label, VerifierLabel.CONTRADICTED.value)

    def test_verifier_does_not_contradict_reported_absence_evidence(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")
        evidence = [
            RetrievedEvidence(
                block_id="b1",
                paper_id="p1",
                section_path="Experiments",
                section_type="experiment",
                text="The paper reports no ablation baselines.",
                rank=1,
                score=2.0,
                retriever="bm25",
            )
        ]

        result = verify_with_heuristics(weakness, evidence)

        self.assertNotEqual(result.label, VerifierLabel.CONTRADICTED.value)

    def test_verifier_marks_unsupported_without_evidence(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")

        result = verify_with_heuristics(weakness, [])

        self.assertEqual(result.label, VerifierLabel.UNSUPPORTED.value)
        self.assertEqual(result.support_score, 0.0)


if __name__ == "__main__":
    unittest.main()
