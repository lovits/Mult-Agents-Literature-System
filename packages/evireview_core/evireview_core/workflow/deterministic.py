from __future__ import annotations

from collections.abc import Callable
from typing import Any

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.workflow.graph import ReviewAuditGraph
from evireview_core.workflow.state import ReviewAuditState, WeaknessGenerationResult


def run_deterministic_review_audit(
    weaknesses: list[Weakness],
    blocks: list[EvidenceBlock],
    top_k: int = 5,
    finding_top_k: int = 3,
    graph_profile: str = "full",
    query_planner: str = "direct",
    retriever: str = "hierarchical",
    weakness_generator: Callable[[ReviewAuditState], WeaknessGenerationResult] | None = None,
    weakness_generator_name: str = "imported",
    verifier: Callable[[Weakness, list[RetrievedEvidence]], VerificationResult] | None = None,
    verifier_name: str = "heuristic",
) -> dict[str, Any]:
    state = ReviewAuditGraph(graph_profile).run(
        ReviewAuditState(
            weaknesses=weaknesses,
            evidence_blocks=blocks,
            top_k=top_k,
            finding_top_k=finding_top_k,
            query_planner_name=query_planner,
            retriever_name=retriever,
            weakness_generator=weakness_generator,
            weakness_generator_name=weakness_generator_name,
            verifier=verifier,
            verifier_name=verifier_name,
        )
    )
    retrieval = {
        weakness_id: [
            {
                "block_id": item.block_id,
                "rank": item.rank,
                "score": item.score,
                "section_type": item.section_type,
                "retriever": item.retriever,
            }
            for item in candidates
        ]
        for weakness_id, candidates in state.retrieval.items()
    }
    return {
        "workflow": "deterministic_review_audit_v1",
        "graph_profile": graph_profile,
        "query_planner": query_planner,
        "retriever": retriever,
        "weakness_generator": weakness_generator_name,
        "verifier": verifier_name,
        "weaknesses": [item.to_dict() for item in state.weaknesses],
        "generation_metadata": state.generation_metadata,
        "query_plan": state.query_plan,
        "weakness_count": len(state.weaknesses),
        "evidence_block_count": len(blocks),
        "retrieval": retrieval,
        "verification": {key: value.to_dict() for key, value in state.verification.items()},
        "deduplication": {
            "candidate_count": len(state.weaknesses),
            "deduplicated_count": len(state.deduplicated_weaknesses or state.weaknesses),
            "duplicate_count": len(state.duplicate_of),
            "duplicate_of": state.duplicate_of,
        },
        "ranked_findings": [item.to_dict() for item in state.ranked_findings],
        "agent_trace": state.agent_trace,
        "metric_boundary": "silver diagnostic",
    }
