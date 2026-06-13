from scripts.validate_e2_formal import validate


def test_formal_e2_is_completed_and_reports_failed_success_criteria_honestly():
    result = validate()

    assert result["passed"] is True
    assert result["status"] == "passed"
    assert result["experiment_verdict"] == "failed_with_metrics"
    assert result["checks"]["formal_run"]["samples"] == 136
    assert result["checks"]["formal_run"]["failures"] == 0
    assert result["checks"]["formal_run"]["revision"] == (
        "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a"
    )
    assert result["metrics"]["gating_p4_recall_delta"] > 0.03
    assert result["success_criteria"]["recall_gain_passed"] is False
    assert result["success_criteria"]["evidence_type_gain_passed"] is False
    assert result["success_criteria"]["latency_passed"] is True
