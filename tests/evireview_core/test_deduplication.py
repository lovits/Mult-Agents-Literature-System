from __future__ import annotations

import unittest

from evireview_core.deduplication.lexical import deduplicate_weaknesses
from evireview_core.domain.models import VerificationResult, Weakness


class WeaknessDeduplicationTest(unittest.TestCase):
    def test_deduplicates_same_paper_and_category_while_preserving_best_evidence(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper lacks an ablation study for the reranker.", "experiment", "major"),
            Weakness("w2", "p1", "The paper lacks ablation studies for the reranker.", "experiment", "major"),
            Weakness("w3", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        verification = {
            "w1": VerificationResult("w1", "Partially Supported", 0.4, ("b1",), "", "test"),
            "w2": VerificationResult("w2", "Supported", 0.9, ("b2",), "", "test"),
            "w3": VerificationResult("w3", "Supported", 0.8, ("b3",), "", "test"),
        }

        result = deduplicate_weaknesses(weaknesses, verification, threshold=0.7)

        self.assertEqual([item.weakness_id for item in result.weaknesses], ["w2", "w3"])
        self.assertEqual(result.duplicate_of, {"w1": "w2"})

    def test_does_not_merge_across_papers_or_categories(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper lacks an ablation study.", "experiment", "major"),
            Weakness("w2", "p2", "The paper lacks an ablation study.", "experiment", "major"),
            Weakness("w3", "p1", "The paper lacks an ablation study.", "clarity", "major"),
        ]

        result = deduplicate_weaknesses(weaknesses, {}, threshold=0.7)

        self.assertEqual([item.weakness_id for item in result.weaknesses], ["w1", "w2", "w3"])
        self.assertEqual(result.duplicate_of, {})


if __name__ == "__main__":
    unittest.main()
