from collections import Counter, defaultdict

from evireview.evaluation.end_to_end_report_runner import (
    _max_token_overlap,
    _official_weakness_texts,
)


SYSTEM_REPORT_KEYS = {
    "B3_cue_aware_structured_report": "cue_aware_reports",
    "B4_agent_rag_pipeline_report": "agent_rag_reports",
    "B5_balanced_agent_rag_pipeline_report": "balanced_agent_rag_reports",
}


def run_b5_diagnostics(
    e6_result: dict,
    submissions: list[dict],
    *,
    top_failure_count: int = 8,
) -> dict:
    gold_by_paper = {
        submission["paper_id"]: _official_weakness_texts(submission) for submission in submissions
    }
    system_profiles = {
        system_name: _profile_reports(e6_result[report_key], gold_by_paper)
        for system_name, report_key in SYSTEM_REPORT_KEYS.items()
    }
    b3_scores = system_profiles["B3_cue_aware_structured_report"]["paper_scores"]
    b4_scores = system_profiles["B4_agent_rag_pipeline_report"]["paper_scores"]
    b5_scores = system_profiles["B5_balanced_agent_rag_pipeline_report"]["paper_scores"]
    b5_vs_b4 = _paper_deltas(b4_scores, b5_scores, "b4", "b5")
    b5_vs_b3 = _paper_deltas(b3_scores, b5_scores, "b3", "b5")
    b5_profile = system_profiles["B5_balanced_agent_rag_pipeline_report"]
    return {
        "protocol": {
            "name": "e6-b5-balanced-agent-rag-diagnostics-v1",
            "source_experiment": e6_result["protocol"]["name"],
            "gold_usage": "diagnostic_only_official_review_weakness_proxy",
            "accept_reject_decision": False,
        },
        "dataset": {
            "openreview_papers": len(submissions),
            "openreview_reviews": sum(len(item.get("reviews", [])) for item in submissions),
        },
        "systems": {
            name: _public_profile(profile) for name, profile in system_profiles.items()
        },
        "comparison": {
            **_delta_summary(b5_vs_b4, "b5", "b4"),
            **_delta_summary(b5_vs_b3, "b5", "b3"),
        },
        "aspect_bottlenecks": _aspect_bottlenecks(b5_profile, limit=top_failure_count),
        "low_overlap_cases": _low_overlap_cases(b5_scores, limit=top_failure_count),
        "regression_vs_b4_cases": [
            item
            for item in sorted(
                b5_vs_b4,
                key=lambda row: (row["delta_b5_minus_b4"], row["paper_id"]),
            )
            if item["delta_b5_minus_b4"] < 0
        ][:top_failure_count],
        "top_improvements_vs_b4": [
            item
            for item in sorted(
                b5_vs_b4,
                key=lambda row: (-row["delta_b5_minus_b4"], row["paper_id"]),
            )
            if item["delta_b5_minus_b4"] > 0
        ][:top_failure_count],
        "next_optimization_hints": _optimization_hints(b5_profile, b5_vs_b4),
    }


def _profile_reports(reports: list[dict], gold_by_paper: dict[str, list[str]]) -> dict:
    candidate_scores = []
    aspect_counts = Counter()
    aspect_scores = defaultdict(list)
    audit_decisions = Counter()
    support_strengths = []
    refutation_strengths = []
    paper_scores = {}
    for report in reports:
        paper_id = report["paper_id"]
        gold_texts = gold_by_paper.get(paper_id, [])
        item_scores = []
        items = report["top_weaknesses"]
        for item in items:
            aspect = item.get("aspect", "unknown")
            score = _max_token_overlap(item["weakness"], gold_texts)
            candidate_scores.append(score)
            item_scores.append(score)
            aspect_counts[aspect] += 1
            aspect_scores[aspect].append(score)
            if "audit_decision" in item:
                audit_decisions[item["audit_decision"]] += 1
            if "support_strength" in item:
                support_strengths.append(float(item["support_strength"]))
            if "refutation_strength" in item:
                refutation_strengths.append(float(item["refutation_strength"]))
        paper_scores[paper_id] = {
            "paper_id": paper_id,
            "title": report.get("title", paper_id),
            "proxy_overlap@k": _mean(item_scores),
            "top_aspects": [item.get("aspect", "unknown") for item in items],
            "top_weaknesses": [item["weakness"] for item in items],
            "audit_decisions": [
                item.get("audit_decision", "n/a") for item in items if "audit_decision" in item
            ],
            "support_strength_mean": _mean(
                [float(item["support_strength"]) for item in items if "support_strength" in item]
            ),
            "refutation_strength_mean": _mean(
                [
                    float(item["refutation_strength"])
                    for item in items
                    if "refutation_strength" in item
                ]
            ),
        }
    return {
        "overall_proxy_overlap@k": _mean(candidate_scores),
        "aspect_distribution": dict(sorted(aspect_counts.items())),
        "aspect_proxy_overlap@k": {
            aspect: _mean(scores) for aspect, scores in sorted(aspect_scores.items())
        },
        "zero_overlap_rate": sum(score == 0 for score in candidate_scores)
        / len(candidate_scores)
        if candidate_scores
        else 0.0,
        "paper_score_mean": _mean([item["proxy_overlap@k"] for item in paper_scores.values()]),
        "paper_score_median": _median(
            [item["proxy_overlap@k"] for item in paper_scores.values()]
        ),
        "audit_decision_distribution": dict(sorted(audit_decisions.items())),
        "support_strength_mean": _mean(support_strengths),
        "refutation_strength_mean": _mean(refutation_strengths),
        "paper_scores": paper_scores,
    }


