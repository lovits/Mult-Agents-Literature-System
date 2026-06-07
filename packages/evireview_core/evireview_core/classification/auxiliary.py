from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import score_finding


REJECT_THRESHOLD = 0.5
MAX_FINDING_SCORE = 1.45


@dataclass(frozen=True)
class AuxiliaryDecisionSignal:
    label: str
    reject_score: float
    features: dict[str, float | int]
    metric_boundary: str = "auxiliary diagnostic"
    not_for_decision: bool = True
    warning: str = "Exploratory evidence-risk tendency only; do not use as an automated paper decision."

    def to_dict(self) -> dict:
        return asdict(self)


def classify_auxiliary_decision(
    weaknesses: list[Weakness],
    verification: dict[str, VerificationResult],
) -> AuxiliaryDecisionSignal:
    verified = [(weakness, verification[weakness.weakness_id]) for weakness in weaknesses if weakness.weakness_id in verification]
    scores = [score_finding(weakness, result) for weakness, result in verified]
    labels = Counter(result.label for _, result in verified)
    major_supported = sum(
        1
        for weakness, result in verified
        if weakness.severity == "major" and result.label in {"Supported", "Partially Supported"}
    )
    reject_score = round(min(1.0, max(scores, default=0.0) / MAX_FINDING_SCORE), 6)
    features: dict[str, float | int] = {
        "verified_weakness_count": len(verified),
        "major_supported_or_partial_count": major_supported,
        "supported_count": labels["Supported"],
        "partially_supported_count": labels["Partially Supported"],
        "mean_support_score": round(
            sum(result.support_score for _, result in verified) / len(verified),
            6,
        )
        if verified
        else 0.0,
        "max_evidence_aware_finding_score": round(max(scores, default=0.0), 6),
    }
    return AuxiliaryDecisionSignal(
        label="Reject" if reject_score >= REJECT_THRESHOLD else "Accept",
        reject_score=reject_score,
        features=features,
    )
