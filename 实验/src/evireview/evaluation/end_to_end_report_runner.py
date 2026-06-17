import re

from evireview.agent.candidate_generator import (
    CUE_AWARE_GENERATOR_NAME,
    GENERATOR_NAME,
    generate_cue_aware_candidate_weaknesses,
    generate_candidate_weaknesses,
)
from evireview.system import AgentRAGReviewPipeline, ReviewPipelineRequest
from evireview.system.config import AgentRAGSystemConfig
from evireview.system.ranker import EvidenceAwareMetaRanker


AGENT_RAG_PIPELINE_NAME = "agent_rag_review_pipeline_v1"
BALANCED_AGENT_RAG_PIPELINE_NAME = "balanced_agent_rag_review_pipeline_v1"
BALANCED_CANDIDATE_PRIOR_WEIGHT = 0.03


def run_end_to_end_report_baseline(
    submissions: list[dict],
    arxiv_papers: list[dict],
    component_metrics: dict,
    *,
    top_k: int = 3,
) -> dict:
    reports = [_review_derived_report(submission, top_k) for submission in submissions]
    generated_reports = [_system_generated_report(submission, top_k) for submission in submissions]
    cue_aware_reports = [_cue_aware_report(submission, top_k) for submission in submissions]
    agent_rag_reports, balanced_agent_rag_reports = _agent_rag_pipeline_report_variants(
        submissions,
        top_k,
    )
    baseline = _baseline_metrics(submissions)
    structured = _structured_metrics(reports, top_k)
    generated = _system_generated_metrics(generated_reports, submissions, top_k)
    cue_aware = _cue_aware_metrics(cue_aware_reports, submissions, generated, top_k)
    agent_rag = _agent_rag_metrics(agent_rag_reports, submissions, cue_aware, top_k)
    return {
        "protocol": {
            "name": "e6-end-to-end-structured-report-v1",
            "top_k": top_k,
            "accept_reject_decision": False,
            "arxiv_unseen_gold_metrics": False,
            "system_candidate_generation": GENERATOR_NAME,
            "cue_aware_candidate_generation": CUE_AWARE_GENERATOR_NAME,
            "agent_rag_pipeline": AGENT_RAG_PIPELINE_NAME,
            "balanced_agent_rag_pipeline": BALANCED_AGENT_RAG_PIPELINE_NAME,
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
            "B3_cue_aware_structured_report": cue_aware,
            "B4_agent_rag_pipeline_report": agent_rag,
            "B5_balanced_agent_rag_pipeline_report": _balanced_agent_rag_metrics(
                balanced_agent_rag_reports,
                submissions,
                agent_rag,
                cue_aware,
                top_k,
            ),
        },
        "openreview_reports": reports,
        "system_generated_reports": generated_reports,
        "cue_aware_reports": cue_aware_reports,
        "agent_rag_reports": agent_rag_reports,
        "balanced_agent_rag_reports": balanced_agent_rag_reports,
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


def _cue_aware_report(submission: dict, top_k: int) -> dict:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    candidates = generate_cue_aware_candidate_weaknesses(submission)
    top = candidates[:top_k]
    return {
        "paper_id": paper_id,
        "title": content.get("title", paper_id),
        "summary": _summary(content),
        "decision": "not_applicable",
        "trace_policy": "paper_content_to_cue_aware_system_generated_topk",
        "candidate_source": CUE_AWARE_GENERATOR_NAME,
        "top_weaknesses": top,
        "candidate_count": len(candidates),
        "review_count": len(submission.get("reviews", [])),
    }


def _agent_rag_pipeline_report_variants(
    submissions: list[dict],
    top_k: int,
) -> tuple[list[dict], list[dict]]:
    pipeline = AgentRAGReviewPipeline(
        AgentRAGSystemConfig(
            max_candidates=max(6, top_k),
            top_k_weaknesses=top_k,
        )
    )
    base_reports = []
    balanced_reports = []
    for submission in submissions:
        base_report, balanced_report = _agent_rag_pipeline_report_variants_for_submission(
            pipeline,
            submission,
            top_k,
        )
        base_reports.append(base_report)
        balanced_reports.append(balanced_report)
    return base_reports, balanced_reports


def _agent_rag_pipeline_report_variants_for_submission(
    pipeline: AgentRAGReviewPipeline,
    submission: dict,
    top_k: int,
) -> tuple[dict, dict]:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    result = pipeline.run(ReviewPipelineRequest(submission=submission))
    traces = {trace.candidate.candidate_id: trace for trace in result.traces}
    base_top = [_pipeline_item_from_ranked(item, traces[item.candidate_id]) for item in result.top_weaknesses[:top_k]]
    balanced_top = _balanced_agent_rag_top_items(result.traces, top_k)
    base_report = {
        "paper_id": paper_id,
        "title": content.get("title", paper_id),
        "summary": result.report.summary,
        "decision": "not_applicable",
        "trace_policy": "paper_content_to_agent_rag_pipeline_topk",
        "candidate_source": AGENT_RAG_PIPELINE_NAME,
        "top_weaknesses": base_top,
        "candidate_count": len(result.traces),
        "review_count": len(submission.get("reviews", [])),
        "pipeline_stages": result.stages,
        "system_trace": result.system_trace,
    }
    balanced_report = {
        **base_report,
        "trace_policy": "paper_content_to_balanced_agent_rag_pipeline_topk",
        "candidate_source": BALANCED_AGENT_RAG_PIPELINE_NAME,
        "top_weaknesses": balanced_top,
        "selection_policy": {
            "name": "aspect_balanced_with_candidate_prior",
            "candidate_prior_weight": BALANCED_CANDIDATE_PRIOR_WEIGHT,
        },
    }
    return base_report, balanced_report


def _pipeline_item_from_ranked(item, trace) -> dict:
    return {
        "candidate_id": item.candidate_id,
        "paper_id": trace.candidate.paper_id,
        "aspect": trace.candidate.aspect,
        "weakness": item.weakness,
        "severity": trace.candidate.severity,
        "suggestion": trace.candidate.suggestion,
        "source_agent": trace.candidate.source_agent,
        "evidence_ids": item.evidence_ids,
        "confidence": item.confidence,
        "rank_score": item.rank_score,
        "source_review_id": None,
        "audit_decision": trace.adjudication.decision,
        "support_strength": trace.support.strength,
        "refutation_strength": trace.refutation.strength,
    }


def _balanced_agent_rag_top_items(traces, top_k: int) -> list[dict]:
    ranker = EvidenceAwareMetaRanker()
    trace_rows = [
        {
            "candidate": trace.candidate,
            "support": trace.support,
            "refutation": trace.refutation,
            "adjudication": trace.adjudication,
            "metadata": trace.metadata,
        }
        for trace in traces
    ]
    scored = []
    trace_by_id = {trace.candidate.candidate_id: trace for trace in traces}
    for row in trace_rows:
        item = ranker.score_traces([row])[0]
        candidate_prior = float(row["metadata"].get("candidate_rank_score") or 0.0)
        item = {
            **item,
            "rank_score": round(
                item["rank_score"] + BALANCED_CANDIDATE_PRIOR_WEIGHT * candidate_prior,
                6,
            ),
        }
        scored.append(item)
    scored.sort(key=lambda item: (-item["rank_score"], item["candidate"].candidate_id))
    selected = []
    used_aspects = set()
    for item in scored:
        aspect = item["candidate"].aspect
        if aspect in used_aspects:
            continue
        selected.append(item)
        used_aspects.add(aspect)
        if len(selected) == top_k:
            break
    for item in scored:
        if item not in selected:
            selected.append(item)
        if len(selected) == top_k:
            break
    return [_pipeline_item_from_scored(item, trace_by_id[item["candidate"].candidate_id]) for item in selected[:top_k]]


def _pipeline_item_from_scored(item: dict, trace) -> dict:
    adjudication = item["adjudication"]
    weakness = (
        adjudication.rewritten_weakness
        if adjudication.decision == "rewrite" and adjudication.rewritten_weakness
        else item["candidate"].weakness
    )
    return {
        "candidate_id": item["candidate"].candidate_id,
        "paper_id": item["candidate"].paper_id,
        "aspect": item["candidate"].aspect,
        "weakness": weakness,
        "severity": item["candidate"].severity,
        "suggestion": item["candidate"].suggestion,
        "source_agent": item["candidate"].source_agent,
        "evidence_ids": adjudication.evidence_ids,
        "confidence": item["confidence"],
        "rank_score": item["rank_score"],
        "source_review_id": None,
        "audit_decision": adjudication.decision,
        "support_strength": item["support"].strength,
        "refutation_strength": item["refutation"].strength,
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
    metrics["aspect_diversity@k"] = _aspect_diversity(reports)
    metrics["redundancy_rate@k"] = _redundancy_rate(reports)
    return metrics


def _cue_aware_metrics(
    reports: list[dict],
    submissions: list[dict],
    baseline_metrics: dict,
    top_k: int,
) -> dict:
    metrics = _system_generated_metrics(reports, submissions, top_k)
    metrics["official_weakness_proxy_overlap_delta_vs_b2"] = (
        metrics["official_weakness_proxy_overlap@k"]
        - baseline_metrics["official_weakness_proxy_overlap@k"]
    )
    return metrics


def _agent_rag_metrics(
    reports: list[dict],
    submissions: list[dict],
    baseline_metrics: dict,
    top_k: int,
) -> dict:
    metrics = _system_generated_metrics(reports, submissions, top_k)
    metrics["official_weakness_proxy_overlap_delta_vs_b3"] = (
        metrics["official_weakness_proxy_overlap@k"]
        - baseline_metrics["official_weakness_proxy_overlap@k"]
    )
    metrics["pipeline_stage_coverage"] = _pipeline_stage_coverage(reports)
    metrics["support_refutation_trace_coverage"] = _support_refutation_trace_coverage(reports)
    metrics["paper_decision_produced"] = any(
        report.get("system_trace", {}).get("paper_decision_produced", False)
        for report in reports
    )
    return metrics


def _balanced_agent_rag_metrics(
    reports: list[dict],
    submissions: list[dict],
    agent_rag_metrics: dict,
    cue_aware_metrics: dict,
    top_k: int,
) -> dict:
    metrics = _agent_rag_metrics(reports, submissions, cue_aware_metrics, top_k)
    metrics["official_weakness_proxy_overlap_delta_vs_b4"] = (
        metrics["official_weakness_proxy_overlap@k"]
        - agent_rag_metrics["official_weakness_proxy_overlap@k"]
    )
    metrics["aspect_diversity_delta_vs_b4"] = (
        metrics["aspect_diversity@k"] - agent_rag_metrics["aspect_diversity@k"]
    )
    metrics["balanced_candidate_prior_weight"] = BALANCED_CANDIDATE_PRIOR_WEIGHT
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


def _aspect_diversity(reports: list[dict]) -> float:
    diversities = []
    for report in reports:
        items = report["top_weaknesses"]
        if not items:
            continue
        diversities.append(len({item.get("aspect") for item in items}) / len(items))
    return sum(diversities) / len(diversities) if diversities else 0.0


def _redundancy_rate(reports: list[dict]) -> float:
    pairs = 0
    redundant = 0
    for report in reports:
        items = report["top_weaknesses"]
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                pairs += 1
                if _max_token_overlap(left["weakness"], [right["weakness"]]) >= 0.5:
                    redundant += 1
    return redundant / pairs if pairs else 0.0


def _pipeline_stage_coverage(reports: list[dict]) -> float:
    required = {
        "paper_parse_index",
        "candidate_generation",
        "query_planning",
        "paper_rag",
        "literature_rag_boundary",
        "support_refutation_audit",
        "adjudication",
        "meta_reviewer_ranking",
        "report_assembly",
    }
    if not reports:
        return 0.0
    return sum(required.issubset(set(report.get("pipeline_stages", []))) for report in reports) / len(reports)


def _support_refutation_trace_coverage(reports: list[dict]) -> float:
    items = [item for report in reports for item in report["top_weaknesses"]]
    if not items:
        return 0.0
    return sum(
        "support_strength" in item
        and "refutation_strength" in item
        and item.get("audit_decision") in {"keep", "rewrite", "reject", "uncertain"}
        for item in items
    ) / len(items)


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
