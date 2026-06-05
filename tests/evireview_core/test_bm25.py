from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock
from evireview_core.retrieval.bm25 import bm25_search


class Bm25Test(unittest.TestCase):
    def test_bm25_returns_matching_experiment_block_first(self) -> None:
        blocks = [
            EvidenceBlock("b1", "p1", "Method", "method", "The model uses a planner."),
            EvidenceBlock("b2", "p1", "Experiments", "experiment", "The ablation study removes the reranker."),
            EvidenceBlock("b3", "p1", "Related Work", "related_work", "Prior work studies agents."),
        ]

        results = bm25_search("missing ablation study", blocks, top_k=2)

        self.assertEqual(results[0].block_id, "b2")
        self.assertEqual(results[0].rank, 1)
        self.assertGreater(results[0].score, 0.0)


if __name__ == "__main__":
    unittest.main()
