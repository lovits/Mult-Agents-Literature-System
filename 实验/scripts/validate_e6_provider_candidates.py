import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
RESULT_PATH = ROOT / "outputs/metrics/e6_deepseek_provider_candidates.json"
AUTORESEARCH_RESULT = (
    REPO_ROOT / ".omx/specs/autoresearch-e6-provider-candidates/result.json"
)


def validate(metrics_path: Path | None = None) -> dict:
    path = metrics_path or RESULT_PATH
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("status") == "pending_environment":
        validation = {
            "status": "pending_environment",
            "passed": False,
            "summary": "E6 provider candidates are implemented but require EVIREVIEW_LLM_API_KEY to run.",
            "checks": result.get("checks", {}),
            "next_experiment": "Export EVIREVIEW_LLM_API_KEY and rerun scripts/run_e6_provider_candidates.py.",
        }
        _write_autoresearch(validation)
        return validation
    protocol = result["protocol"]
    dataset = result["dataset"]
    systems = result["systems"]
    integrity = result["integrity"]
    comparison = result["comparison"]
    provider_system = systems["P1_provider_generated_failure_slice"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e6-provider-candidate-failure-slice-v1"
                and protocol["provider_backed"] is True
                and protocol["model"] == "deepseek-v4-flash-free"
                and protocol["prompt_input_boundary"]
                == "paper_metadata_and_b3_candidates_only_no_official_reviews"
                and protocol["accept_reject_decision"] is False
            ),
            **protocol,
        },
        "coverage": {
            "passed": dataset["selected_papers"] == protocol["limit"] == 8,
            "selected_papers": dataset["selected_papers"],
            "limit": protocol["limit"],
        },
        "provider_output_boundary": {
            "passed": (
                provider_system["top_k_compliance"] == 1.0
                and provider_system["review_leakage_free"] is True
                and provider_system["accept_reject_decisions"] == 0
            ),
            "paper_report_coverage": provider_system["paper_report_coverage"],
            "top_k_compliance": provider_system["top_k_compliance"],
            "review_leakage_free": provider_system["review_leakage_free"],
            "accept_reject_decisions": provider_system["accept_reject_decisions"],
        },
        "integrity_accounting": {
            "passed": (
                integrity["provider_failures"] >= 0
                and integrity["evidence_attribution_accuracy"] >= 0.75
                and "failure_reasons" in integrity
            ),
            **integrity,
        },
        "comparison": {
            "passed": "p1_minus_b3_proxy_overlap_delta" in comparison,
            **comparison,
        },
    }
    passed = all(check["passed"] for check in checks.values())
    success_criteria = {
        "full_provider_coverage": provider_system["paper_report_coverage"] == 1.0,
        "zero_provider_failures": integrity["provider_failures"] == 0,
        "improves_over_b3_failure_slice": comparison["p1_minus_b3_proxy_overlap_delta"] > 0,
        "improves_over_b2_failure_slice": comparison["p1_minus_b2_proxy_overlap_delta"] > 0,
    }
    experiment_success = all(success_criteria.values())
    validation = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "E6 provider-generated candidate comparison completed on the diagnostic failure slice."
            if passed
            else "E6 provider-generated candidate comparison failed validation."
        ),
        "experiment_verdict": (
            "passed_success_criteria" if experiment_success else "failed_with_metrics"
        ),
        "checks": checks,
        "metrics": {
            "b2_failure_slice_proxy_overlap@k": systems["B2_failure_slice"][
                "official_weakness_proxy_overlap@k"
            ],
            "b3_failure_slice_proxy_overlap@k": systems["B3_failure_slice"][
                "official_weakness_proxy_overlap@k"
            ],
            "p1_provider_proxy_overlap@k": provider_system[
                "official_weakness_proxy_overlap@k"
            ],
            "p1_minus_b3_proxy_overlap_delta": comparison[
                "p1_minus_b3_proxy_overlap_delta"
            ],
            "p1_minus_b2_proxy_overlap_delta": comparison[
                "p1_minus_b2_proxy_overlap_delta"
            ],
            "paper_report_coverage": provider_system["paper_report_coverage"],
            "provider_failures": integrity["provider_failures"],
        },
        "success_criteria": success_criteria,
        "next_experiment": "Use E6-P results to decide whether provider-generated candidates should replace or only complement B3 on failure slices.",
    }
    _write_autoresearch(validation)
    return validation


def _write_autoresearch(validation: dict) -> None:
    AUTORESEARCH_RESULT.parent.mkdir(parents=True, exist_ok=True)
    AUTORESEARCH_RESULT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
