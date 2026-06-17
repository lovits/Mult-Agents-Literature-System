import json

from scripts.validate_e6_provider_candidates import validate


def test_validate_e6_provider_candidates_accepts_completed_provider_slice(tmp_path):
    metrics = {
        "protocol": {
            "name": "e6-provider-candidate-failure-slice-v1",
            "provider_backed": True,
            "model": "deepseek-v4-flash-free",
            "selection": "e6_candidate_diagnostics_failure_cases",
            "limit": 8,
            "top_k": 3,
            "prompt_input_boundary": "paper_metadata_and_b3_candidates_only_no_official_reviews",
            "gold_usage": "offline_proxy_evaluation_only",
            "accept_reject_decision": False,
        },
        "dataset": {"selected_papers": 8, "openreview_reviews_in_selected_papers": 32},
        "systems": {
            "B2_failure_slice": {"official_weakness_proxy_overlap@k": 0.05},
            "B3_failure_slice": {"official_weakness_proxy_overlap@k": 0.04},
            "P1_provider_generated_failure_slice": {
                "paper_report_coverage": 1.0,
                "trace_coverage": 1.0,
                "top_k_compliance": 1.0,
                "accept_reject_decisions": 0,
                "review_leakage_free": True,
                "official_weakness_proxy_overlap@k": 0.06,
            },
        },
        "comparison": {
            "p1_minus_b3_proxy_overlap_delta": 0.02,
            "p1_minus_b2_proxy_overlap_delta": 0.01,
            "p1_improved_over_b3_papers": 4,
        },
        "integrity": {
            "provider_failures": 0,
            "invalid_citations": 0,
            "cited_evidence_ids": 8,
            "evidence_attribution_accuracy": 1.0,
            "failure_reasons": {},
        },
    }
    path = tmp_path / "provider.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["metrics"]["p1_minus_b3_proxy_overlap_delta"] == 0.02


def test_validate_e6_provider_candidates_preserves_pending_environment(tmp_path):
    metrics = {
        "status": "pending_environment",
        "passed": False,
        "checks": {"environment": {"passed": False}},
    }
    path = tmp_path / "provider.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "pending_environment"
    assert result["passed"] is False
