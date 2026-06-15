from evireview.agent.provider import ROLE_INSTRUCTIONS


def test_strict_evidence_roles_reject_relatedness_as_sufficient_evidence():
    assert "mere relatedness is insufficient" in ROLE_INSTRUCTIONS["support_strict"]
    assert "mere relatedness is insufficient" in ROLE_INSTRUCTIONS["refutation_strict"]
    assert "strength must be at most 0.3" in ROLE_INSTRUCTIONS["support_strict"]
    assert "strength must be at most 0.3" in ROLE_INSTRUCTIONS["refutation_strict"]


def test_compact_adjudicator_is_conservative():
    instruction = ROLE_INSTRUCTIONS["adjudicate_compact"]

    assert "Do not default to keep" in instruction
    assert "Relatedness alone is not decisive" in instruction
