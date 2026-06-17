import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "outputs/metrics/e6_b5_diagnostics.json"
AUTORESEARCH_RESULT = (
    ROOT.parent / ".omx/specs/autoresearch-e6-b5-diagnostics/result.json"
)


def validate(metrics_path: Path | None = None) -> dict:
    path = metrics_path or RESULT_PATH
    result = json.loads(path.read_text(encoding="utf-8"))
    protocol = result["protocol"]
    dataset = result["dataset"]
    systems = result["systems"]
    comparison = result["comparison"]
    b5 = systems["B5_balanced_agent_rag_pipeline_report"]
    paper_count = dataset["openreview_papers"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e6-b5-balanced-agent-rag-diagnostics-v1"
                and protocol["gold_usage"]
                == "diagnostic_only_official_review_weakness_proxy"
                and protocol["accept_reject_decision"] is False
            ),
            "name": protocol["name"],
            "gold_usage": protocol["gold_usage"],
        },
        "dataset": {
            "passed": dataset["openreview_papers"] >= 30
            and dataset["openreview_reviews"] >= 120,
            "openreview_papers": dataset["openreview_papers"],
            "openreview_reviews": dataset["openreview_reviews"],
        },
        "systems": {
            "passed": (
                b5["overall_proxy_overlap@k"] > 0
                and bool(b5["aspect_distribution"])
                and bool(b5["aspect_proxy_overlap@k"])
            ),
            "b5_overlap": b5["overall_proxy_overlap@k"],
            "b5_aspects": b5["aspect_distribution"],
            "b5_zero_overlap_rate": b5["zero_overlap_rate"],
        },
        "comparison": {
            "passed": (
                comparison["b5_minus_b4_mean_delta"] > 0
                and comparison["b5_improved_vs_b4_papers"]
                + comparison["b5_tied_vs_b4_papers"]
                + comparison["b5_regressed_vs_b4_papers"]
                == paper_count
                and comparison["b5_improved_vs_b3_papers"]
                + comparison["b5_tied_vs_b3_papers"]
                + comparison["b5_regressed_vs_b3_papers"]
                == paper_count
            ),
            "b5_minus_b4_mean_delta": comparison["b5_minus_b4_mean_delta"],
            "b5_minus_b3_mean_delta": comparison["b5_minus_b3_mean_delta"],
            "b5_improved_vs_b4_papers": comparison["b5_improved_vs_b4_papers"],
            "b5_regressed_vs_b4_papers": comparison["b5_regressed_vs_b4_papers"],
        },
        "diagnostic_actionability": {
            "passed": bool(result["aspect_bottlenecks"])
            and bool(result["low_overlap_cases"])
            and bool(result["next_optimization_hints"]),
            "aspect_bottlenecks": result["aspect_bottlenecks"],
            "low_overlap_cases": len(result["low_overlap_cases"]),
            "regression_vs_b4_cases": len(result["regression_vs_b4_cases"]),
            "hints": result["next_optimization_hints"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    validation = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "E6 B5 diagnostics validates balanced Agent-RAG aspect bottlenecks and paper-level deltas."
            if passed
            else "E6 B5 diagnostics failed validation."
        ),
        "checks": checks,
        "metrics": {
            "b5_proxy_overlap@k": b5["overall_proxy_overlap@k"],
            "b5_zero_overlap_rate": b5["zero_overlap_rate"],
            "b5_minus_b4_mean_delta": comparison["b5_minus_b4_mean_delta"],
            "b5_minus_b3_mean_delta": comparison["b5_minus_b3_mean_delta"],
            "b5_improved_vs_b4_papers": comparison["b5_improved_vs_b4_papers"],
            "b5_tied_vs_b4_papers": comparison["b5_tied_vs_b4_papers"],
            "b5_regressed_vs_b4_papers": comparison["b5_regressed_vs_b4_papers"],
            "weakest_b5_aspect": result["aspect_bottlenecks"][0]["aspect"]
            if result["aspect_bottlenecks"]
            else None,
        },
        "next_experiment": (
            "Use the weakest B5 aspect slice to decide whether to optimize candidate filtering "
            "or aspect-specific query planning."
        ),
    }
    AUTORESEARCH_RESULT.parent.mkdir(parents=True, exist_ok=True)
    AUTORESEARCH_RESULT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return validation


def main() -> None:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
