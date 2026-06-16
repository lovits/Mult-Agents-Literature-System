import re
from collections import defaultdict
from collections.abc import Callable

from evireview.dao.substanreview import SubstanClaim, SubstanReviewDataset


SYSTEMS: dict[str, Callable[[str, str, int], float]] = {
    "S0_proximity": lambda claim, candidate, gap: _proximity_score(gap),
    "S1_lexical": lambda claim, candidate, gap: _token_f1(claim, candidate),
    "S2_hybrid": lambda claim, candidate, gap: (
        0.7 * _token_f1(claim, candidate) + 0.3 * _proximity_score(gap)
    ),
}


def run_substanreview_baselines(dataset: SubstanReviewDataset) -> dict:
    development = [claim for claim in dataset.claims if claim.split == "train"]
    evaluation = [claim for claim in dataset.claims if claim.split == "test"]
    thresholds = {
        name: _tune_threshold(development, scorer) for name, scorer in SYSTEMS.items()
    }
    evaluated = {
        name: _evaluate(evaluation, scorer, thresholds[name])
        for name, scorer in SYSTEMS.items()
    }
    return {
        "protocol": {
            "name": "substanreview-gold-claim-evidence-linkage-v1",
            "development_split": "train",
            "evaluation_split": "test",
            "gold_claim_spans": True,
            "development_gold_used_for_threshold_tuning": True,
            "evaluation_gold_used_only_for_metrics": True,
            "weakness_validity_gold": False,
            "covered_refuted_gold": False,
        },
        "dataset": dataset.audit_summary(),
        "evaluation": _gold_summary(evaluation),
        "systems": {name: result["metrics"] for name, result in evaluated.items()},
        "sample_results": [
            {
                "claim_id": claim.claim_id,
                "review_id": claim.review_id,
                "polarity": claim.polarity,
                "gold_supported": claim.supported,
                "gold_evidence": [span.model_dump() for span in claim.evidence_spans],
                "systems": {
                    name: evaluated[name]["samples"][index]
                    for name in SYSTEMS
                },
            }
            for index, claim in enumerate(evaluation)
        ],
    }


def _gold_summary(claims: list[SubstanClaim]) -> dict:
    by_review: dict[str, list[SubstanClaim]] = defaultdict(list)
    for claim in claims:
        by_review[claim.review_id].append(claim)
    supported = sum(claim.supported for claim in claims)
    rates = [
        sum(claim.supported for claim in review_claims) / len(review_claims)
        for review_claims in by_review.values()
    ]
    substan_scores = [
        rate
        * len(next(iter(review_claims)).review.split())
        for rate, review_claims in zip(rates, by_review.values(), strict=True)
    ]
    return {
        "reviews": len(by_review),
        "claims": len(claims),
        "supported_claims": supported,
        "claim_evidence_coverage": supported / len(claims) if claims else 0.0,
        "substantiated_claim_rate": sum(rates) / len(rates) if rates else 0.0,
        "mean_substan_score": (
            sum(substan_scores) / len(substan_scores) if substan_scores else 0.0
        ),
    }


def _tune_threshold(
    claims: list[SubstanClaim],
    scorer: Callable[[str, str, int], float],
) -> float:
    scored = [_best_candidate(claim, scorer) for claim in claims]
    thresholds = sorted({0.0, 1.000001, *(score for _, score in scored)})
    candidates = []
    for threshold in thresholds:
        predicted = [score >= threshold for _, score in scored]
        precision, recall, f1 = _binary_metrics(
            [claim.supported for claim in claims], predicted
        )
        candidates.append((f1, precision, recall, threshold))
    return max(candidates)[3] if candidates else 1.000001


