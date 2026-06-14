from evireview.agent.evidence_adjudicator import EvidenceAdjudicator
from evireview.evaluation.label_mapping import claimcheck_agreement_to_decision
from evireview.models.audit import AuditCase
from evireview.models.weakness import CandidateWeakness


def _candidate() -> CandidateWeakness:
    return CandidateWeakness(
        candidate_id="w1",
        paper_id="p1",
        aspect="experiment",
        target="ablation",
        weakness="The retrieval component lacks an ablation.",
        severity="major",
        suggestion="Add an ablation.",
        source_agent="experiment_reviewer",
    )


def _case(stance: str, strength: float) -> AuditCase:
    return AuditCase(
        candidate_id="w1",
        stance=stance,
        claim=f"{stance} case",
        evidence_ids=["p1:b1"] if strength > 0.2 else [],
        strength=strength,
        rationale=f"{stance} rationale",
    )


def test_strong_refutation_rejects_candidate():
    result = EvidenceAdjudicator().decide(
        _candidate(),
        _case("support", 0.2),
        _case("refutation", 0.8),
    )

    assert result.decision == "reject"
    assert result.confidence >= 0.5


def test_weak_cases_produce_machine_uncertain_decision():
    result = EvidenceAdjudicator().decide(
        _candidate(),
        _case("support", 0.2),
        _case("refutation", 0.2),
    )

    assert result.decision == "uncertain"
    assert "human" not in result.reason.lower()


def test_claimcheck_agreement_mapping_is_explicit_proxy():
    assert claimcheck_agreement_to_decision(1) == "reject"
    assert claimcheck_agreement_to_decision(2) == "reject"
    assert claimcheck_agreement_to_decision(3) == "uncertain"
    assert claimcheck_agreement_to_decision(4) == "keep"
    assert claimcheck_agreement_to_decision(5) == "keep"
