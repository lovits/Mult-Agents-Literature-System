import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate(metrics_path: Path | None = None) -> dict:
    metrics_path = metrics_path or EXPERIMENT_ROOT / "outputs/metrics/e6_neurips_stability.json"
    result = json.loads(metrics_path.read_text(encoding="utf-8"))
    systems = result["systems"]
    b3 = systems["B3_cue_aware_structured_report"]
    b4 = systems["B4_agent_rag_pipeline_report"]
    b5 = systems["B5_balanced_agent_rag_pipeline_report"]
    report_path = EXPERIMENT_ROOT / "reports/e6_neurips_stability_2026-06-17.md"
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    checks = {
        "protocol": {
            "passed": (
                result["protocol"]["name"] == "e6-neurips-2023-stability-v1"
                and result["protocol"]["accept_reject_decision"] is False
                and "proxy" in result["protocol"]["gold_boundary"]
            ),
            "protocol": result["protocol"],
        },
        "dataset": {
            "passed": result["dataset"]["papers"] >= 50
            and result["dataset"]["reviews"] >= 200,
            "dataset": result["dataset"],
        },
        "trace_and_topk": {
            "passed": (
                b3["trace_coverage"] == 1.0
                and b4["trace_coverage"] == 1.0
                and b5["trace_coverage"] == 1.0
                and b3["top_k_compliance"] == 1.0
                and b4["top_k_compliance"] == 1.0
                and b5["top_k_compliance"] == 1.0
            ),
            "b3_trace": b3["trace_coverage"],
            "b4_trace": b4["trace_coverage"],
            "b5_trace": b5["trace_coverage"],
        },
        "agent_rag_chain": {
            "passed": b4["pipeline_stage_coverage"] == 1.0
            and b4["support_refutation_trace_coverage"] == 1.0
            and b5["pipeline_stage_coverage"] == 1.0
            and b5["support_refutation_trace_coverage"] == 1.0,
            "b4_pipeline_stage_coverage": b4["pipeline_stage_coverage"],
            "b5_pipeline_stage_coverage": b5["pipeline_stage_coverage"],
        },
        "decision_boundary": {
            "passed": b3["accept_reject_decisions"] == 0
            and b4["accept_reject_decisions"] == 0
            and b5["accept_reject_decisions"] == 0
            and b4["paper_decision_produced"] is False
            and b5["paper_decision_produced"] is False,
        },
        "comparison_recorded": {
            "passed": {
                "b5_overlap_delta_vs_b3",
                "b5_overlap_delta_vs_b4",
                "b5_aspect_diversity_delta_vs_b4",
                "b5_redundancy_delta_vs_b4",
            }.issubset(result["comparison"]),
            "comparison": result["comparison"],
            "experiment_verdict": result["experiment_verdict"],
        },
        "report": {
            "passed": "E6 NeurIPS 2023 Stability Diagnostic" in report_text
            and "Experiment verdict" in report_text
            and "not a strict human Gold" in report_text,
            "report": str(report_path),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "E6 NeurIPS 2023 stability diagnostic is reproducible and boundary-gated.",
        "checks": checks,
        "metrics": {
            "b3_proxy_overlap": b3["official_weakness_proxy_overlap@k"],
            "b4_proxy_overlap": b4["official_weakness_proxy_overlap@k"],
            "b5_proxy_overlap": b5["official_weakness_proxy_overlap@k"],
            "b5_overlap_delta_vs_b3": result["comparison"]["b5_overlap_delta_vs_b3"],
            "b5_overlap_delta_vs_b4": result["comparison"]["b5_overlap_delta_vs_b4"],
            "b4_aspect_diversity": b4["aspect_diversity@k"],
            "b5_aspect_diversity": b5["aspect_diversity@k"],
            "experiment_verdict": result["experiment_verdict"],
        },
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e6-neurips-stability/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
