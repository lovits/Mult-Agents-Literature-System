from __future__ import annotations

from evireview_core.domain.models import RankedFinding, VerificationResult
from evireview_core.ranking.evidence_aware import rank_weaknesses
from evireview_core.workflow.components import DEFAULT_COMPONENT_REGISTRY
from evireview_core.workflow.state import ReviewAuditState


def generate_or_import_weaknesses(state: ReviewAuditState) -> dict[str, object]:
    if state.weaknesses or state.weakness_generator is None:
        return {
            "mode": "imported",
            "weakness_generator": state.weakness_generator_name,
            "weakness_count": len(state.weaknesses),
        }
    result = state.weakness_generator(state)
    state.weaknesses = result.weaknesses
    state.generation_metadata = result.metadata
    return {
        "mode": "generated",
        "weakness_generator": state.weakness_generator_name,
        "weakness_count": len(state.weaknesses),
    }


def plan_weakness_queries(state: ReviewAuditState) -> dict[str, object]:
    planner = DEFAULT_COMPONENT_REGISTRY.query_planner(state.query_planner_name)
    state.query_plan = {weakness.weakness_id: planner(weakness) for weakness in state.weaknesses}
    return {"query_planner": state.query_planner_name, "query_count": len(state.query_plan)}


def retrieve_evidence(state: ReviewAuditState) -> dict[str, object]:
    retriever = DEFAULT_COMPONENT_REGISTRY.retriever(state.retriever_name)
    state.retrieval = {
        weakness.weakness_id: retriever(
            weakness,
            state.query_plan.get(weakness.weakness_id, weakness.weakness_text),
            state.evidence_blocks,
            state.top_k,
        )
        for weakness in state.weaknesses
    }
    return {"retriever": state.retriever_name, "retrieval_count": len(state.retrieval)}


def verify_weaknesses(state: ReviewAuditState) -> dict[str, object]:
    verifier = state.verifier or DEFAULT_COMPONENT_REGISTRY.verifier(state.verifier_name)
    state.verification = {
        weakness.weakness_id: verifier(weakness, state.retrieval.get(weakness.weakness_id, []))
        for weakness in state.weaknesses
    }
    return {"verifier": state.verifier_name, "verification_count": len(state.verification)}


def assume_supported(state: ReviewAuditState) -> dict[str, object]:
    state.verification = {
        weakness.weakness_id: VerificationResult(
            weakness_id=weakness.weakness_id,
            label="Supported",
            support_score=1.0,
            evidence_block_ids=tuple(item.block_id for item in state.retrieval.get(weakness.weakness_id, [])[:3]),
            rationale="Ablation profile bypassed evidence verification.",
            verifier="no_verifier_ablation",
        )
        for weakness in state.weaknesses
    }
    return {"ablation": "no_verifier"}


def rank_findings(state: ReviewAuditState) -> None:
    state.ranked_findings = rank_weaknesses(state.weaknesses, state.verification, top_k=state.finding_top_k)


def preserve_candidate_order(state: ReviewAuditState) -> dict[str, object]:
    state.ranked_findings = [
        RankedFinding(
            weakness_id=weakness.weakness_id,
            rank=rank,
            rank_score=0.0,
            label=state.verification[weakness.weakness_id].label,
        )
        for rank, weakness in enumerate(state.weaknesses[: state.finding_top_k], start=1)
        if weakness.weakness_id in state.verification
    ]
    return {"ablation": "no_ranker"}