def _public_profile(profile: dict) -> dict:
    fields = [
        "overall_proxy_overlap@k",
        "aspect_distribution",
        "aspect_proxy_overlap@k",
        "zero_overlap_rate",
        "paper_score_mean",
        "paper_score_median",
        "audit_decision_distribution",
        "support_strength_mean",
        "refutation_strength_mean",
    ]
    return {field: profile[field] for field in fields if field in profile}


def _paper_deltas(
    baseline_scores: dict[str, dict],
    candidate_scores: dict[str, dict],
    baseline_label: str,
    candidate_label: str,
) -> list[dict]:
    rows = []
    for paper_id in sorted(set(baseline_scores) & set(candidate_scores)):
        baseline = baseline_scores[paper_id]
        candidate = candidate_scores[paper_id]
        rows.append(
            {
                "paper_id": paper_id,
                "title": candidate["title"],
                f"{baseline_label}_proxy_overlap@k": baseline["proxy_overlap@k"],
                f"{candidate_label}_proxy_overlap@k": candidate["proxy_overlap@k"],
                f"delta_{candidate_label}_minus_{baseline_label}": (
                    candidate["proxy_overlap@k"] - baseline["proxy_overlap@k"]
                ),
                f"{baseline_label}_aspects": baseline["top_aspects"],
                f"{candidate_label}_aspects": candidate["top_aspects"],
                f"{candidate_label}_top_weaknesses": candidate["top_weaknesses"],
                f"{candidate_label}_audit_decisions": candidate["audit_decisions"],
                f"{candidate_label}_support_strength_mean": candidate[
                    "support_strength_mean"
                ],
                f"{candidate_label}_refutation_strength_mean": candidate[
                    "refutation_strength_mean"
                ],
            }
        )
    return rows


def _delta_summary(rows: list[dict], candidate_label: str, baseline_label: str) -> dict:
    delta_key = f"delta_{candidate_label}_minus_{baseline_label}"
    return {
        f"{candidate_label}_minus_{baseline_label}_mean_delta": _mean(
            [item[delta_key] for item in rows]
        ),
        f"{candidate_label}_improved_vs_{baseline_label}_papers": sum(
            item[delta_key] > 0 for item in rows
        ),
        f"{candidate_label}_tied_vs_{baseline_label}_papers": sum(
            item[delta_key] == 0 for item in rows
        ),
        f"{candidate_label}_regressed_vs_{baseline_label}_papers": sum(
            item[delta_key] < 0 for item in rows
        ),
    }


def _aspect_bottlenecks(profile: dict, *, limit: int) -> list[dict]:
    rows = []
    for aspect, score in profile["aspect_proxy_overlap@k"].items():
        rows.append(
            {
                "aspect": aspect,
                "count": profile["aspect_distribution"].get(aspect, 0),
                "proxy_overlap@k": score,
            }
        )
    return sorted(rows, key=lambda item: (item["proxy_overlap@k"], -item["count"], item["aspect"]))[
        :limit
    ]


def _low_overlap_cases(paper_scores: dict[str, dict], *, limit: int) -> list[dict]:
    return [
        {
            "paper_id": item["paper_id"],
            "title": item["title"],
            "b5_proxy_overlap@k": item["proxy_overlap@k"],
            "b5_aspects": item["top_aspects"],
            "b5_audit_decisions": item["audit_decisions"],
            "b5_support_strength_mean": item["support_strength_mean"],
            "b5_refutation_strength_mean": item["refutation_strength_mean"],
            "b5_top_weaknesses": item["top_weaknesses"],
        }
        for item in sorted(
            paper_scores.values(),
            key=lambda row: (row["proxy_overlap@k"], row["paper_id"]),
        )[:limit]
    ]


def _optimization_hints(b5_profile: dict, b5_vs_b4: list[dict]) -> list[str]:
    hints = []
    bottlenecks = _aspect_bottlenecks(b5_profile, limit=2)
    if bottlenecks:
        aspects = ", ".join(item["aspect"] for item in bottlenecks)
        hints.append(
            f"Inspect B5 low-overlap aspect slices first: {aspects}."
        )
    regressed = [item for item in b5_vs_b4 if item["delta_b5_minus_b4"] < 0]
    if regressed:
        hints.append(
            "Compare B5 regressions against B4 selected aspects before changing candidate templates."
        )
    if b5_profile["zero_overlap_rate"] > 0:
        hints.append(
            "For zero-overlap B5 items, require candidate weaknesses to include at least one paper-local cue or literature cue."
        )
    hints.append(
        "Keep the next optimization bounded: change candidate filtering or aspect-specific query planning, not provider prompts."
    )
    return hints


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
