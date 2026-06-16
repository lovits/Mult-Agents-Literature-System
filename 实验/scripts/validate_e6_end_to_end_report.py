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
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e6-end-to-end-structured-report-v1"
                and protocol["accept_reject_decision"] is False
                and protocol["arxiv_unseen_gold_metrics"] is False
                and set(protocol["uses_component_outputs"]) == {"E2", "E3", "E4", "E5"}
            ),
            "protocol": protocol["name"],
        },
        "dataset": {
            "passed": (
                dataset["openreview_papers"] == 10
                and dataset["openreview_reviews"] >= 40
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
            "passed": structured["top_k_compliance"] == 1.0,
            "top_k_compliance": structured["top_k_compliance"],
        },
        "decision_boundary": {
            "passed": structured["accept_reject_decisions"] == 0,
            "accept_reject_decisions": structured["accept_reject_decisions"],
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
            "structured_paper_report_coverage": structured["paper_report_coverage"],
            "structured_top_k_compliance": structured["top_k_compliance"],
            "accept_reject_decisions": structured["accept_reject_decisions"],
        },
        "next_experiment": "Expand OpenReview seed or replace review-derived candidates with provider-generated candidates after provider stability improves.",
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
