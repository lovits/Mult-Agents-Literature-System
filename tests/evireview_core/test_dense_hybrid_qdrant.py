from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock
from evireview_core.retrieval.dense import dense_search
from evireview_core.retrieval.hybrid import hybrid_search
from evireview_core.retrieval.qdrant import QdrantQueryClient


DOCS = [
    EvidenceBlock("b1", "p1", "Experiments", "experiment", "We compare BM25 against the proposed method."),
    EvidenceBlock("b2", "p1", "Ablations", "experiment", "Component removal causes a substantial accuracy drop."),
    EvidenceBlock("b3", "p1", "Introduction", "introduction", "Retrieval augmented generation is widely used."),
]


def fake_embed(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        lower = text.lower()
        if "ablation" in lower or "component removal" in lower:
            vectors.append([1.0, 0.0])
        elif "bm25" in lower:
            vectors.append([0.8, 0.2])
        else:
            vectors.append([0.0, 1.0])
    return vectors


class DenseHybridQdrantTest(unittest.TestCase):
    def test_dense_search_uses_injected_embeddings_and_cosine(self) -> None:
        results = dense_search("missing ablation evidence", DOCS, fake_embed, top_k=2)

        self.assertEqual([item.block_id for item in results], ["b2", "b1"])
        self.assertEqual(results[0].retriever, "dense_cosine")

    def test_hybrid_search_fuses_bm25_and_dense_ranks(self) -> None:
        results = hybrid_search("BM25 ablation", DOCS, fake_embed, top_k=3)

        self.assertEqual(results[0].block_id, "b1")
        self.assertEqual(results[0].retriever, "hybrid_rrf")
        self.assertGreater(results[0].score, results[1].score)

    def test_qdrant_hybrid_query_uses_prefetch_and_rrf(self) -> None:
        calls = []

        def transport(method: str, url: str, payload: dict) -> dict:
            calls.append((method, url, payload))
            return {"result": {"points": [{"id": "b2", "score": 0.75, "payload": {"paper_id": "p1"}}]}}

        client = QdrantQueryClient("http://qdrant:6333", transport=transport)
        points = client.hybrid_query(
            "evidence",
            dense_vector=[0.1, 0.9],
            sparse_vector={3: 0.8, 9: 0.2},
            limit=5,
            paper_id="p1",
        )

        self.assertEqual(points[0]["id"], "b2")
        method, url, payload = calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "http://qdrant:6333/collections/evidence/points/query")
        self.assertEqual(payload["query"], {"fusion": "rrf"})
        self.assertEqual(len(payload["prefetch"]), 2)
        self.assertEqual(payload["filter"]["must"][0]["match"]["value"], "p1")

    def test_qdrant_collection_lifecycle_maps_to_rest_api(self) -> None:
        calls = []

        def transport(method: str, url: str, payload: dict) -> dict:
            calls.append((method, url, payload))
            return {"result": {"operation_id": 1, "status": "completed"}}

        client = QdrantQueryClient("http://qdrant:6333", transport=transport)
        client.server_info()
        client.recreate_collection("evidence", dense_size=3)
        client.create_keyword_index("evidence", "paper_id")
        client.upsert_points(
            "evidence",
            [
                {
                    "id": 1,
                    "vector": {
                        "dense": [0.1, 0.2, 0.3],
                        "sparse": {"indices": [2], "values": [1.0]},
                    },
                    "payload": {"paper_id": "p1"},
                }
            ],
        )

        self.assertEqual(calls[0][:2], ("GET", "http://qdrant:6333/"))
        self.assertEqual(calls[1][:2], ("DELETE", "http://qdrant:6333/collections/evidence"))
        self.assertEqual(calls[2][:2], ("PUT", "http://qdrant:6333/collections/evidence"))
        self.assertEqual(calls[2][2]["vectors"]["dense"]["size"], 3)
        self.assertEqual(calls[2][2]["sparse_vectors"], {"sparse": {}})
        self.assertEqual(calls[3][:2], ("PUT", "http://qdrant:6333/collections/evidence/index?wait=true"))
        self.assertEqual(calls[3][2], {"field_name": "paper_id", "field_schema": "keyword"})
        self.assertEqual(calls[4][:2], ("PUT", "http://qdrant:6333/collections/evidence/points?wait=true"))
        self.assertEqual(calls[4][2]["points"][0]["id"], 1)

    def test_qdrant_dense_and_sparse_queries_share_payload_filters(self) -> None:
        calls = []

        def transport(method: str, url: str, payload: dict) -> dict:
            calls.append((method, url, payload))
            return {"result": {"points": []}}

        client = QdrantQueryClient("http://qdrant:6333", transport=transport)
        client.dense_query("evidence", [0.1, 0.9], filters={"row_id": 7})
        client.sparse_query("evidence", {3: 0.8}, filters={"row_id": 7})

        self.assertEqual(calls[0][2]["using"], "dense")
        self.assertEqual(calls[1][2]["using"], "sparse")
        self.assertEqual(calls[0][2]["filter"], calls[1][2]["filter"])


if __name__ == "__main__":
    unittest.main()
