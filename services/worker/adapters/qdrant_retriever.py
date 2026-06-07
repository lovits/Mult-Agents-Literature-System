from __future__ import annotations

import hashlib
import math
from collections import Counter

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.parsing.markdown_sections import tokenize
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.retrieval.dense import Embedder
from evireview_core.retrieval.qdrant import QdrantQueryClient


class QdrantRuntimeRetriever:
    def __init__(
        self,
        client: QdrantQueryClient,
        collection: str,
        docs: list[EvidenceBlock],
        embedder: Embedder | None = None,
    ) -> None:
        self.client = client
        self.collection = collection
        self.docs = list(docs)
        self.embedder = embedder
        self.vocabulary = self._vocabulary(self.docs)
        self.tokenized_docs = {doc.block_id: tokenize(doc.text) for doc in self.docs}
        lengths = [len(tokens) for tokens in self.tokenized_docs.values()]
        self.average_document_length = sum(lengths) / len(lengths) if lengths else 1.0
        self.document_frequency = Counter(
            term for tokens in self.tokenized_docs.values() for term in set(tokens)
        )
        self._index()

    def __call__(
        self,
        weakness: Weakness,
        query: str,
        _docs: list[EvidenceBlock],
        top_k: int,
    ) -> list[RetrievedEvidence]:
        sparse = self._query_sparse(query)
        if not sparse:
            return []
        if self.embedder is None:
            points = self.client.sparse_query(self.collection, sparse, top_k, {"paper_id": weakness.paper_id})
            retriever = "qdrant_sparse"
        else:
            dense = self.embedder([query])[0]
            points = self.client.hybrid_query(
                self.collection,
                dense,
                sparse,
                top_k,
                filters={"paper_id": weakness.paper_id},
            )
            retriever = "qdrant_hybrid"
        return [self._retrieved(point, rank, retriever) for rank, point in enumerate(points, start=1)]

    def _index(self) -> None:
        dense_vectors = self.embedder([doc.text for doc in self.docs]) if self.embedder is not None and self.docs else []
        if dense_vectors:
            self.client.recreate_collection(self.collection, len(dense_vectors[0]))
        else:
            self.client.recreate_sparse_collection(self.collection)
        self.client.create_keyword_index(self.collection, "paper_id")
        points = [
            {
                "id": index,
                "vector": self._point_vectors(doc, dense_vectors[index - 1] if dense_vectors else None),
                "payload": doc.to_dict(),
            }
            for index, doc in enumerate(self.docs, start=1)
        ]
        self.client.upsert_points(self.collection, points)

    def _point_vectors(self, doc: EvidenceBlock, dense: list[float] | None) -> dict:
        vectors = {"sparse": self._qdrant_sparse(self._document_sparse(doc))}
        if dense is not None:
            vectors["dense"] = dense
        return vectors

    def _document_sparse(self, doc: EvidenceBlock) -> dict[int, float]:
        tokens = self.tokenized_docs[doc.block_id]
        term_counts = Counter(tokens)
        vector = {}
        for term, tf in term_counts.items():
            if term not in self.vocabulary:
                continue
            df = self.document_frequency[term]
            idf = math.log(1 + (len(self.docs) - df + 0.5) / (df + 0.5))
            denom = tf + 1.5 * (1 - 0.75 + 0.75 * len(tokens) / self.average_document_length)
            vector[self.vocabulary[term]] = idf * tf * 2.5 / denom
        return vector

    def _query_sparse(self, query: str) -> dict[int, float]:
        return {
            self.vocabulary[term]: float(count)
            for term, count in Counter(tokenize(query)).items()
            if term in self.vocabulary
        }

    @staticmethod
    def _vocabulary(docs: list[EvidenceBlock]) -> dict[str, int]:
        terms = sorted({term for doc in docs for term in tokenize(doc.text)})
        return {term: index for index, term in enumerate(terms)}

    @staticmethod
    def _qdrant_sparse(vector: dict[int, float]) -> dict[str, list]:
        items = sorted((index, value) for index, value in vector.items() if value)
        return {"indices": [index for index, _ in items], "values": [value for _, value in items]}

    @staticmethod
    def _retrieved(point: dict, rank: int, retriever: str) -> RetrievedEvidence:
        payload = point["payload"]
        return RetrievedEvidence(
            block_id=str(payload["block_id"]),
            paper_id=str(payload["paper_id"]),
            section_path=str(payload["section_path"]),
            section_type=str(payload["section_type"]),
            text=str(payload["text"]),
            rank=rank,
            score=round(float(point.get("score", 0.0)), 6),
            retriever=retriever,
        )


def runtime_collection_name(docs: list[EvidenceBlock]) -> str:
    digest = hashlib.sha256("\n".join(f"{doc.block_id}:{doc.text}" for doc in docs).encode("utf-8")).hexdigest()[:16]
    return f"evireview_runtime_{digest}"
