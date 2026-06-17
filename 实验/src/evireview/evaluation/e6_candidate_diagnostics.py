from collections import Counter, defaultdict

from evireview.evaluation.end_to_end_report_runner import (
    _max_token_overlap,
    _official_weakness_texts,
)


SYSTEM_REPORT_KEYS = {
    "B2_system_generated_structured_report": "system_generated_reports",
    "B3_cue_aware_structured_report": "cue_aware_reports",
}


def run_candidate_diagnostics(
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
    paper_deltas = _paper_deltas(
        system_profiles["B2_system_generated_structured_report"]["paper_scores"],
        system_profiles["B3_cue_aware_structured_report"]["paper_scores"],
    )
    failures = [item for item in paper_deltas if item["delta_b3_minus_b2"] <= 0]
    return {
        "protocol": {
            "name": "e6-candidate-diagnostics-v1",
            "source_experiment": e6_result["protocol"]["name"],
            "gold_usage": "diagnostic_only_official_review_weakness_proxy",
            "accept_reject_decision": False,
        },
        "dataset": {
            "openreview_papers": len(submissions),
            "openreview_reviews": sum(len(item.get("reviews", [])) for item in submissions),
        },
        "systems": {
            name: {
                "overall_proxy_overlap@k": profile["overall_proxy_overlap@k"],
                "aspect_distribution": profile["aspect_distribution"],
                "aspect_proxy_overlap@k": profile["aspect_proxy_overlap@k"],
                "zero_overlap_rate": profile["zero_overlap_rate"],
                "paper_score_mean": profile["paper_score_mean"],
                "paper_score_median": profile["paper_score_median"],
            }
            for name, profile in system_profiles.items()
        },
        "comparison": {
            "b3_minus_b2_mean_delta": _mean([item["delta_b3_minus_b2"] for item in paper_deltas]),
            "b3_improved_papers": sum(item["delta_b3_minus_b2"] > 0 for item in paper_deltas),
            "b3_tied_papers": sum(item["delta_b3_minus_b2"] == 0 for item in paper_deltas),
            "b3_regressed_papers": sum(item["delta_b3_minus_b2"] < 0 for item in paper_deltas),
            "failure_or_tie_rate": len(failures) / len(paper_deltas) if paper_deltas else 0.0,
        },
        "failure_cases": sorted(
            failures,
            key=lambda item: (item["delta_b3_minus_b2"], item["paper_id"]),
        )[:top_failure_count],
        "top_improvements": sorted(
            [item for item in paper_deltas if item["delta_b3_minus_b2"] > 0],
            key=lambda item: (-item["delta_b3_minus_b2"], item["paper_id"]),
        )[:top_failure_count],
        "next_optimization_hints": _optimization_hints(system_profiles, failures),
    }


def _profile_reports(reports: list[dict], gold_by_paper: dict[str, list[str]]) -> dict:
    candidate_rows = []
    aspect_counts = Counter()
    aspect_scores = defaultdict(list)
    paper_scores = {}
    for report in reports:
        paper_id = report["paper_id"]
        gold_texts = gold_by_paper.get(paper_id, [])
        item_scores = []
        for item in report["top_weaknesses"]:
            aspect = item.get("aspect", "unknown")
            score = _max_token_overlap(item["weakness"], gold_texts)
            candidate_rows.append(score)
            item_scores.append(score)
            aspect_counts[aspect] += 1
            aspect_scores[aspect].append(score)
        paper_scores[paper_id] = {
            "paper_id": paper_id,
            "title": report.get("title", paper_id),
            "proxy_overlap@k": _mean(item_scores),
            "top_aspects": [item.get("aspect", "unknown") for item in report["top_weaknesses"]],
            "top_weaknesses": [item["weakness"] for item in report["top_weaknesses"]],
        }
    return {
        "overall_proxy_overlap@k": _mean(candidate_rows),
        "aspect_distribution": dict(sorted(aspect_counts.items())),
        "aspect_proxy_overlap@k": {
            aspect: _mean(scores) for aspect, scores in sorted(aspect_scores.items())
        },
        "zero_overlap_rate": sum(score == 0 for score in candidate_rows) / len(candidate_rows)
        if candidate_rows
        else 0.0,
        "paper_score_mean": _mean([item["proxy_overlap@k"] for item in paper_scores.values()]),
        "paper_score_median": _median(
            [item["proxy_overlap@k"] for item in paper_scores.values()]
        ),
        "paper_scores": paper_scores,
    }


def _paper_deltas(b2_scores: dict[str, dict], b3_scores: dict[str, dict]) -> list[dict]:
    rows = []
    for paper_id in sorted(set(b2_scores) & set(b3_scores)):
        b2 = b2_scores[paper_id]
        b3 = b3_scores[paper_id]
        rows.append(
            {
                "paper_id": paper_id,
                "title": b3["title"],
                "b2_proxy_overlap@k": b2["proxy_overlap@k"],
                "b3_proxy_overlap@k": b3["proxy_overlap@k"],
                "delta_b3_minus_b2": b3["proxy_overlap@k"] - b2["proxy_overlap@k"],
                "b2_aspects": b2["top_aspects"],
                "b3_aspects": b3["top_aspects"],
                "b3_top_weaknesses": b3["top_weaknesses"],
            }
        )
    return rows


def _optimization_hints(system_profiles: dict, failures: list[dict]) -> list[str]:
    hints = []
    b3 = system_profiles["B3_cue_aware_structured_report"]
    aspect_scores = b3["aspect_proxy_overlap@k"]
    if aspect_scores:
        weakest_aspect = min(aspect_scores, key=aspect_scores.get)
        hints.append(
            f"Inspect low-overlap B3 aspect `{weakest_aspect}` before adding more templates."
        )
    if b3["zero_overlap_rate"] > 0:
        hints.append(
            "Reduce zero-overlap candidates by requiring at least one paper-title or abstract cue in every Top-K item."
        )
    if failures:
        hints.append(
            "Compare failure-case titles against B3 selected aspects before provider prompting; these cases define the first provider evaluation slice."
        )
    hints.append(
        "Keep provider-generated candidates leakage-free: prompts may include paper metadata and retrieved paper evidence, not Official Review text."
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
