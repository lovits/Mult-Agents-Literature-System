from __future__ import annotations

import re
from dataclasses import dataclass

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import score_finding


TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset({"a", "an", "and", "for", "of", "the", "to"})
DEFAULT_SIMILARITY_THRESHOLD = 0.5


@dataclass(frozen=True)
class DeduplicationResult:
    weaknesses: list[Weakness]
    duplicate_of: dict[str, str]


def _normalize_token(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return f"{token[:-3]}y"
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


def _tokens(text: str) -> set[str]:
    return {_normalize_token(token) for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS}


def lexical_similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _evidence_score(weakness: Weakness, verification: dict[str, VerificationResult]) -> float:
    result = verification.get(weakness.weakness_id)
    return score_finding(weakness, result) if result is not None else 0.0


def deduplicate_weaknesses(
    weaknesses: list[Weakness],
    verification: dict[str, VerificationResult],
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> DeduplicationResult:
    groups: dict[tuple[str, str], list[list[Weakness]]] = {}
    ordered_clusters: list[list[Weakness]] = []
    for weakness in weaknesses:
        key = (weakness.paper_id, weakness.category)
        clusters = groups.setdefault(key, [])
        cluster = next(
            (
                candidate
                for candidate in clusters
                if any(lexical_similarity(weakness.weakness_text, item.weakness_text) >= threshold for item in candidate)
            ),
            None,
        )
        if cluster is None:
            cluster = [weakness]
            clusters.append(cluster)
            ordered_clusters.append(cluster)
        else:
            cluster.append(weakness)

    representatives: list[Weakness] = []
    duplicate_of: dict[str, str] = {}
    for cluster in ordered_clusters:
        representative = max(cluster, key=lambda item: _evidence_score(item, verification))
        representatives.append(representative)
        duplicate_of.update(
            {item.weakness_id: representative.weakness_id for item in cluster if item.weakness_id != representative.weakness_id}
        )
    return DeduplicationResult(weaknesses=representatives, duplicate_of=duplicate_of)
