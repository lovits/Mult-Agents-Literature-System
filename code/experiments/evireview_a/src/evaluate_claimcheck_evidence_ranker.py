from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, write_json
from evaluate_claimcheck_feature_verifier import (
    EMBEDDING_CACHE_PATH,
    best_threshold,
    make_group_folds,
    predict_probabilities,
    row_features,
    standardize,
    train_logistic,
)


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def average_precision(labels: list[int]) -> float:
    hits = 0
    total = 0.0
    for rank, label in enumerate(labels, start=1):
        if label:
            hits += 1
            total += hits / rank
    return safe_div(total, sum(labels))


def dcg(labels: list[int], k: int) -> float:
    return sum(label / math.log2(rank + 1) for rank, label in enumerate(labels[:k], start=1))


def ndcg(labels: list[int], k: int) -> float:
    ideal = sorted(labels, reverse=True)
    return safe_div(dcg(labels, k), dcg(ideal, k))


def grouped_rank_metrics(rows: list[dict[str, Any]], scores: list[float]) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row["paper_review_id"]].append(index)

    evaluated = []
    skipped = 0
    for indices in groups.values():
        labels = [1 if rows[index]["grounding_label"] == "Grounded" else 0 for index in indices]
        if not any(labels) or all(labels):
            skipped += 1
            continue
        ranked = sorted(indices, key=lambda index: scores[index], reverse=True)
        ranked_labels = [1 if rows[index]["grounding_label"] == "Grounded" else 0 for index in ranked]
        evaluated.append(
            {
                "ap": average_precision(ranked_labels),
                "ndcg_at_3": ndcg(ranked_labels, 3),
                "ndcg_at_5": ndcg(ranked_labels, 5),
                "top1_grounded": ranked_labels[0],
                "bottom1_ungrounded": 1 - ranked_labels[-1],
            }
        )

    return {
        "evaluated_group_count": len(evaluated),
        "skipped_single_label_group_count": skipped,
        "map": round(safe_div(sum(item["ap"] for item in evaluated), len(evaluated)), 4),
        "ndcg_at_3": round(safe_div(sum(item["ndcg_at_3"] for item in evaluated), len(evaluated)), 4),
        "ndcg_at_5": round(safe_div(sum(item["ndcg_at_5"] for item in evaluated), len(evaluated)), 4),
        "top1_grounded_rate": round(safe_div(sum(item["top1_grounded"] for item in evaluated), len(evaluated)), 4),
        "bottom1_ungrounded_rate": round(safe_div(sum(item["bottom1_ungrounded"] for item in evaluated), len(evaluated)), 4),
    }


def cross_validated_grounding_probabilities(rows: list[dict[str, Any]], feature_matrix: list[list[float]], labels: list[int]) -> list[float]:
    folds = make_group_folds(rows)
    all_indices = set(range(len(rows)))
    probabilities = [0.0] * len(rows)
    for test_indices in folds:
        train_indices = sorted(all_indices - set(test_indices))
        train_gold = [rows[index]["grounding_label"] for index in train_indices]
        scaled, _, _ = standardize(feature_matrix, train_indices)
        weights, bias = train_logistic(scaled, labels, train_indices)
        train_probs = predict_probabilities(scaled, weights, bias, train_indices)
        threshold, _ = best_threshold(train_probs, train_gold)
        test_probs = predict_probabilities(scaled, weights, bias, test_indices)
        # Calibrate probabilities around the train-selected threshold so scores are comparable across folds.
        for index, probability in zip(test_indices, test_probs):
            probabilities[index] = probability - threshold
    return probabilities


def main() -> None:
    ensure_dirs()
    output_path = DATA_DIR / "claimcheck_evidence_ranker_metrics.json"
    if not EMBEDDING_CACHE_PATH.exists():
        payload = {
            "status": "blocked",
            "reason": "OpenRouter embedding cache missing; run evaluate_claimcheck_openrouter_embeddings.py first.",
        }
        write_json(output_path, payload)
        print(payload["reason"])
        return

    embeddings = json.loads(EMBEDDING_CACHE_PATH.read_text(encoding="utf-8"))
    rows = read_jsonl(DATA_DIR / "claimcheck_main_weaknesses.jsonl")
    feature_rows = [row_features(row, embeddings) for row in rows]
    feature_names = sorted(feature_rows[0])
    feature_matrix = [[features[name] for name in feature_names] for features in feature_rows]
    labels = [1 if row["grounding_label"] == "Grounded" else 0 for row in rows]
    feature_scores = cross_validated_grounding_probabilities(rows, feature_matrix, labels)

    score_sets = {
        "embedding_max_similarity": [features["max_embedding_similarity"] for features in feature_rows],
        "bm25_max_similarity": [features["max_bm25_similarity"] for features in feature_rows],
        "feature_verifier_probability": feature_scores,
        "candidate_claim_count": [features["candidate_claim_count_log"] for features in feature_rows],
    }
    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "Rank critique weaknesses by likelihood of being paper-grounded within each paper-review group",
        "validation": "Feature-verifier scores are out-of-fold by paper_review_id; lexical and embedding baselines are unsupervised.",
        "warning": "Aggregate diagnostic only; CLAIMCHECK row-level text is not committed because the upstream repository has no detected LICENSE.",
        "row_count": len(rows),
        "group_count": len({row["paper_review_id"] for row in rows}),
        "label_counts": dict(Counter(row["grounding_label"] for row in rows)),
        "metrics": {name: grouped_rank_metrics(rows, scores) for name, scores in score_sets.items()},
    }
    write_json(output_path, payload)
    best = max(payload["metrics"].items(), key=lambda item: (item[1]["map"], item[1]["top1_grounded_rate"]))
    print(f"best_ranker={best[0]} map={best[1]['map']} top1_grounded={best[1]['top1_grounded_rate']}")


if __name__ == "__main__":
    main()
