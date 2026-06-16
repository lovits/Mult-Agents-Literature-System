import re

from evireview.agent.candidate_generator import (
    GENERATOR_NAME,
    generate_candidate_weaknesses,
)


def run_end_to_end_report_baseline(
    submissions: list[dict],
    arxiv_papers: list[dict],
    component_metrics: dict,
    *,
    top_k: int = 3,
) -> dict:
    reports = [_review_derived_report(submission, top_k) for submission in submissions]
    generated_reports = [_system_generated_report(submission, top_k) for submission in submissions]
    baseline = _baseline_metrics(submissions)
    structured = _structured_metrics(reports, top_k)
    generated = _system_generated_metrics(generated_reports, submissions, top_k)
    return {
        "protocol": {
            "name": "e6-end-to-end-structured-report-v1",
            "top_k": top_k,
            "accept_reject_decision": False,
            "arxiv_unseen_gold_metrics": False,
            "system_candidate_generation": GENERATOR_NAME,
            "uses_component_outputs": ["E2", "E3", "E4", "E5"],
            "component_status": {
                name.upper(): metrics.get("status", "available")
                for name, metrics in component_metrics.items()
            },
        },
        "dataset": {
            "openreview_papers": len(submissions),
            "openreview_reviews": sum(len(item.get("reviews", [])) for item in submissions),
            "arxiv_unseen_papers": len(arxiv_papers),
        },
        "systems": {
            "B0_unstructured_review_dump": baseline,
            "B1_structured_evidence_report": structured,
            "B2_system_generated_structured_report": generated,
        },
        "openreview_reports": reports,
        "system_generated_reports": generated_reports,
        "unseen_demo": {
            "papers": len(arxiv_papers),
            "gold_metrics_reported": False,
            "items": [
                {
                    "paper_id": paper.get("arxiv_id"),
                    "title": paper.get("title", ""),
                    "published": paper.get("published"),
                    "local_pdf": paper.get("local_pdf"),
                    "demo_boundary": "unseen_demo_only_no_gold_metrics",
                }
                for paper in arxiv_papers
            ],
        },
    }


def _review_derived_report(submission: dict, top_k: int) -> dict:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    candidates = _review_candidate_weaknesses(submission)
    ranked = sorted(candidates, key=lambda item: (-item["rank_score"], item["candidate_id"]))
    top = ranked[:top_k]
    return {
        "paper_id": paper_id,
        "title": content.get("title", paper_id),
        "summary": _summary(content),
        "decision": "not_applicable",
        "trace_policy": "review_weakness_to_structured_topk_with_source_review_ids",
        "candidate_source": "official_review_weakness_upper_bound",
        "top_weaknesses": top,
        "candidate_count": len(candidates),
        "review_count": len(submission.get("reviews", [])),
    }


def _system_generated_report(submission: dict, top_k: int) -> dict:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    candidates = generate_candidate_weaknesses(submission)
    top = candidates[:top_k]
    return {
        "paper_id": paper_id,
        "title": content.get("title", paper_id),
        "summary": _summary(content),
        "decision": "not_applicable",
        "trace_policy": "paper_content_to_system_generated_topk",
        "candidate_source": GENERATOR_NAME,
        "top_weaknesses": top,
        "candidate_count": len(candidates),
        "review_count": len(submission.get("reviews", [])),
    }


def _review_candidate_weaknesses(submission: dict) -> list[dict]:
    paper_id = submission["paper_id"]
    candidates = []
    for review_index, review in enumerate(submission.get("reviews", [])):
        review_id = review.get("id", f"review-{review_index}")
        content = review.get("content", {})
        for weakness_index, weakness in enumerate(_split_weaknesses(content.get("weaknesses", ""))):
            candidate_id = f"{paper_id}:{review_id}:{weakness_index}"
            evidence_ids = [f"{paper_id}:{review_id}:weaknesses"]
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "weakness": weakness,
                    "evidence_ids": evidence_ids,
                    "confidence": _confidence(content),
                    "rank_score": _rank_score(weakness, content),
                    "source_review_id": review_id,
                    "rating": content.get("rating"),
                    "reviewer_confidence": content.get("confidence"),
                }
            )
    if not candidates:
        candidates.append(
            {
                "candidate_id": f"{paper_id}:no-review-weakness:0",
                "weakness": "No explicit weakness text is available in the OpenReview seed record.",
                "evidence_ids": [f"{paper_id}:metadata"],
                "confidence": 0.0,
                "rank_score": 0.0,
                "source_review_id": None,
                "rating": None,
                "reviewer_confidence": None,
            }
        )
    return candidates


