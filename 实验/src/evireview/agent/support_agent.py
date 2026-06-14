from evireview.agent._audit_case import build_audit_case, lexical_overlap
from evireview.models.audit import AuditCase
from evireview.models.evidence import EvidenceBundle
from evireview.models.weakness import CandidateWeakness


class SupportAgent:
    """Builds the strongest available case that a candidate weakness is grounded."""

    def run(
        self,
        candidate: CandidateWeakness,
        bundle: EvidenceBundle,
    ) -> AuditCase:
        return build_audit_case(
            candidate,
            bundle,
            stance="support",
            scorer=lexical_overlap,
            claim=f"The evidence grounds this weakness: {candidate.weakness}",
        )
