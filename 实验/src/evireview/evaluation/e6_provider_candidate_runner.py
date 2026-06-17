from collections import Counter
from typing import Any

from evireview.evaluation.end_to_end_report_runner import (
    _max_token_overlap,
    _official_weakness_texts,
)


ALLOWED_ASPECTS = {
    "experiment",
    "method",
    "missing_baseline",
    "novelty",
    "related_work",
    "reproducibility",
}


def run_provider_candidate_experiment(
    *,
    e6_result: dict,
    diagnostics: dict,
    submissions: list[dict],
    provider: Any,
    limit: int = 8,
    top_k: int = 3,
) -> dict:
    selected_paper_ids = [item["paper_id"] for item in diagnostics["failure_cases"][:limit]]
    submissions_by_id = {submission["paper_id"]: submission for submission in submissions}
    selected = [submissions_by_id[paper_id] for paper_id in selected_paper_ids if paper_id in submissions_by_id]
    gold_by_paper = {
        submission["paper_id"]: _official_weakness_texts(submission) for submission in selected
    }
    b2_reports = _filter_reports(e6_result["system_generated_reports"], selected_paper_ids)
    b3_reports = _filter_reports(e6_result["cue_aware_reports"], selected_paper_ids)
    provider_reports = []
    integrity = Counter()
    costs = Counter()
    for submission in selected:
        report, usage = _provider_report(submission, provider, top_k, integrity)
        provider_reports.append(report)
        costs.update(usage)
    b2_metrics = _slice_metrics(b2_reports, gold_by_paper, top_k)
    b3_metrics = _slice_metrics(b3_reports, gold_by_paper, top_k)
    provider_metrics = _slice_metrics(provider_reports, gold_by_paper, top_k)
    evaluated = len(selected)
    provider_metrics["tokens_per_paper"] = (
        costs["total_tokens"] / evaluated if evaluated else 0.0
    )
    provider_metrics["latency_ms_per_paper"] = (
        costs["latency_ms"] / evaluated if evaluated else 0.0
    )
    return {
        "protocol": {
            "name": "e6-provider-candidate-failure-slice-v1",
            "provider_backed": True,
            "model": provider.model,
            "selection": "e6_candidate_diagnostics_failure_cases",
            "limit": limit,
            "top_k": top_k,
            "prompt_input_boundary": "paper_metadata_and_b3_candidates_only_no_official_reviews",
            "gold_usage": "offline_proxy_evaluation_only",
            "accept_reject_decision": False,
        },
        "dataset": {
            "selected_papers": evaluated,
            "openreview_reviews_in_selected_papers": sum(
                len(submission.get("reviews", [])) for submission in selected
            ),
            "source_openreview_papers": len(submissions),
        },
        "systems": {
            "B2_failure_slice": b2_metrics,
            "B3_failure_slice": b3_metrics,
            "P1_provider_generated_failure_slice": provider_metrics,
        },
        "comparison": {
            "p1_minus_b3_proxy_overlap_delta": (
                provider_metrics["official_weakness_proxy_overlap@k"]
                - b3_metrics["official_weakness_proxy_overlap@k"]
            ),
            "p1_minus_b2_proxy_overlap_delta": (
                provider_metrics["official_weakness_proxy_overlap@k"]
                - b2_metrics["official_weakness_proxy_overlap@k"]
            ),
            "p1_improved_over_b3_papers": _paper_improvements(
                provider_reports,
                b3_reports,
                gold_by_paper,
            ),
        },
        "integrity": {
            "provider_failures": integrity["provider_failures"],
            "invalid_citations": integrity["invalid_citations"],
            "cited_evidence_ids": integrity["cited_evidence_ids"],
            "evidence_attribution_accuracy": (
                1 - integrity["invalid_citations"] / integrity["cited_evidence_ids"]
                if integrity["cited_evidence_ids"]
                else 1.0
            ),
            "failure_reasons": {
                key.removeprefix("failure_reason:"): value
                for key, value in integrity.items()
                if key.startswith("failure_reason:")
            },
        },
        "provider_reports": provider_reports,
    }


def _provider_report(submission: dict, provider: Any, top_k: int, integrity: Counter):
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    evidence = _metadata_evidence(paper_id, content)
    allowed = {item["evidence_id"] for item in evidence}
    payload = {
        "paper": {
            "paper_id": paper_id,
            "title": content.get("title", paper_id),
            "abstract": content.get("abstract", "")[:3500],
            "keywords": content.get("keywords", []),
            "primary_area": content.get("primary_area", ""),
        },
        "evidence": evidence,
        "allowed_aspects": sorted(ALLOWED_ASPECTS),
        "top_k": top_k,
        "task": "Generate major weakness candidates for an automatic paper review report. Do not include accept/reject decisions.",
    }
    try:
        result = provider.complete_json("generate_review_candidates", payload)
        raw_candidates = result.data.get("candidates", [])
        if not isinstance(raw_candidates, list):
            raise ValueError("provider candidates must be a list")
        candidates = [
            _sanitize_candidate(
                paper_id,
                index,
                item,
                allowed,
                integrity,
            )
            for index, item in enumerate(raw_candidates[:top_k])
            if isinstance(item, dict)
        ]
        usage = Counter(result.usage)
        usage["latency_ms"] += result.latency_ms
    except Exception as error:
        integrity["provider_failures"] += 1
        integrity[f"failure_reason:{type(error).__name__}"] += 1
        candidates = []
        usage = Counter()
    return {
        "paper_id": paper_id,
        "title": content.get("title", paper_id),
        "decision": "not_applicable",
        "trace_policy": "paper_metadata_to_provider_generated_topk",
        "candidate_source": f"provider:{provider.model}",
        "top_weaknesses": candidates,
        "candidate_count": len(candidates),
        "review_count": len(submission.get("reviews", [])),
    }, usage


