from __future__ import annotations

from collections import defaultdict

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence, bm25_search
from evireview_core.retrieval.section_prior import section_prior


RRF_K = 60


def _section_read(weakness: Weakness, docs: list[EvidenceBlock], top_k: int) -> list[RetrievedEvidence]:
    scored: list[tuple[float, EvidenceBlock]] = []
    for doc in docs:
        prior = section_prior(weakness.category, doc.section_type)
        if prior > 0:
            scored.append((prior, doc))
    scored.sort(key=lambda item: (item[0], item[1].score), reverse=True)
    return [
        RetrievedEvidence(
            block_id=doc.block_id,
            paper_id=doc.paper_id,
            section_path=doc.section_path,
            section_type=doc.section_type,
            text=doc.text,
            rank=rank,
            score=score,
            retriever="section_read",
        )
        for rank, (score, doc) in enumerate(scored[:top_k], start=1)
    ]


def _rrf_merge(ranked_lists: list[list[RetrievedEvidence]], top_k: int) -> list[RetrievedEvidence]:
    scores: dict[str, float] = defaultdict(float)
    by_block: dict[str, RetrievedEvidence] = {}
    for ranked in ranked_lists:
        for item in ranked:
            scores[item.block_id] += 1.0 / (RRF_K + item.rank)
            by_block[item.block_id] = item
    merged_ids = sorted(scores, key=lambda block_id: scores[block_id], reverse=True)[:top_k]
    return [
        RetrievedEvidence(
            block_id=by_block[block_id].block_id,
            paper_id=by_block[block_id].paper_id,
            section_path=by_block[block_id].section_path,
            section_type=by_block[block_id].section_type,
            text=by_block[block_id].text,
            rank=rank,
            score=round(scores[block_id], 6),
            retriever="hierarchical_rrf",
        )
        for rank, block_id in enumerate(merged_ids, start=1)
    ]


def hierarchical_search(weakness: Weakness, docs: list[EvidenceBlock], top_k: int = 5) -> list[RetrievedEvidence]:
    same_paper_docs = [doc for doc in docs if doc.paper_id == weakness.paper_id]
    keyword = bm25_search(weakness.weakness_text, same_paper_docs, top_k=top_k)
    routed = _section_read(weakness, same_paper_docs, top_k=top_k)
    return _rrf_merge([keyword, routed], top_k=top_k)
