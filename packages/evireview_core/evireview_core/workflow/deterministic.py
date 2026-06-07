from __future__ import annotations

from typing import Any

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.workflow.graph import ReviewAuditGraph
from evireview_core.workflow.state import ReviewAuditState


def run_deterministic_review_audit(
    weaknesses: list[Weakness],
    blocks: list[EvidenceBlock],
    top_k: int = 5,
    finding_top_k: int = 3,
    graph_profile: str = "full",
    query_planner: str = "direct",
    retriever: str = "hierarchical",
) -> dict[str, Any]:
    state = ReviewAuditGraph(graph_profile).run(
        ReviewAuditState(
            weaknesses=weaknesses,
            evidence_blocks=blocks,
            top_k=top_k,
            finding_top_k=finding_top_k,
            query_planner_name=query_planner,
            retriever_name=retriever,
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
        "query_plan": state.query_plan,
        "weakness_count": len(weaknesses),
        "evidence_block_count": len(blocks),
        "retrieval": retrieval,
        "verification": {key: value.to_dict() for key, value in state.verification.items()},
        "ranked_findings": [item.to_dict() for item in state.ranked_findings],
        "agent_trace": state.agent_trace,
        "metric_boundary": "silver diagnostic",
    }
