from scripts.validate_e4_minimax_calibration import validate


def test_minimax_calibration_reports_current_quota_blocker_honestly():
    result = validate()

    assert result["passed"] is False
    assert result["status"] == "pending_quota"
    assert result["checks"]["provider"]["model"] == "MiniMax-M2.7"
    assert result["checks"]["integrity"]["failure_reasons"] == {"http_429": 6}
    assert result["next_experiment"].startswith("Scale provider-backed E4")
