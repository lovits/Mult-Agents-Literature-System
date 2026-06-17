import math
import re

from evireview.models.audit import AdjudicationResult, AuditCase
from evireview.models.review import RankedWeakness
from evireview.models.weakness import CandidateWeakness


DECISION_WEIGHTS = {
    "keep": 0.42,
    "rewrite": 0.24,
    "uncertain": -0.05,
    "reject": -0.30,
}


class EvidenceAwareMetaRanker:
    """Filters, deduplicates, and ranks audited weaknesses for the final report."""

    def __init__(self, *, dedup_threshold: float = 0.48):
        self.dedup_threshold = dedup_threshold

    def rank(self, traces: list[dict], *, top_k: int) -> list[RankedWeakness]:
        scored = self.score_traces(traces)
        deduped = self._deduplicate(scored)
        return [
            RankedWeakness(
                candidate_id=item["candidate"].candidate_id,
                weakness=(
                    item["adjudication"].rewritten_weakness
                    if item["adjudication"].decision == "rewrite"
                    and item["adjudication"].rewritten_weakness
                    else item["candidate"].weakness
                ),
                evidence_ids=item["adjudication"].evidence_ids,
                confidence=item["confidence"],
                rank_score=item["rank_score"],
            )
            for item in deduped[:top_k]
        ]

    def score_traces(self, traces: list[dict]) -> list[dict]:
        scored = [self._score_trace(trace) for trace in traces]
        scored = [item for item in scored if item["decision"] in {"keep", "rewrite", "uncertain"}]
        scored.sort(key=lambda item: (-item["rank_score"], item["candidate"].candidate_id))
        return scored

    def _score_trace(self, trace: dict) -> dict:
        candidate: CandidateWeakness = trace["candidate"]
        support: AuditCase = trace["support"]
        refutation: AuditCase = trace["refutation"]
        adjudication: AdjudicationResult = trace["adjudication"]
        specificity = min(len(_tokens(candidate.weakness)) / 40, 1.0)
        actionability = min(len(_tokens(candidate.suggestion)) / 24, 1.0)
        severity = 0.22 if candidate.severity == "major" else 0.08
        uncertainty_penalty = 0.18 if adjudication.decision == "uncertain" else 0.0
        score = (
            DECISION_WEIGHTS[adjudication.decision]
            + 0.32 * support.strength
            - 0.18 * refutation.strength
            + severity
            + 0.12 * specificity
            + 0.10 * actionability
            - uncertainty_penalty
        )
        confidence = _sigmoid(score)
        return {
            "candidate": candidate,
            "support": support,
            "refutation": refutation,
            "adjudication": adjudication,
            "decision": adjudication.decision,
            "rank_score": round(score, 6),
            "confidence": round(confidence, 6),
        }

    def _deduplicate(self, items: list[dict]) -> list[dict]:
        selected: list[dict] = []
        deferred: list[dict] = []
        for item in items:
            redundancy = max(
                (
                    _jaccard(item["candidate"].weakness, previous["candidate"].weakness)
                    for previous in selected
                ),
                default=0.0,
            )
            if redundancy >= self.dedup_threshold:
                item = {**item, "rank_score": round(item["rank_score"] - redundancy, 6)}
                deferred.append(item)
            else:
                selected.append(item)
        reranked = selected + deferred
        reranked.sort(key=lambda item: (-item["rank_score"], item["candidate"].candidate_id))
        return reranked


def _jaccard(left: str, right: str) -> float:
    left_tokens = set(_tokens(left))
    right_tokens = set(_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))
