from __future__ import annotations

from collections import defaultdict

from evireview_core.domain.models import EvidenceBlock
from evireview_core.retrieval.bm25 import RetrievedEvidence, bm25_search
from evireview_core.retrieval.dense import Embedder, dense_search


RRF_K = 60


def reciprocal_rank_fusion(ranked_lists: list[list[RetrievedEvidence]], top_k: int = 5) -> list[RetrievedEvidence]:
    scores: dict[str, float] = defaultdict(float)
    by_block: dict[str, RetrievedEvidence] = {}
    for ranked in ranked_lists:
        for item in ranked:
            scores[item.block_id] += 1.0 / (RRF_K + item.rank)
            by_block[item.block_id] = item
    block_ids = sorted(scores, key=lambda block_id: (-scores[block_id], block_id))[:top_k]
    return [
        RetrievedEvidence(
            block_id=item.block_id,
            paper_id=item.paper_id,
            section_path=item.section_path,
            section_type=item.section_type,
            text=item.text,
            rank=rank,
            score=round(scores[block_id], 6),
            retriever="hybrid_rrf",
        )
        for rank, block_id in enumerate(block_ids, start=1)
        for item in [by_block[block_id]]
    ]


def hybrid_search(query: str, docs: list[EvidenceBlock], embedder: Embedder, top_k: int = 5) -> list[RetrievedEvidence]:
    candidate_k = max(top_k * 2, top_k)
    return reciprocal_rank_fusion(
        [
            bm25_search(query, docs, top_k=candidate_k),
            dense_search(query, docs, embedder, top_k=candidate_k),
        ],
        top_k=top_k,
    )
