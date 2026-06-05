from __future__ import annotations

import unittest

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import rank_weaknesses, score_finding
from evireview_core.verification.labels import VerifierLabel


class EvidenceAwareRankerTest(unittest.TestCase):
    def test_score_favors_supported_major_weakness(self) -> None:
        weakness = Weakness("w1", "p1", "Major missing ablation.", "experiment", "major")
        result = VerificationResult(
            weakness_id="w1",
            label=VerifierLabel.SUPPORTED.value,
            support_score=0.8,
            evidence_block_ids=("b1",),
            rationale="Evidence supports the issue.",
            verifier="test",
        )

        self.assertGreater(score_finding(weakness, result), 1.0)

    def test_rank_weaknesses_orders_by_evidence_score(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "Minor clarity issue.", "clarity", "minor"),
            Weakness("w2", "p1", "Major experiment issue.", "experiment", "major"),
        ]
        verification = {
            "w1": VerificationResult("w1", VerifierLabel.MENTIONED_NOT_PROBLEM.value, 0.2, ("b1",), "", "test"),
            "w2": VerificationResult("w2", VerifierLabel.SUPPORTED.value, 0.8, ("b2",), "", "test"),
        }

        ranked = rank_weaknesses(weaknesses, verification, top_k=2)

        self.assertEqual(ranked[0].weakness_id, "w2")
        self.assertEqual(ranked[0].rank, 1)


if __name__ == "__main__":
    unittest.main()
