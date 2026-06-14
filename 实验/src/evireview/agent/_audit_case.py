from collections.abc import Callable

from evireview.models.audit import AuditCase
from evireview.models.evidence import EvidenceBundle, EvidenceItem
from evireview.models.weakness import CandidateWeakness
from evireview.rag.bm25 import tokenize


CaseScorer = Callable[[CandidateWeakness, EvidenceItem], float]


def build_audit_case(
    candidate: CandidateWeakness,
    bundle: EvidenceBundle,
    *,
    stance: str,
    scorer: CaseScorer,
    claim: str,
) -> AuditCase:
    if bundle.candidate_id != candidate.candidate_id:
        raise ValueError("evidence bundle must belong to the candidate")
    evidence = bundle.paper_evidence + bundle.literature_evidence
    scored = sorted(
        ((item, _bounded(scorer(candidate, item))) for item in evidence),
        key=lambda row: (-row[1], row[0].evidence_id),
    )
    selected = [item.evidence_id for item, score in scored[:3] if score > 0]
    strength = scored[0][1] if selected else 0.0
    return AuditCase(
        candidate_id=candidate.candidate_id,
        stance=stance,
        claim=claim,
        evidence_ids=selected,
        strength=min(strength, 0.2) if not selected else strength,
        rationale=(
            f"{stance} case cites {len(selected)} evidence item(s)."
            if selected
            else f"No evidence supports the {stance} case."
        ),
    )


def lexical_overlap(candidate: CandidateWeakness, item: EvidenceItem) -> float:
    query = set(tokenize(f"{candidate.target} {candidate.weakness}"))
    evidence = set(tokenize(item.text))
    return len(query & evidence) / max(len(query), 1)


def _bounded(value: float) -> float:
    return max(0.0, min(float(value), 1.0))
