from evireview.agent.refutation_agent import RefutationAgent
from evireview.agent.support_agent import SupportAgent
from evireview.models.evidence import EvidenceBundle, EvidenceItem
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


def _bundle() -> EvidenceBundle:
    return EvidenceBundle(
        candidate_id="w1",
        paper_evidence=[
            EvidenceItem(
                evidence_id="p1:b1",
                source="paper",
                text="We report an ablation of the retrieval component in Table 3.",
                score=2.0,
                section="experiments",
                document_id="p1",
            )
        ],
        literature_evidence=[],
    )


def test_audit_cases_can_only_cite_bundle_evidence():
    candidate = _candidate()
    bundle = _bundle()

    support = SupportAgent().run(candidate, bundle)
    refutation = RefutationAgent().run(candidate, bundle)

    allowed = {
        item.evidence_id
        for item in bundle.paper_evidence + bundle.literature_evidence
    }
    assert set(support.evidence_ids) <= allowed
    assert set(refutation.evidence_ids) <= allowed
    assert support.stance == "support"
    assert refutation.stance == "refutation"


def test_empty_evidence_cases_have_capped_strength():
    candidate = _candidate()
    bundle = EvidenceBundle(
        candidate_id="w1",
        paper_evidence=[],
        literature_evidence=[],
    )

    support = SupportAgent().run(candidate, bundle)
    refutation = RefutationAgent().run(candidate, bundle)

    assert support.evidence_ids == []
    assert refutation.evidence_ids == []
    assert support.strength <= 0.2
    assert refutation.strength <= 0.2
