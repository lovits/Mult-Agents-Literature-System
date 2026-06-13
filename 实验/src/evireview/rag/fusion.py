from dataclasses import dataclass


@dataclass(frozen=True)
class FusedItem:
    item_id: str
    score: float


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[FusedItem]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank)
    return [
        FusedItem(item_id=item_id, score=score)
        for item_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    ]
