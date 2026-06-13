import math
from collections.abc import Iterable


def evaluate_ranking(
    ranked_ids: list[str],
    relevant_ids: set[str],
    cutoffs: Iterable[int] = (1, 3, 5, 10),
) -> dict[str, float]:
    if not relevant_ids:
        raise ValueError("relevant_ids must not be empty")

    metrics = {
        f"recall@{cutoff}": _recall_at_k(ranked_ids, relevant_ids, cutoff)
        for cutoff in cutoffs
    }
    metrics["mrr"] = _reciprocal_rank(ranked_ids, relevant_ids)
    for cutoff in cutoffs:
        metrics[f"ndcg@{cutoff}"] = _ndcg_at_k(ranked_ids, relevant_ids, cutoff)
    return metrics


def _recall_at_k(ranked_ids: list[str], relevant_ids: set[str], cutoff: int) -> float:
    return len(set(ranked_ids[:cutoff]) & relevant_ids) / len(relevant_ids)


def _reciprocal_rank(ranked_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, item_id in enumerate(ranked_ids, start=1):
        if item_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def _ndcg_at_k(ranked_ids: list[str], relevant_ids: set[str], cutoff: int) -> float:
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, item_id in enumerate(ranked_ids[:cutoff], start=1)
        if item_id in relevant_ids
    )
    ideal_hits = min(len(relevant_ids), cutoff)
    ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / ideal_dcg
