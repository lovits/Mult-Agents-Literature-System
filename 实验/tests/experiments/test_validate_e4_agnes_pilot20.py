from scripts.validate_e4_agnes_pilot20 import validate


def test_agnes_pilot20_completes_with_honest_failed_metrics_verdict():
    result = validate()

    assert result["passed"] is True
    assert result["experiment_verdict"] == "failed_with_metrics"
    assert result["checks"]["coverage"]["evaluated"] == 20
    assert result["metrics"]["evidence_attribution_accuracy"] >= 0.75
    assert result["success_criteria"]["A4_improves_over_A2"] is False
    assert result["success_criteria"]["cost_ratio_passed"] is False