def _split_weaknesses(text: str) -> list[str]:
    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip(" -\t")]
    if len(lines) > 1:
        return lines
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _rank_score(weakness: str, review_content: dict) -> float:
    lowered = weakness.lower()
    severity_terms = sum(
        term in lowered
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
            "theory",
            "unclear",
        )
    )
    action_terms = sum(
        term in lowered
        for term in ("should", "need", "needs", "provide", "add", "compare", "clarify", "include")
    )
    rating_penalty = max(0.0, 8 - float(review_content.get("rating", 5) or 5)) * 0.05
    specificity = min(len(_tokens(weakness)) / 70, 1.0)
    return 0.28 * severity_terms + 0.18 * action_terms + 0.28 * specificity + rating_penalty


def _confidence(review_content: dict) -> float:
    raw = review_content.get("confidence", 0)
    try:
        return max(0.0, min(float(raw) / 5, 1.0))
    except (TypeError, ValueError):
        return 0.0


def _summary(content: dict) -> str:
    abstract = content.get("abstract", "")
    if not abstract:
        return "No abstract available in the OpenReview seed metadata."
    return abstract[:360] + ("..." if len(abstract) > 360 else "")


def _baseline_metrics(submissions: list[dict]) -> dict:
    return {
        "paper_report_coverage": 1.0 if submissions else 0.0,
        "trace_coverage": 0.0,
        "top_k_compliance": 0.0,
        "accept_reject_decisions": 0,
    }


def _structured_metrics(reports: list[dict], top_k: int) -> dict:
    if not reports:
        return {
            "paper_report_coverage": 0.0,
            "trace_coverage": 0.0,
            "top_k_compliance": 0.0,
            "accept_reject_decisions": 0,
        }
    return {
        "paper_report_coverage": sum(bool(report["top_weaknesses"]) for report in reports) / len(reports),
        "trace_coverage": _trace_coverage(reports),
        "top_k_compliance": sum(len(report["top_weaknesses"]) <= top_k for report in reports) / len(reports),
        "accept_reject_decisions": sum(report["decision"] != "not_applicable" for report in reports),
    }


def _system_generated_metrics(
    reports: list[dict],
    submissions: list[dict],
    top_k: int,
) -> dict:
    metrics = _structured_metrics(reports, top_k)
    metrics["review_leakage_free"] = _review_leakage_free(reports)
    metrics["official_weakness_proxy_overlap@k"] = _official_weakness_proxy_overlap(
        reports,
        submissions,
    )
    return metrics


def _trace_coverage(reports: list[dict]) -> float:
    items = [item for report in reports for item in report["top_weaknesses"]]
    return sum(bool(item.get("evidence_ids")) for item in items) / len(items) if items else 0.0


def _review_leakage_free(reports: list[dict]) -> bool:
    for report in reports:
        for item in report["top_weaknesses"]:
            if item.get("source_review_id") is not None:
                return False
            if "review" in " ".join(item.get("evidence_ids", [])).lower():
                return False
    return True


def _official_weakness_proxy_overlap(reports: list[dict], submissions: list[dict]) -> float:
    gold_by_paper = {
        submission["paper_id"]: _official_weakness_texts(submission) for submission in submissions
    }
    scored = []
    for report in reports:
        gold_texts = gold_by_paper.get(report["paper_id"], [])
        for item in report["top_weaknesses"]:
            scored.append(_max_token_overlap(item["weakness"], gold_texts))
    return sum(scored) / len(scored) if scored else 0.0


def _official_weakness_texts(submission: dict) -> list[str]:
    texts = []
    for review in submission.get("reviews", []):
        content = review.get("content", {})
        texts.extend(_split_weaknesses(content.get("weaknesses", "")))
    return texts


def _max_token_overlap(candidate: str, references: list[str]) -> float:
    candidate_tokens = set(_tokens(candidate)) - _STOPWORDS
    if not candidate_tokens:
        return 0.0
    best = 0.0
    for reference in references:
        reference_tokens = set(_tokens(reference)) - _STOPWORDS
        if not reference_tokens:
            continue
        best = max(best, len(candidate_tokens & reference_tokens) / len(candidate_tokens | reference_tokens))
    return best


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "may",
    "of",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}
