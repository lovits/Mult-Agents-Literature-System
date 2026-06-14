from scripts.validate_e4_audit_protocol import validate


def test_e4_audit_protocol_is_complete_but_not_misreported_as_formal():
    result = validate()

    assert result["passed"] is True
    assert result["checks"]["protocol"]["formal_a0_a4_result"] is False
    assert result["checks"]["coverage"]["evaluated"] == 155
    assert result["checks"]["integrity"]["invalid_citations"] == 0
    assert result["checks"]["integrity"]["missing_bidirectional_cases"] == 0
    assert result["next_experiment"] == "Formal provider-backed E4 A0-A4"
