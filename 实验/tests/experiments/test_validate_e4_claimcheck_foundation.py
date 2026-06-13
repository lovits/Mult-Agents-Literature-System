from scripts.validate_e4_claimcheck_foundation import validate


def test_e4_claimcheck_foundation_is_ready_without_overclaiming_labels():
    result = validate()

    assert result["passed"] is True
    assert result["checks"]["claimcheck"]["weaknesses"] == 168
    assert result["checks"]["claimcheck"]["grounded_weaknesses"] == 120
    assert result["checks"]["evaluation_boundary"]["covered_refuted_gold"] is False
    assert result["next_experiment"] == "E4 claim association and weakness labeling baselines"
