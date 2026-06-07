from __future__ import annotations

import unittest
from unittest.mock import patch

from evireview_core.domain.models import EvidenceBlock, Weakness
from services.worker.adapters.qdrant_retriever import QdrantRuntimeRetriever
from services.worker.tasks.review_audit import build_retriever


class FakeQdrantClient:
    def __init__(self) -> None:
        self.points = []
        self.recreated = []

    def recreate_sparse_collection(self, collection: str) -> None:
        self.recreated.append(("sparse", collection))

    def recreate_collection(self, collection: str, dense_size: int) -> None:
        self.recreated.append(("hybrid", collection, dense_size))

    def create_keyword_index(self, _collection: str, _field_name: str) -> None:
        return None

    def upsert_points(self, _collection: str, points: list[dict]) -> None:
        self.points.extend(points)

    def sparse_query(self, _collection: str, _vector: dict[int, float], limit: int, _filters: dict) -> list[dict]:
        return [{"score": 0.8, "payload": self.points[0]["payload"]}][:limit]

    def hybrid_query(
        self,
        _collection: str,
        _dense: list[float],
        _sparse: dict[int, float],
        limit: int,
        filters: dict,
    ) -> list[dict]:
        self.hybrid_filters = filters
        return [{"score": 0.9, "payload": self.points[1]["payload"]}][:limit]


class QdrantRuntimeRetrieverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.docs = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The ablation removes the reranker."),
            EvidenceBlock("b2", "p1", "Method", "method", "The method uses a retrieval agent."),
        ]

    def test_sparse_runtime_retriever_indexes_and_queries_paper_blocks(self) -> None:
        client = FakeQdrantClient()
        retriever = QdrantRuntimeRetriever(client, "runtime", self.docs)

        results = retriever(Weakness("w1", "p1", "Missing ablation.", "experiment"), "ablation", self.docs, 1)

        self.assertEqual(client.recreated, [("sparse", "runtime")])
        self.assertEqual(results[0].block_id, "b1")
        self.assertEqual(results[0].retriever, "qdrant_sparse")

    def test_hybrid_runtime_retriever_uses_injected_embedder(self) -> None:
        client = FakeQdrantClient()

        def embedder(texts: list[str]) -> list[list[float]]:
            return [[float(index), 1.0] for index, _ in enumerate(texts, start=1)]

        retriever = QdrantRuntimeRetriever(client, "runtime", self.docs, embedder=embedder)
        results = retriever(Weakness("w1", "p1", "Method issue.", "method"), "method", self.docs, 1)

        self.assertEqual(client.recreated, [("hybrid", "runtime", 2)])
        self.assertEqual(results[0].block_id, "b2")
        self.assertEqual(results[0].retriever, "qdrant_hybrid")
        self.assertEqual(client.hybrid_filters, {"paper_id": "p1"})

    def test_default_hybrid_factory_requires_embedding_environment(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "embedding"):
                build_retriever("qdrant_hybrid", self.docs)


if __name__ == "__main__":
    unittest.main()
