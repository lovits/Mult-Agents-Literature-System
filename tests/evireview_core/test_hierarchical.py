from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.retrieval.section_prior import section_prior


class HierarchicalRetrievalTest(unittest.TestCase):
    def test_section_prior_prefers_expected_experiment_section(self) -> None:
        self.assertEqual(section_prior("experiment", "experiment"), 1.15)
        self.assertEqual(section_prior("experiment", "method"), 0.85)
        self.assertEqual(section_prior("experiment", "reference"), 0.15)
        self.assertEqual(section_prior("experiment", "related_work"), 0.0)

    def test_hierarchical_search_returns_section_routed_candidate(self) -> None:
        weakness = Weakness(
            weakness_id="w1",
            paper_id="p1",
            weakness_text="The paper lacks ablation baselines.",
            category="experiment",
            severity="major",
        )
        blocks = [
            EvidenceBlock("b1", "p1", "Method", "method", "The method has a planner."),
            EvidenceBlock("b2", "p1", "Experiments", "experiment", "The paper reports datasets and baselines."),
            EvidenceBlock("b3", "p1", "References", "reference", "References are listed here."),
        ]

        results = hierarchical_search(weakness, blocks, top_k=2)

        self.assertEqual(results[0].block_id, "b2")
        self.assertEqual(results[0].retriever, "hierarchical_rrf")

    def test_hierarchical_search_prefers_exact_section_over_method_tie(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")
        blocks = [
            EvidenceBlock("b1", "p1", "Method", "method", "The method mentions baselines."),
            EvidenceBlock("b2", "p1", "Experiments", "experiment", "The paper reports ablation baselines."),
        ]

        results = hierarchical_search(weakness, blocks, top_k=1)

        self.assertEqual(results[0].block_id, "b2")


if __name__ == "__main__":
    unittest.main()
