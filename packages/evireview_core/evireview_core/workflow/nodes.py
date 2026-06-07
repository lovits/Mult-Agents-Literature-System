from __future__ import annotations

from evireview_core.deduplication.lexical import deduplicate_weaknesses as apply_deduplication
from evireview_core.classification.auxiliary import classify_auxiliary_decision as classify_decision
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
    retriever = state.runtime_retriever or DEFAULT_COMPONENT_REGISTRY.retriever(state.retriever_name)
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


def deduplicate_weaknesses(state: ReviewAuditState) -> dict[str, object]:
    result = apply_deduplication(state.weaknesses, state.verification)
    state.deduplicated_weaknesses = result.weaknesses
    state.duplicate_of = result.duplicate_of
    return {
        "candidate_count": len(state.weaknesses),
        "deduplicated_count": len(state.deduplicated_weaknesses),
        "duplicate_count": len(state.duplicate_of),
    }


def skip_deduplication(state: ReviewAuditState) -> dict[str, object]:
    state.deduplicated_weaknesses = list(state.weaknesses)
    state.duplicate_of = {}
    return {"ablation": "no_dedup", "candidate_count": len(state.weaknesses)}


def rank_findings(state: ReviewAuditState) -> None:
    weaknesses = state.deduplicated_weaknesses or state.weaknesses
    state.ranked_findings = rank_weaknesses(weaknesses, state.verification, top_k=state.finding_top_k)


def preserve_candidate_order(state: ReviewAuditState) -> dict[str, object]:
    state.ranked_findings = [
        RankedFinding(
            weakness_id=weakness.weakness_id,
            rank=rank,
            rank_score=0.0,
            label=state.verification[weakness.weakness_id].label,
        )
        for rank, weakness in enumerate((state.deduplicated_weaknesses or state.weaknesses)[: state.finding_top_k], start=1)
        if weakness.weakness_id in state.verification
    ]
    return {"ablation": "no_ranker"}


def classify_auxiliary_decision(state: ReviewAuditState) -> dict[str, object]:
    weaknesses = state.deduplicated_weaknesses or state.weaknesses
    signal = classify_decision(weaknesses, state.verification)
    state.auxiliary_decision = signal.to_dict()
    return {
        "metric_boundary": signal.metric_boundary,
        "not_for_decision": signal.not_for_decision,
        "label": signal.label,
    }