def _evaluate(
    claims: list[SubstanClaim],
    scorer: Callable[[str, str, int], float],
    threshold: float,
) -> dict:
    samples = []
    gold = []
    predicted = []
    evidence_hits = []
    evidence_f1s = []
    exact_matches = []
    for claim in claims:
        candidate, score = _best_candidate(claim, scorer)
        is_supported = score >= threshold
        gold.append(claim.supported)
        predicted.append(is_supported)
        if claim.supported:
            prediction = candidate["text"] if is_supported and candidate else ""
            evidence_hits.append(
                any(
                    _overlaps(candidate, span.start, span.end)
                    for span in claim.evidence_spans
                )
                if is_supported and candidate
                else False
            )
            evidence_f1s.append(
                max(
                    (_token_f1(prediction, span.text) for span in claim.evidence_spans),
                    default=0.0,
                )
            )
            exact_matches.append(
                any(
                    candidate["start"] == span.start and candidate["end"] == span.end
                    for span in claim.evidence_spans
                )
                if is_supported and candidate
                else False
            )
        samples.append(
            {
                "score": score,
                "threshold": threshold,
                "predicted_supported": is_supported,
                "predicted_evidence": candidate,
            }
        )
    precision, recall, f1 = _binary_metrics(gold, predicted)
    return {
        "metrics": {
            "threshold": threshold,
            "supported_precision": precision,
            "supported_recall": recall,
            "supported_f1": f1,
            "predicted_substantiated_rate": (
                sum(predicted) / len(predicted) if predicted else 0.0
            ),
            "evidence_hit@1": (
                sum(evidence_hits) / len(evidence_hits) if evidence_hits else 0.0
            ),
            "evidence_exact_match": (
                sum(exact_matches) / len(exact_matches) if exact_matches else 0.0
            ),
            "evidence_token_f1": (
                sum(evidence_f1s) / len(evidence_f1s) if evidence_f1s else 0.0
            ),
        },
        "samples": samples,
    }


def _best_candidate(
    claim: SubstanClaim,
    scorer: Callable[[str, str, int], float],
) -> tuple[dict | None, float]:
    candidates = _candidate_spans(claim.review, claim.claim_start, claim.claim_end)
    if not candidates:
        return None, 0.0
    ranked = [
        (
            scorer(claim.claim_text, candidate["text"], candidate["gap"]),
            -candidate["start"],
            candidate,
        )
        for candidate in candidates
    ]
    score, _, candidate = max(ranked, key=lambda item: (item[0], item[1]))
    return candidate, score


def _candidate_spans(review: str, claim_start: int, claim_end: int) -> list[dict]:
    candidates = []
    for start, end in _sentence_spans(review):
        pieces = (
            [(start, end)]
            if claim_end <= start or claim_start >= end
            else [(start, claim_start), (claim_end, end)]
        )
        for piece_start, piece_end in pieces:
            trimmed = _trim_span(review, piece_start, piece_end)
            if trimmed is None:
                continue
            item_start, item_end = trimmed
            gap = max(claim_start - item_end, item_start - claim_end, 0)
            candidates.append(
                {
                    "start": item_start,
                    "end": item_end,
                    "text": review[item_start:item_end],
                    "gap": gap,
                }
            )
    return candidates


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    boundaries = [0]
    boundaries.extend(
        match.end()
        for match in re.finditer(r"(?:[.!?](?=\s|$)|\n+)", text)
    )
    if boundaries[-1] != len(text):
        boundaries.append(len(text))
    return [
        (start, end)
        for start, end in zip(boundaries, boundaries[1:])
        if text[start:end].strip()
    ]


def _trim_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and (text[start].isspace() or text[start] in ".!?-:;,"):
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in ".!?-:;,"):
        end -= 1
    return (start, end) if start < end else None


def _proximity_score(gap: int) -> float:
    return 1 / (1 + gap / 100)


def _token_f1(left: str, right: str) -> float:
    left_tokens = re.findall(r"[a-z0-9]+", left.lower())
    right_tokens = re.findall(r"[a-z0-9]+", right.lower())
    if not left_tokens or not right_tokens:
        return 0.0
    left_counts = {token: left_tokens.count(token) for token in set(left_tokens)}
    right_counts = {token: right_tokens.count(token) for token in set(right_tokens)}
    overlap = sum(
        min(left_counts.get(token, 0), right_counts.get(token, 0))
        for token in left_counts
    )
    return 2 * overlap / (len(left_tokens) + len(right_tokens))


def _binary_metrics(gold: list[bool], predicted: list[bool]) -> tuple[float, float, float]:
    true_positive = sum(
        left and right for left, right in zip(gold, predicted, strict=True)
    )
    false_positive = sum(
        not left and right for left, right in zip(gold, predicted, strict=True)
    )
    false_negative = sum(
        left and not right for left, right in zip(gold, predicted, strict=True)
    )
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def _overlaps(candidate: dict, start: int, end: int) -> bool:
    return max(candidate["start"], start) < min(candidate["end"], end)
