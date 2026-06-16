import math
import re
from collections import defaultdict

from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.label_mapping import claimcheck_agreement_to_decision


SYSTEM_NAMES = (
    "R0_input_order",
    "R1_text_severity",
    "R2_text_dedup",
    "R3_evidence_aware",
)
DECISION_WEIGHTS = {
    "keep": 0.35,
    "rewrite": 0.2,
    "uncertain": -0.05,
    "reject": -0.25,
}


def run_meta_reviewer_baselines(
    dataset: ClaimCheckDataset,
    audit_result: dict,
    substanreview_result: dict,
    literature_result: dict,
    *,
    top_k: int = 3,
) -> dict:
    examples = [example for example in dataset.examples if example.split == "main"]
    traces = {trace["example_id"]: trace for trace in audit_result.get("traces", [])}
    substan_prior = float(
        substanreview_result.get("evaluation", {}).get("substantiated_claim_rate", 0.0)
    )
    literature_metrics = literature_result.get("systems", {}).get(
        "L3_hybrid_metadata_filter", {}
    )
    literature_prior = (
        0.05
        if literature_metrics.get("citation_validity_rate", 0.0) >= 0.95
        and literature_metrics.get("future_leakage_count", 1) == 0
        else 0.0
    )
    rankings = {
        "R0_input_order": _rank_by_paper(
            examples,
            lambda example, index: -index,
            dedup=False,
        ),
        "R1_text_severity": _rank_by_paper(
            examples,
            lambda example, index: _text_rank_score(example),
            dedup=False,
        ),
        "R2_text_dedup": _rank_by_paper(
            examples,
            lambda example, index: _text_rank_score(example),
            dedup=True,
        ),
        "R3_evidence_aware": _rank_by_paper(
            examples,
            lambda example, index: _evidence_rank_score(
                example,
                traces.get(example.example_id, {}),
                substan_prior,
                literature_prior,
            ),
            dedup=True,
        ),
    }
    return {
        "protocol": {
            "name": "e5-meta-reviewer-ranker-v1",
            "top_k": top_k,
            "gold_used_only_for_metrics": True,
            "no_gold_severity_feature": True,
            "covered_refuted_gold": False,
            "uses_e4_audit_trace": True,
            "uses_substanreview_auxiliary": True,
            "uses_literature_rag_boundary": True,
        },
        "dataset": {
            "evaluated_candidates": len(examples),
            "paper_groups": len({example.paper_review_id for example in examples}),
            "gold_keep_candidates": sum(
                _gold_keep(example) for example in examples
            ),
        },
        "systems": {
            name: _evaluate_system(rankings[name], top_k)
            for name in SYSTEM_NAMES
        },
        "sample_rankings": {
            name: {
                paper_id: [item for item in ranked[:top_k]]
                for paper_id, ranked in rankings[name].items()
            }
            for name in SYSTEM_NAMES
        },
    }


def _rank_by_paper(examples, score_fn, *, dedup: bool) -> dict[str, list[dict]]:
    groups: dict[str, list[tuple[int, ClaimCheckWeakness]]] = defaultdict(list)
    for index, example in enumerate(examples):
        groups[example.paper_review_id].append((index, example))
    rankings = {}
    for paper_id, indexed in groups.items():
        scored = [
            _ranking_item(example, score_fn(example, index))
            for index, example in indexed
        ]
        scored.sort(key=lambda item: (-item["rank_score"], item["candidate_id"]))
        rankings[paper_id] = _deduplicate(scored) if dedup else scored
    return rankings


def _ranking_item(example: ClaimCheckWeakness, rank_score: float) -> dict:
    confidence = max(0.0, min(1.0, _sigmoid(rank_score)))
    return {
        "candidate_id": example.example_id,
        "paper_id": example.paper_review_id,
        "weakness": example.weakness,
        "rank_score": rank_score,
        "confidence": confidence,
        "gold_agreement_proxy": claimcheck_agreement_to_decision(example.agreement),
        "gold_high_agreement": example.agreement >= 4,
    }


def _deduplicate(items: list[dict], threshold: float = 0.48) -> list[dict]:
    selected = []
    deferred = []
    for item in items:
        redundancy = max(
            (_jaccard(item["weakness"], existing["weakness"]) for existing in selected),
            default=0.0,
        )
        if redundancy >= threshold:
            item = {**item, "rank_score": item["rank_score"] - redundancy}
            deferred.append(item)
        else:
            selected.append(item)
    reranked = selected + deferred
    reranked.sort(key=lambda item: (-item["rank_score"], item["candidate_id"]))
    return reranked


