import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate(metrics_path: Path | None = None) -> dict:
    result = json.loads(
        (metrics_path or EXPERIMENT_ROOT / "outputs/metrics/e6_end_to_end_report.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = result["protocol"]
    dataset = result["dataset"]
    baseline = result["systems"]["B0_unstructured_review_dump"]
    structured = result["systems"]["B1_structured_evidence_report"]
    generated = result["systems"]["B2_system_generated_structured_report"]
    cue_aware = result["systems"]["B3_cue_aware_structured_report"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e6-end-to-end-structured-report-v1"
                and protocol["accept_reject_decision"] is False
                and protocol["arxiv_unseen_gold_metrics"] is False
                and protocol["system_candidate_generation"] == "system_deterministic_baseline_v1"
                and protocol["cue_aware_candidate_generation"] == "system_cue_aware_baseline_v2"
                and set(protocol["uses_component_outputs"]) == {"E2", "E3", "E4", "E5"}
            ),
            "protocol": protocol["name"],
        },
        "dataset": {
            "passed": (
                dataset["openreview_papers"] >= 30
                and dataset["openreview_reviews"] >= 120
                and dataset["arxiv_unseen_papers"] == 5
            ),
            "openreview_papers": dataset["openreview_papers"],
            "openreview_reviews": dataset["openreview_reviews"],
            "arxiv_unseen_papers": dataset["arxiv_unseen_papers"],
        },
        "traceability_improvement": {
            "passed": structured["trace_coverage"] > baseline["trace_coverage"],
            "baseline_trace_coverage": baseline["trace_coverage"],
            "structured_trace_coverage": structured["trace_coverage"],
        },
        "top_k_compliance": {
            "passed": (
                structured["top_k_compliance"] == 1.0
                and generated["top_k_compliance"] == 1.0
                and cue_aware["top_k_compliance"] == 1.0
            ),
            "review_derived_top_k_compliance": structured["top_k_compliance"],
            "system_generated_top_k_compliance": generated["top_k_compliance"],
            "cue_aware_top_k_compliance": cue_aware["top_k_compliance"],
        },
        "system_generated_candidates": {
            "passed": (
                generated["paper_report_coverage"] == 1.0
                and generated["trace_coverage"] == 1.0
                and generated["review_leakage_free"] is True
                and generated["official_weakness_proxy_overlap@k"] > 0.0
            ),
            "paper_report_coverage": generated["paper_report_coverage"],
            "trace_coverage": generated["trace_coverage"],
            "review_leakage_free": generated["review_leakage_free"],
            "official_weakness_proxy_overlap@k": generated["official_weakness_proxy_overlap@k"],
        },
        "cue_aware_optimization": {
            "passed": (
                cue_aware["paper_report_coverage"] == 1.0
                and cue_aware["trace_coverage"] == 1.0
                and cue_aware["review_leakage_free"] is True
                and cue_aware["official_weakness_proxy_overlap@k"]
                > generated["official_weakness_proxy_overlap@k"]
                and cue_aware["official_weakness_proxy_overlap_delta_vs_b2"] > 0.0
                and cue_aware["redundancy_rate@k"] <= generated.get("redundancy_rate@k", 1.0)
            ),
            "paper_report_coverage": cue_aware["paper_report_coverage"],
            "trace_coverage": cue_aware["trace_coverage"],
            "review_leakage_free": cue_aware["review_leakage_free"],
            "official_weakness_proxy_overlap@k": cue_aware[
                "official_weakness_proxy_overlap@k"
            ],
            "official_weakness_proxy_overlap_delta_vs_b2": cue_aware[
                "official_weakness_proxy_overlap_delta_vs_b2"
            ],
            "aspect_diversity@k": cue_aware["aspect_diversity@k"],
            "redundancy_rate@k": cue_aware["redundancy_rate@k"],
        },
        "decision_boundary": {
            "passed": (
                structured["accept_reject_decisions"] == 0
                and generated["accept_reject_decisions"] == 0
                and cue_aware["accept_reject_decisions"] == 0
            ),
            "review_derived_accept_reject_decisions": structured["accept_reject_decisions"],
            "system_generated_accept_reject_decisions": generated["accept_reject_decisions"],
            "cue_aware_accept_reject_decisions": cue_aware["accept_reject_decisions"],
        },
        "unseen_boundary": {
            "passed": result["unseen_demo"]["gold_metrics_reported"] is False
            and result["unseen_demo"]["papers"] == 5,
            "unseen_papers": result["unseen_demo"]["papers"],
            "gold_metrics_reported": result["unseen_demo"]["gold_metrics_reported"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "E6 end-to-end structured report assembly validates traceable Top-K reporting and unseen-demo boundaries.",
        "checks": checks,
        "metrics": {
            "baseline_trace_coverage": baseline["trace_coverage"],
            "structured_trace_coverage": structured["trace_coverage"],
            "system_generated_trace_coverage": generated["trace_coverage"],
            "cue_aware_trace_coverage": cue_aware["trace_coverage"],
            "structured_paper_report_coverage": structured["paper_report_coverage"],
            "system_generated_paper_report_coverage": generated["paper_report_coverage"],
            "cue_aware_paper_report_coverage": cue_aware["paper_report_coverage"],
            "structured_top_k_compliance": structured["top_k_compliance"],
            "system_generated_top_k_compliance": generated["top_k_compliance"],
            "cue_aware_top_k_compliance": cue_aware["top_k_compliance"],
            "system_generated_official_weakness_proxy_overlap@k": generated[
                "official_weakness_proxy_overlap@k"
            ],
            "cue_aware_official_weakness_proxy_overlap@k": cue_aware[
                "official_weakness_proxy_overlap@k"
            ],
            "cue_aware_official_weakness_proxy_overlap_delta_vs_b2": cue_aware[
                "official_weakness_proxy_overlap_delta_vs_b2"
            ],
            "cue_aware_aspect_diversity@k": cue_aware["aspect_diversity@k"],
            "cue_aware_redundancy_rate@k": cue_aware["redundancy_rate@k"],
            "accept_reject_decisions": cue_aware["accept_reject_decisions"],
        },
        "next_experiment": "Expand OpenReview seed and compare B3 cue-aware deterministic candidates with provider-generated candidates after provider stability improves.",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e6-end-to-end-report/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
