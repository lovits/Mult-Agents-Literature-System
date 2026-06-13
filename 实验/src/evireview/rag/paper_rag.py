from collections.abc import Callable, Sequence
from typing import Literal

from pydantic import BaseModel

from evireview.models.evidence import EvidenceBlock, EvidenceItem
from evireview.models.weakness import QueryPlan
from evireview.rag.bm25 import BM25Retriever
from evireview.rag.dense import DenseRetriever
from evireview.rag.fusion import reciprocal_rank_fusion
from evireview.rag.priors import apply_structure_priors, expand_neighbors


class PaperRAGConfig(BaseModel):
    mode: Literal["P2", "P3", "P4"] = "P4"
    top_k: int = 5
    retrieval_depth: int = 20
    section_weight: float = 0.1
    evidence_type_weight: float = 0.1
    neighbor_radius: int = 1


class PaperRAGResult(BaseModel):
    items: list[EvidenceItem]
    trace: dict[str, bool | str | int]


class PaperRAG:
    def __init__(
        self,
        blocks: list[EvidenceBlock],
        embed: Callable[[str], list[float]],
        *,
        query_embed: Callable[[str], list[float]] | None = None,
        embed_many: Callable[[Sequence[str]], list[list[float]]] | None = None,
    ):
        self.blocks = blocks
        self.block_by_id = {block.block_id: block for block in blocks}
        self.bm25 = BM25Retriever(blocks)
        self.dense = DenseRetriever(
            blocks,
            embed,
            query_embed=query_embed,
            embed_many=embed_many,
        )

    def retrieve(self, plan: QueryPlan, config: PaperRAGConfig) -> PaperRAGResult:
        keyword_query = " ".join(plan.keyword_queries)
        sparse = self.bm25.retrieve(keyword_query, config.retrieval_depth)
        dense = self.dense.retrieve(plan.semantic_query, config.retrieval_depth)
        fused = reciprocal_rank_fusion(
            [
                [item.evidence_id for item in sparse],
                [item.evidence_id for item in dense],
            ]
        )
        candidates = [
            {
                "id": item.item_id,
                "section": self.block_by_id[item.item_id].section,
                "type": self.block_by_id[item.item_id].evidence_type,
                "score": item.score,
            }
            for item in fused
        ]

        use_section = config.mode in {"P3", "P4"}
        use_type = config.mode == "P4"
        if use_section or use_type:
            candidates = apply_structure_priors(
                expected_sections=plan.expected_sections if use_section else [],
                expected_types=plan.expected_evidence_types if use_type else [],
                candidates=candidates,
                section_weight=config.section_weight,
                evidence_type_weight=config.evidence_type_weight,
            )

        ranked_ids = [candidate["id"] for candidate in candidates[: config.top_k]]
        selected_blocks = [self.block_by_id[item_id] for item_id in ranked_ids]
        if config.mode == "P4":
            selected_blocks = expand_neighbors(
                self.blocks,
                seed_ids=ranked_ids,
                radius=config.neighbor_radius,
            )
            selected_blocks.sort(
                key=lambda block: ranked_ids.index(block.block_id)
                if block.block_id in ranked_ids
                else len(ranked_ids) + block.ordinal
            )

        scores = {candidate["id"]: candidate["score"] for candidate in candidates}
        items = [
            EvidenceItem(
                evidence_id=block.block_id,
                source="paper",
                text=block.text,
                score=scores.get(block.block_id, 0.0),
                section=block.section,
                document_id=block.paper_id,
            )
            for block in selected_blocks[: config.top_k]
        ]
        return PaperRAGResult(
            items=items,
            trace={
                "mode": config.mode,
                "section_prior": use_section,
                "evidence_type_prior": use_type,
                "neighbor_expansion": config.mode == "P4",
                "retrieval_depth": config.retrieval_depth,
            },
        )