def _evaluate_system(rankings: dict[str, list[dict]], top_k: int) -> dict:
    precisions = []
    confidence_targets = []
    selected_keep = 0
    total_keep = 0
    selected_high_agreement = 0
    total_high_agreement = 0
    redundancy_rates = []
    for ranked in rankings.values():
        top = ranked[: min(top_k, len(ranked))]
        if not top:
            continue
        keep_flags = [item["gold_agreement_proxy"] == "keep" for item in top]
        precisions.append(sum(keep_flags) / len(top))
        all_keep = [item for item in ranked if item["gold_agreement_proxy"] == "keep"]
        all_high = [item for item in ranked if item["gold_high_agreement"]]
        selected_keep += sum(item["gold_agreement_proxy"] == "keep" for item in top)
        total_keep += len(all_keep)
        selected_high_agreement += sum(item["gold_high_agreement"] for item in top)
        total_high_agreement += len(all_high)
        confidence_targets.extend(
            (item["confidence"], float(item["gold_agreement_proxy"] == "keep"))
            for item in ranked
        )
        redundancy_rates.append(_redundancy_rate(top))
    return {
        "top_k_agreement_precision": (
            sum(precisions) / len(precisions) if precisions else 0.0
        ),
        "keep_coverage@k": selected_keep / total_keep if total_keep else 0.0,
        "high_agreement_coverage@k": (
            selected_high_agreement / total_high_agreement
            if total_high_agreement
            else 0.0
        ),
        "redundancy_rate": (
            sum(redundancy_rates) / len(redundancy_rates)
            if redundancy_rates
            else 0.0
        ),
        "confidence_brier": _brier(confidence_targets),
    }


def _text_rank_score(example: ClaimCheckWeakness) -> float:
    text = example.weakness.lower()
    tokens = _tokens(text)
    severity_terms = sum(
        term in text
        for term in (
            "lack",
            "missing",
            "no ",
            "not ",
            "fail",
            "baseline",
            "ablation",
            "experiment",
            "reproduc",
            "claim",
            "invalid",
            "unclear",
        )
    )
    action_terms = sum(
        term in text
        for term in ("should", "need", "needs", "provide", "add", "compare", "clarify", "include")
    )
    specificity = min(len(tokens) / 70, 1.0)
    number_or_citation = 0.15 if re.search(r"\d|table|figure|section", text) else 0.0
    return 0.24 * severity_terms + 0.35 * specificity + 0.16 * action_terms + number_or_citation


def _evidence_rank_score(
    example: ClaimCheckWeakness,
    trace: dict,
    substan_prior: float,
    literature_prior: float,
) -> float:
    base = _text_rank_score(example)
    support = trace.get("support", {})
    refutation = trace.get("refutation", {})
    decision = trace.get("A4_heuristic_smoke", {})
    evidence_count = len(decision.get("evidence_ids", []))
    external_bonus = literature_prior if _looks_external(example.weakness) else 0.0
    return (
        base
        + DECISION_WEIGHTS.get(decision.get("decision", "uncertain"), -0.05)
        + 0.2 * float(decision.get("confidence", 0.0))
        + 0.22 * float(support.get("strength", 0.0))
        - 0.12 * float(refutation.get("strength", 0.0))
        + 0.025 * min(evidence_count, 5)
        + 0.05 * substan_prior
        + external_bonus
    )


def _looks_external(text: str) -> bool:
    lowered = text.lower()
    return any(
        term in lowered
        for term in ("novel", "related work", "baseline", "compare", "comparison")
    )


def _gold_keep(example: ClaimCheckWeakness) -> bool:
    return claimcheck_agreement_to_decision(example.agreement) == "keep"


def _redundancy_rate(items: list[dict], threshold: float = 0.45) -> float:
    pairs = 0
    duplicates = 0
    for left in range(len(items)):
        for right in range(left + 1, len(items)):
            pairs += 1
            duplicates += _jaccard(items[left]["weakness"], items[right]["weakness"]) >= threshold
    return duplicates / pairs if pairs else 0.0


def _jaccard(left: str, right: str) -> float:
    left_tokens = set(_tokens(left))
    right_tokens = set(_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def _brier(pairs: list[tuple[float, float]]) -> float:
    return sum((confidence - target) ** 2 for confidence, target in pairs) / len(pairs) if pairs else 0.0
