from scripts.validate_e4_agnes_calibration import validate


def test_agnes_calibration_has_all_systems_usage_and_no_failures():
    result = validate()

    assert result["passed"] is True
    assert result["checks"]["provider"]["model"] == "agnes-2.0-flash"
    assert result["checks"]["coverage"]["evaluated"] == 5
    assert result["checks"]["integrity"]["failures"] == 0
    assert result["next_experiment"] == "Scale Agnes provider-backed E4 A0-A4"
