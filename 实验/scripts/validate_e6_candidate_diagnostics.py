import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "outputs/metrics/e6_candidate_diagnostics.json"
AUTORESEARCH_RESULT = (
    ROOT.parent / ".omx/specs/autoresearch-e6-candidate-diagnostics/result.json"
)


def validate(metrics_path: Path | None = None) -> dict:
    path = metrics_path or RESULT_PATH
    result = json.loads(path.read_text(encoding="utf-8"))
    protocol = result["protocol"]
    dataset = result["dataset"]
    systems = result["systems"]
    comparison = result["comparison"]
    b2 = systems["B2_system_generated_structured_report"]
    b3 = systems["B3_cue_aware_structured_report"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e6-candidate-diagnostics-v1"
                and protocol["gold_usage"] == "diagnostic_only_official_review_weakness_proxy"
                and protocol["accept_reject_decision"] is False
            ),
            "name": protocol["name"],
            "gold_usage": protocol["gold_usage"],
        },
        "dataset": {
            "passed": dataset["openreview_papers"] >= 30 and dataset["openreview_reviews"] >= 120,
            "openreview_papers": dataset["openreview_papers"],
            "openreview_reviews": dataset["openreview_reviews"],
        },
        "systems": {
            "passed": (
                b2["overall_proxy_overlap@k"] > 0
                and b3["overall_proxy_overlap@k"] > 0
                and bool(b2["aspect_distribution"])
                and bool(b3["aspect_distribution"])
            ),
            "b2_overlap": b2["overall_proxy_overlap@k"],
            "b3_overlap": b3["overall_proxy_overlap@k"],
            "b3_aspects": b3["aspect_distribution"],
        },
        "comparison": {
            "passed": (
                comparison["b3_minus_b2_mean_delta"] > 0
                and comparison["b3_improved_papers"]
                + comparison["b3_tied_papers"]
                + comparison["b3_regressed_papers"]
                == dataset["openreview_papers"]
            ),
            "mean_delta": comparison["b3_minus_b2_mean_delta"],
            "improved": comparison["b3_improved_papers"],
            "tied": comparison["b3_tied_papers"],
            "regressed": comparison["b3_regressed_papers"],
        },
        "diagnostic_actionability": {
            "passed": bool(result["failure_cases"]) and bool(result["next_optimization_hints"]),
            "failure_cases": len(result["failure_cases"]),
            "hints": result["next_optimization_hints"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    validation = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "E6 candidate diagnostics validates B2/B3 aspect distribution and paper-level failure analysis."
            if passed
            else "E6 candidate diagnostics failed validation."
        ),
        "checks": checks,
        "metrics": {
            "b2_proxy_overlap@k": b2["overall_proxy_overlap@k"],
            "b3_proxy_overlap@k": b3["overall_proxy_overlap@k"],
            "b3_minus_b2_mean_delta": comparison["b3_minus_b2_mean_delta"],
            "b3_improved_papers": comparison["b3_improved_papers"],
            "b3_tied_papers": comparison["b3_tied_papers"],
            "b3_regressed_papers": comparison["b3_regressed_papers"],
            "failure_or_tie_rate": comparison["failure_or_tie_rate"],
        },
        "next_experiment": "Use the E6 failure slice for provider-generated candidate comparison without exposing Official Review text.",
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
