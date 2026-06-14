from evireview.models.audit import AdjudicationResult, AuditCase
from evireview.models.weakness import CandidateWeakness


class EvidenceAdjudicator:
    """Turns fixed support/refutation cases into a reproducible machine decision."""

    def __init__(self, *, decisive_strength: float = 0.55, margin: float = 0.15):
        self.decisive_strength = decisive_strength
        self.margin = margin

    def decide(
        self,
        candidate: CandidateWeakness,
        support: AuditCase,
        refutation: AuditCase,
    ) -> AdjudicationResult:
        self._validate(candidate, support, refutation)
        delta = support.strength - refutation.strength
        evidence_ids = list(dict.fromkeys(support.evidence_ids + refutation.evidence_ids))

        if (
            refutation.strength >= self.decisive_strength
            and delta <= -self.margin
        ):
            decision = "reject"
            reason = "Refutation evidence is materially stronger than support evidence."
        elif support.strength >= self.decisive_strength and delta >= self.margin:
            decision = "keep"
            reason = "Support evidence is materially stronger than refutation evidence."
        elif (
            support.strength >= self.decisive_strength
            and refutation.strength >= self.decisive_strength
        ):
            decision = "rewrite"
            reason = "Both directions are strong; narrow the weakness to the unresolved part."
        else:
            decision = "uncertain"
            reason = "Available evidence is insufficient for a decisive machine judgment."

        confidence = min(1.0, max(support.strength, refutation.strength, abs(delta)))
        return AdjudicationResult(
            candidate_id=candidate.candidate_id,
            decision=decision,
            confidence=confidence,
            evidence_ids=evidence_ids,
            reason=reason,
            rewritten_weakness=(
                f"Clarify the unresolved evidence for: {candidate.weakness}"
                if decision == "rewrite"
                else None
            ),
        )

    @staticmethod
    def _validate(
        candidate: CandidateWeakness,
        support: AuditCase,
        refutation: AuditCase,
    ) -> None:
        if support.candidate_id != candidate.candidate_id:
            raise ValueError("support case must belong to the candidate")
        if refutation.candidate_id != candidate.candidate_id:
            raise ValueError("refutation case must belong to the candidate")
        if support.stance != "support" or refutation.stance != "refutation":
            raise ValueError("adjudicator requires fixed support and refutation cases")
