from __future__ import annotations

import math
from collections.abc import Callable

from evireview_core.domain.models import EvidenceBlock
from evireview_core.retrieval.bm25 import RetrievedEvidence


Embedder = Callable[[list[str]], list[list[float]]]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def dense_search(query: str, docs: list[EvidenceBlock], embedder: Embedder, top_k: int = 5) -> list[RetrievedEvidence]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if not docs:
        return []
    vectors = embedder([query, *[doc.text for doc in docs]])
    if len(vectors) != len(docs) + 1:
        raise ValueError("embedder must return one vector per input text")
    query_vector, doc_vectors = vectors[0], vectors[1:]
    scored = sorted(
        ((cosine_similarity(query_vector, vector), doc) for vector, doc in zip(doc_vectors, docs)),
        key=lambda item: (-item[0], item[1].block_id),
    )[:top_k]
    return [
        RetrievedEvidence(
            block_id=doc.block_id,
            paper_id=doc.paper_id,
            section_path=doc.section_path,
            section_type=doc.section_type,
            text=doc.text,
            rank=rank,
            score=round(score, 6),
            retriever="dense_cosine",
        )
        for rank, (score, doc) in enumerate(scored, start=1)
    ]
