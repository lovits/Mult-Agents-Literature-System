from __future__ import annotations

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.parsing.markdown_sections import tokenize
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.labels import VerifierLabel


ABSENCE_TERMS = {"lack", "lacks", "missing", "without", "no"}
PRESENCE_TERMS = {"include", "includes", "included", "report", "reports", "reported", "provide", "provides", "has"}
NEGATION_TERMS = {"no", "not", "none", "cannot", "without"}


def _overlap_ratio(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def _looks_contradicted(weakness_text: str, evidence_text: str) -> bool:
    weakness_tokens = set(tokenize(weakness_text))
    evidence_tokens = set(tokenize(evidence_text))
    content_overlap = weakness_tokens & evidence_tokens - ABSENCE_TERMS - PRESENCE_TERMS
    if evidence_tokens & NEGATION_TERMS:
        return False
    return bool(weakness_tokens & ABSENCE_TERMS and evidence_tokens & PRESENCE_TERMS and len(content_overlap) >= 2)


def verify_with_heuristics(weakness: Weakness, evidence: list[RetrievedEvidence]) -> VerificationResult:
    if not evidence:
        return VerificationResult(
            weakness_id=weakness.weakness_id,
            label=VerifierLabel.UNSUPPORTED.value,
            support_score=0.0,
            evidence_block_ids=(),
            rationale="No retrieved evidence was available for this weakness.",
            verifier="heuristic_overlap_v1",
        )

    best_evidence = max(evidence, key=lambda item: _overlap_ratio(weakness.weakness_text, item.text))
    best_overlap = _overlap_ratio(weakness.weakness_text, best_evidence.text)
    evidence_ids = tuple(item.block_id for item in evidence[:3])
    if _looks_contradicted(weakness.weakness_text, best_evidence.text):
        label = VerifierLabel.CONTRADICTED.value
        rationale = "Retrieved evidence appears to state the missing element is present."
    elif best_overlap >= 0.45:
        label = VerifierLabel.PARTIALLY_SUPPORTED.value
        rationale = "Retrieved evidence shares substantial terms with the weakness and should be reviewed."
    elif best_overlap >= 0.2:
        label = VerifierLabel.MENTIONED_NOT_PROBLEM.value
        rationale = "Retrieved evidence mentions related terms but does not clearly establish the problem."
    else:
        label = VerifierLabel.UNSUPPORTED.value
        rationale = "Retrieved evidence has weak lexical overlap with the weakness."

    return VerificationResult(
        weakness_id=weakness.weakness_id,
        label=label,
        support_score=round(best_overlap, 4),
        evidence_block_ids=evidence_ids,
        rationale=rationale,
        verifier="heuristic_overlap_v1",
    )
