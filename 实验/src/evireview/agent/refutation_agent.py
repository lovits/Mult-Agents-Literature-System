from evireview.agent._audit_case import build_audit_case, lexical_overlap
from evireview.models.audit import AuditCase
from evireview.models.evidence import EvidenceBundle, EvidenceItem
from evireview.models.weakness import CandidateWeakness
from evireview.rag.bm25 import tokenize


COVERAGE_CUES = {
    "ablation",
    "appendix",
    "compare",
    "comparison",
    "evaluate",
    "experiment",
    "include",
    "provide",
    "report",
    "result",
    "show",
    "table",
    "we",
}


def _refutation_score(candidate: CandidateWeakness, item: EvidenceItem) -> float:
    tokens = set(tokenize(item.text))
    cue_score = len(tokens & COVERAGE_CUES) / 4
    return 0.6 * lexical_overlap(candidate, item) + 0.4 * min(cue_score, 1.0)


class RefutationAgent:
    """Builds the strongest case that the paper already covers the concern."""

    def run(
        self,
        candidate: CandidateWeakness,
        bundle: EvidenceBundle,
    ) -> AuditCase:
        return build_audit_case(
            candidate,
            bundle,
            stance="refutation",
            scorer=_refutation_score,
            claim=f"The paper may already address this weakness: {candidate.weakness}",
        )
