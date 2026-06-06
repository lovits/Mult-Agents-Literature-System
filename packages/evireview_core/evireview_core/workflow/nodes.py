from __future__ import annotations

from evireview_core.ranking.evidence_aware import rank_weaknesses
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.verification.heuristic import verify_with_heuristics
from evireview_core.workflow.state import ReviewAuditState


def generate_or_import_weaknesses(state: ReviewAuditState) -> dict[str, object]:
    if state.weaknesses or state.weakness_generator is None:
        return {"mode": "imported", "weakness_count": len(state.weaknesses)}
    result = state.weakness_generator(state)
    state.weaknesses = result.weaknesses
    state.generation_metadata = result.metadata
    return {"mode": "generated", "weakness_count": len(state.weaknesses)}


def retrieve_evidence(state: ReviewAuditState) -> None:
    state.retrieval = {
        weakness.weakness_id: hierarchical_search(weakness, state.evidence_blocks, top_k=state.top_k)
        for weakness in state.weaknesses
    }


def verify_weaknesses(state: ReviewAuditState) -> None:
    state.verification = {
        weakness.weakness_id: verify_with_heuristics(weakness, state.retrieval.get(weakness.weakness_id, []))
        for weakness in state.weaknesses
    }


def rank_findings(state: ReviewAuditState) -> None:
    state.ranked_findings = rank_weaknesses(state.weaknesses, state.verification, top_k=state.finding_top_k)
