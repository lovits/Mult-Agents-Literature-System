import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate(
    baseline_path: Path | None = None,
    optimized_path: Path | None = None,
) -> dict:
    baseline = _read(
        baseline_path or EXPERIMENT_ROOT / "outputs/metrics/e4_agnes_pilot20.json"
    )
    optimized = _read(
        optimized_path
        or EXPERIMENT_ROOT / "outputs/metrics/e4_agnes_pilot20_optimized.json"
    )
    baseline_systems = baseline["systems"]
    optimized_systems = optimized["systems"]
    baseline_a4 = baseline_systems["A4"]
    a2 = optimized_systems["A2"]
    a3 = optimized_systems["A3"]
    a4 = optimized_systems["A4"]
    metrics = {
        "A4_macro_f1": a4["agreement_proxy_macro_f1"],
        "A4_vs_baseline_A4_macro_f1_delta": (
            a4["agreement_proxy_macro_f1"]
            - baseline_a4["agreement_proxy_macro_f1"]
        ),
        "A4_vs_A2_macro_f1_delta": (
            a4["agreement_proxy_macro_f1"] - a2["agreement_proxy_macro_f1"]
        ),
        "A4_vs_A3_macro_f1_delta": (
            a4["agreement_proxy_macro_f1"] - a3["agreement_proxy_macro_f1"]
        ),
        "A4_vs_A2_token_ratio": (
            a4["tokens_per_candidate"] / a2["tokens_per_candidate"]
        ),
        "A4_token_reduction_vs_baseline": (
            1
            - a4["tokens_per_candidate"] / baseline_a4["tokens_per_candidate"]
        ),
        "evidence_attribution_accuracy": optimized["integrity"][
            "evidence_attribution_accuracy"
        ],
        "provider_failures": optimized["integrity"]["failures"],
    }
    success_criteria = {
        "A4_improves_over_baseline_A4": (
            metrics["A4_vs_baseline_A4_macro_f1_delta"] >= 0.03
        ),
        "A4_not_worse_than_A2": metrics["A4_vs_A2_macro_f1_delta"] >= 0,
        "A4_not_worse_than_A3": metrics["A4_vs_A3_macro_f1_delta"] >= 0,
        "cost_ratio_passed": metrics["A4_vs_A2_token_ratio"] <= 2.5,
        "evidence_attribution_passed": (
            metrics["evidence_attribution_accuracy"] >= 0.75
        ),
        "zero_provider_failures": metrics["provider_failures"] == 0,
    }
    baseline_ids = [trace["example_id"] for trace in baseline["traces"]]
    optimized_ids = [trace["example_id"] for trace in optimized["traces"]]
    checks = {
        "protocol": {
            "passed": (
                baseline["protocol"].get("audit_profile", "standard_v1")
                == "standard_v1"
                and optimized["protocol"].get("audit_profile") == "bounded_v2"
                and optimized["protocol"]["provider_backed"] is True
                and optimized["protocol"]["selection"] == "stratified_proxy"
            ),
            "baseline_audit_profile": baseline["protocol"].get(
                "audit_profile", "standard_v1"
            ),
            "optimized_audit_profile": optimized["protocol"].get("audit_profile"),
        },
        "same_frozen_sample": {
            "passed": baseline_ids == optimized_ids and len(optimized_ids) == 20,
            "baseline_count": len(baseline_ids),
            "optimized_count": len(optimized_ids),
        },
        "systems": {
            "passed": set(optimized_systems) == {"A0", "A1", "A2", "A3", "A4"},
            "systems": sorted(optimized_systems),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    experiment_success = all(success_criteria.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Agnes E4 bounded optimization completed on the frozen Pilot20.",
        "experiment_verdict": (
            "passed_success_criteria" if experiment_success else "failed_with_metrics"
        ),
        "scale_decision": (
            "scale_to_main" if experiment_success else "stop_after_bounded_optimization"
        ),
        "checks": checks,
        "metrics": metrics,
        "success_criteria": success_criteria,
        "next_experiment": (
            "Scale E4 to main"
            if experiment_success
            else "Preserve the negative E4 result and move to SubstanReview"
        ),
    }


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    result = validate()
    output = (
        REPO_ROOT
        / ".omx/specs/autoresearch-e4-agnes-bounded-optimization/result.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
