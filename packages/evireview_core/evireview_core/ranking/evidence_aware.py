from __future__ import annotations

from evireview_core.domain.models import RankedFinding, VerificationResult, Weakness


LABEL_WEIGHTS = {
    "Supported": 1.0,
    "Partially Supported": 0.8,
    "Mentioned but Not Problem": 0.45,
    "Generic / Vague": 0.2,
    "Unsupported": 0.05,
    "Contradicted": 0.0,
}

SEVERITY_WEIGHTS = {
    "major": 1.0,
    "minor": 0.65,
    "minor_or_question": 0.6,
    "unknown": 0.75,
}


def score_finding(weakness: Weakness, result: VerificationResult) -> float:
    label_weight = LABEL_WEIGHTS.get(result.label, 0.25)
    severity_weight = SEVERITY_WEIGHTS.get(weakness.severity, 0.75)
    return round((0.45 + result.support_score) * label_weight * severity_weight, 6)


def rank_weaknesses(
    weaknesses: list[Weakness],
    verification: dict[str, VerificationResult],
    top_k: int = 3,
) -> list[RankedFinding]:
    scored: list[tuple[float, Weakness, VerificationResult]] = []
    for weakness in weaknesses:
        result = verification.get(weakness.weakness_id)
        if result is not None:
            scored.append((score_finding(weakness, result), weakness, result))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        RankedFinding(
            weakness_id=weakness.weakness_id,
            rank=rank,
            rank_score=score,
            label=result.label,
        )
        for rank, (score, weakness, result) in enumerate(scored[:top_k], start=1)
    ]
