import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    result = json.loads(
        (EXPERIMENT_ROOT / "outputs/metrics/e4_agnes_pilot20.json").read_text(
            encoding="utf-8"
        )
    )
    systems = result["systems"]
    integrity = result["integrity"]
    a2 = systems["A2"]
    a3 = systems["A3"]
    a4 = systems["A4"]
    metrics = {
        "A4_vs_A2_macro_f1_delta": (
            a4["agreement_proxy_macro_f1"] - a2["agreement_proxy_macro_f1"]
        ),
        "A4_vs_A3_macro_f1_delta": (
            a4["agreement_proxy_macro_f1"] - a3["agreement_proxy_macro_f1"]
        ),
        "A4_vs_A2_token_ratio": (
            a4["tokens_per_candidate"] / a2["tokens_per_candidate"]
        ),
        "A4_vs_A2_latency_ratio": (
            a4["latency_ms_per_candidate"] / a2["latency_ms_per_candidate"]
        ),
        "evidence_attribution_accuracy": integrity["evidence_attribution_accuracy"],
        "provider_failures": integrity["failures"],
    }
    success_criteria = {
        "A4_improves_over_A2": metrics["A4_vs_A2_macro_f1_delta"] >= 0.05,
        "A4_improves_over_A3": metrics["A4_vs_A3_macro_f1_delta"] >= 0.05,
        "evidence_attribution_passed": (
            metrics["evidence_attribution_accuracy"] >= 0.75
        ),
        "cost_ratio_passed": metrics["A4_vs_A2_token_ratio"] <= 2.5,
        "zero_provider_failures": metrics["provider_failures"] == 0,
    }
    checks = {
        "protocol": {
            "passed": (
                result["protocol"]["provider_backed"] is True
                and result["protocol"]["model"] == "agnes-2.0-flash"
                and result["protocol"]["selection"] == "stratified_proxy"
            ),
            **result["protocol"],
        },
        "coverage": {
            "passed": result["evaluated"] == 20 and len(result["traces"]) == 20,
            "evaluated": result["evaluated"],
            "traces": len(result["traces"]),
        },
        "systems": {
            "passed": set(systems) == {"A0", "A1", "A2", "A3", "A4"},
            "systems": sorted(systems),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    experiment_success = all(success_criteria.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Agnes E4 stratified pilot20 completed with an honest verdict.",
        "experiment_verdict": (
            "passed_success_criteria" if experiment_success else "failed_with_metrics"
        ),
        "checks": checks,
        "metrics": metrics,
        "success_criteria": success_criteria,
        "next_experiment": "One bounded prompt/output-contract optimization before scaling",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-agnes-pilot20/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