def _sanitize_candidate(
    paper_id: str,
    index: int,
    item: dict,
    allowed: set[str],
    integrity: Counter,
) -> dict:
    raw_citations = item.get("evidence_ids", [])
    if not isinstance(raw_citations, list):
        raw_citations = []
    cited = [str(evidence_id) for evidence_id in raw_citations if str(evidence_id) in allowed]
    integrity["cited_evidence_ids"] += len(raw_citations)
    integrity["invalid_citations"] += len(raw_citations) - len(cited)
    aspect = str(item.get("aspect", "experiment")).strip().lower()
    if aspect not in ALLOWED_ASPECTS:
        aspect = "experiment"
    severity = str(item.get("severity", "major")).strip().lower()
    if severity not in {"major", "minor"}:
        severity = "major"
    confidence = _bounded_float(item.get("confidence", 0.0), 0.0, 1.0)
    return {
        "candidate_id": f"{paper_id}:provider:{index}",
        "paper_id": paper_id,
        "aspect": aspect,
        "target": str(item.get("target", ""))[:240],
        "weakness": str(item.get("weakness", "")).strip(),
        "severity": severity,
        "suggestion": str(item.get("suggestion", "")).strip(),
        "source_agent": "provider_generated_candidate_v1",
        "evidence_ids": cited,
        "confidence": confidence,
        "rank_score": _rank_score(aspect, severity, confidence),
        "source_review_id": None,
    }


def _rank_score(aspect: str, severity: str, confidence: float) -> float:
    score = confidence + (0.25 if severity == "major" else 0.05)
    if aspect in {"experiment", "missing_baseline", "method"}:
        score += 0.1
    return round(score, 6)


def _metadata_evidence(paper_id: str, content: dict) -> list[dict]:
    evidence = []
    for field in ("title", "abstract", "keywords", "primary_area"):
        value = content.get(field)
        if value:
            evidence.append(
                {
                    "evidence_id": f"{paper_id}:content:{field}",
                    "field": field,
                    "text": value if isinstance(value, str) else ", ".join(map(str, value)),
                }
            )
    return evidence or [
        {
            "evidence_id": f"{paper_id}:content:metadata",
            "field": "metadata",
            "text": content.get("title", paper_id),
        }
    ]


def _filter_reports(reports: list[dict], paper_ids: list[str]) -> list[dict]:
    selected = set(paper_ids)
    return [report for report in reports if report["paper_id"] in selected]


def _slice_metrics(reports: list[dict], gold_by_paper: dict[str, list[str]], top_k: int) -> dict:
    candidate_scores = []
    paper_scores = []
    aspects = Counter()
    invalid_top_k = 0
    traceable = 0
    total = 0
    for report in reports:
        items = report["top_weaknesses"]
        invalid_top_k += len(items) > top_k
        item_scores = []
        for item in items:
            total += 1
            traceable += bool(item.get("evidence_ids"))
            aspects[item.get("aspect", "unknown")] += 1
            score = _max_token_overlap(item.get("weakness", ""), gold_by_paper.get(report["paper_id"], []))
            candidate_scores.append(score)
            item_scores.append(score)
        paper_scores.append(_mean(item_scores))
    return {
        "paper_report_coverage": sum(bool(report["top_weaknesses"]) for report in reports) / len(reports)
        if reports
        else 0.0,
        "trace_coverage": traceable / total if total else 0.0,
        "top_k_compliance": 1 - invalid_top_k / len(reports) if reports else 0.0,
        "accept_reject_decisions": sum(report.get("decision") != "not_applicable" for report in reports),
        "review_leakage_free": _review_leakage_free(reports),
        "official_weakness_proxy_overlap@k": _mean(candidate_scores),
        "paper_proxy_overlap_mean": _mean(paper_scores),
        "zero_overlap_rate": sum(score == 0 for score in candidate_scores) / len(candidate_scores)
        if candidate_scores
        else 0.0,
        "aspect_distribution": dict(sorted(aspects.items())),
    }


def _paper_improvements(provider_reports: list[dict], baseline_reports: list[dict], gold_by_paper: dict[str, list[str]]) -> int:
    baseline_by_id = {report["paper_id"]: report for report in baseline_reports}
    improved = 0
    for report in provider_reports:
        baseline = baseline_by_id.get(report["paper_id"])
        if not baseline:
            continue
        provider_score = _report_score(report, gold_by_paper)
        baseline_score = _report_score(baseline, gold_by_paper)
        improved += provider_score > baseline_score
    return improved


def _report_score(report: dict, gold_by_paper: dict[str, list[str]]) -> float:
    scores = [
        _max_token_overlap(item.get("weakness", ""), gold_by_paper.get(report["paper_id"], []))
        for item in report["top_weaknesses"]
    ]
    return _mean(scores)


def _review_leakage_free(reports: list[dict]) -> bool:
    for report in reports:
        for item in report["top_weaknesses"]:
            if item.get("source_review_id") is not None:
                return False
            if "review" in " ".join(item.get("evidence_ids", [])).lower():
                return False
    return True


def _bounded_float(value, lower: float, upper: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = lower
    return max(lower, min(parsed, upper))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
