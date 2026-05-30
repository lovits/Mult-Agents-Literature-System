from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, classify_weakness_category, ensure_dirs, read_jsonl, tokenize, write_json
from evaluate_claimcheck_openrouter_verifier import vector_cosine
from evaluate_claimcheck_retrieval import prepare_row


EMBEDDING_CACHE_PATH = DATA_DIR / "claimcheck_openrouter_embedding_cache.json"
LABELS = ("Grounded", "Ungrounded")
WEAKNESS_TYPES = ("clarity", "experiment", "method", "other", "related_work", "reproducibility", "validity")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def classification_metrics(gold: list[str], pred: list[str]) -> dict[str, Any]:
    confusion = {label: {other: 0 for other in LABELS} for label in LABELS}
    correct = 0
    for expected, actual in zip(gold, pred):
        confusion[expected][actual] += 1
        correct += int(expected == actual)

    per_label = {}
    f1_values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(confusion[label].values()),
        }
        f1_values.append(f1)

    return {
        "count": len(gold),
        "accuracy": round(safe_div(correct, len(gold)), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "per_label": per_label,
        "confusion": confusion,
    }


def best_threshold(scores: list[float], labels: list[str]) -> tuple[float, dict[str, Any]]:
    candidates = sorted({0.0, 1.0, *scores})
    best = (0.5, {"macro_f1": -1.0, "accuracy": -1.0})
    for threshold in candidates:
        pred = ["Grounded" if score >= threshold else "Ungrounded" for score in scores]
        metrics = classification_metrics(labels, pred)
        if (metrics["macro_f1"], metrics["accuracy"]) > (best[1]["macro_f1"], best[1]["accuracy"]):
            best = (threshold, metrics)
    return best


def top_stats(values: list[float], k: int) -> tuple[float, float]:
    top = sorted(values, reverse=True)[:k]
    if not top:
        return 0.0, 0.0
    return max(top), sum(top) / len(top)


def row_features(row: dict[str, Any], embeddings: dict[str, list[float]]) -> dict[str, float]:
    prepared = prepare_row(row)
    candidate_claims = row["candidate_claims"]
    weakness_vec = embeddings[row["weakness_text"]]
    embedding_scores = [vector_cosine(weakness_vec, embeddings[claim]) for claim in candidate_claims]
    sorted_embedding_scores = sorted(embedding_scores, reverse=True)
    max_embedding, mean_top3_embedding = top_stats(embedding_scores, 3)
    _, mean_top5_embedding = top_stats(embedding_scores, 5)
    gap_top1_top2 = (
        sorted_embedding_scores[0] - sorted_embedding_scores[1]
        if len(sorted_embedding_scores) >= 2
        else sorted_embedding_scores[0] if sorted_embedding_scores else 0.0
    )

    normalized_scores = list(prepared["_normalized_scores"].values())
    max_by_name = {
        name: max((scores[name] for scores in normalized_scores), default=0.0)
        for name in ("lexical", "char_ngram", "tfidf", "bm25")
    }
    weakness_tokens = tokenize(row["weakness_text"])
    features = {
        "max_embedding_similarity": max_embedding,
        "mean_top3_embedding_similarity": mean_top3_embedding,
        "mean_top5_embedding_similarity": mean_top5_embedding,
        "gap_top1_top2_embedding": gap_top1_top2,
        "max_lexical_similarity": max_by_name["lexical"],
        "max_char_ngram_similarity": max_by_name["char_ngram"],
        "max_tfidf_similarity": max_by_name["tfidf"],
        "max_bm25_similarity": max_by_name["bm25"],
        "candidate_claim_count_log": math.log1p(row["candidate_claim_count"]),
        "weakness_token_count_log": math.log1p(len(weakness_tokens)),
    }
    weakness_type_set = {classify_weakness_category(row["weakness_text"])}
    for weakness_type in WEAKNESS_TYPES:
        features[f"type_{weakness_type}"] = 1.0 if weakness_type in weakness_type_set else 0.0
    return features


def make_group_folds(rows: list[dict[str, Any]], fold_count: int = 5) -> list[list[int]]:
    group_to_indices: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        group_to_indices[row["paper_review_id"]].append(index)

    groups = []
    for group_id, indices in group_to_indices.items():
        counts = Counter(rows[index]["grounding_label"] for index in indices)
        groups.append((group_id, indices, counts))
    groups.sort(key=lambda item: (item[2]["Ungrounded"], len(item[1]), item[2]["Grounded"]), reverse=True)

    folds: list[list[int]] = [[] for _ in range(fold_count)]
    fold_counts = [Counter() for _ in range(fold_count)]
    for _, indices, counts in groups:
        if counts["Ungrounded"]:
            best_fold = min(
                range(fold_count),
                key=lambda fold: (
                    fold_counts[fold]["Ungrounded"],
                    len(folds[fold]),
                    fold_counts[fold]["Grounded"],
                ),
            )
        else:
            best_fold = min(
                range(fold_count),
                key=lambda fold: (
                    len(folds[fold]),
                    fold_counts[fold]["Grounded"],
                ),
            )
        folds[best_fold].extend(indices)
        fold_counts[best_fold].update(counts)
    return folds


def standardize(
    matrix: list[list[float]],
    train_indices: list[int],
) -> tuple[list[list[float]], list[float], list[float]]:
    feature_count = len(matrix[0])
    means = []
    stds = []
    for feature_index in range(feature_count):
        values = [matrix[index][feature_index] for index in train_indices]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means.append(mean)
        stds.append(math.sqrt(variance) or 1.0)
    scaled = [[(value - means[index]) / stds[index] for index, value in enumerate(row)] for row in matrix]
    return scaled, means, stds


def train_logistic(
    matrix: list[list[float]],
    labels: list[int],
    train_indices: list[int],
    epochs: int = 900,
    learning_rate: float = 0.08,
    l2: float = 0.02,
) -> tuple[list[float], float]:
    feature_count = len(matrix[0])
    weights = [0.0] * feature_count
    bias = 0.0
    positive = sum(labels[index] for index in train_indices)
    negative = len(train_indices) - positive
    positive_weight = safe_div(len(train_indices), 2 * positive)
    negative_weight = safe_div(len(train_indices), 2 * negative)

    for _ in range(epochs):
        weight_grad = [0.0] * feature_count
        bias_grad = 0.0
        for index in train_indices:
            row = matrix[index]
            target = labels[index]
            logit = bias + sum(weight * value for weight, value in zip(weights, row))
            prob = sigmoid(logit)
            sample_weight = positive_weight if target else negative_weight
            error = (prob - target) * sample_weight
            bias_grad += error
            for feature_index, value in enumerate(row):
                weight_grad[feature_index] += error * value
        denom = len(train_indices)
        bias -= learning_rate * bias_grad / denom
        for feature_index in range(feature_count):
            regularized = weight_grad[feature_index] / denom + l2 * weights[feature_index]
            weights[feature_index] -= learning_rate * regularized
    return weights, bias


def predict_probabilities(matrix: list[list[float]], weights: list[float], bias: float, indices: list[int]) -> list[float]:
    return [sigmoid(bias + sum(weight * value for weight, value in zip(weights, matrix[index]))) for index in indices]


def mean_feature_weights(feature_names: list[str], fold_weights: list[list[float]]) -> list[dict[str, float]]:
    if not fold_weights:
        return []
    averaged = []
    for feature_index, name in enumerate(feature_names):
        value = sum(weights[feature_index] for weights in fold_weights) / len(fold_weights)
        averaged.append({"feature": name, "mean_weight": round(value, 4)})
    return sorted(averaged, key=lambda item: abs(item["mean_weight"]), reverse=True)


def main() -> None:
    ensure_dirs()
    output_path = DATA_DIR / "claimcheck_feature_verifier_metrics.json"
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
    matrix = [[features[name] for name in feature_names] for features in feature_rows]
    label_names = [row["grounding_label"] for row in rows]
    labels = [1 if label == "Grounded" else 0 for label in label_names]
    folds = make_group_folds(rows)

    logistic_gold: list[str] = []
    logistic_pred: list[str] = []
    majority_gold: list[str] = []
    majority_pred: list[str] = []
    embedding_gold: list[str] = []
    embedding_pred: list[str] = []
    fold_summaries = []
    fold_weights = []

    max_embedding_scores = [features["max_embedding_similarity"] for features in feature_rows]
    all_indices = set(range(len(rows)))
    for fold_index, test_indices in enumerate(folds, start=1):
        train_indices = sorted(all_indices - set(test_indices))
        train_gold = [label_names[index] for index in train_indices]
        test_gold = [label_names[index] for index in test_indices]

        majority_label = Counter(train_gold).most_common(1)[0][0]
        majority_gold.extend(test_gold)
        majority_pred.extend([majority_label] * len(test_indices))

        threshold, _ = best_threshold([max_embedding_scores[index] for index in train_indices], train_gold)
        embedding_fold_pred = [
            "Grounded" if max_embedding_scores[index] >= threshold else "Ungrounded"
            for index in test_indices
        ]
        embedding_gold.extend(test_gold)
        embedding_pred.extend(embedding_fold_pred)

        scaled, _, _ = standardize(matrix, train_indices)
        weights, bias = train_logistic(scaled, labels, train_indices)
        train_probs = predict_probabilities(scaled, weights, bias, train_indices)
        probability_threshold, _ = best_threshold(train_probs, train_gold)
        test_probs = predict_probabilities(scaled, weights, bias, test_indices)
        logistic_fold_pred = [
            "Grounded" if probability >= probability_threshold else "Ungrounded"
            for probability in test_probs
        ]
        logistic_gold.extend(test_gold)
        logistic_pred.extend(logistic_fold_pred)
        fold_weights.append(weights)
        fold_summaries.append(
            {
                "fold": fold_index,
                "test_count": len(test_indices),
                "test_label_counts": dict(Counter(test_gold)),
                "embedding_threshold": round(threshold, 4),
                "logistic_probability_threshold": round(probability_threshold, 4),
                "feature_verifier": classification_metrics(test_gold, logistic_fold_pred),
            }
        )

    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "Grounded/Ungrounded verifier from retrieval, embedding, and metadata features",
        "validation": "5-fold grouped cross-validation by paper_review_id on the CLAIMCHECK main split",
        "warning": "Diagnostic experiment only; CLAIMCHECK row-level text is not committed because the upstream repository has no detected LICENSE.",
        "leakage_controls": [
            "Grouped cross-validation keeps paper_review_id groups out of both train and test folds.",
            "Gold target claim counts, annotation confidence, target claim text, and human weakness type annotations are excluded from features.",
            "Weakness category features are inferred from weakness text with the local rule-based classifier.",
        ],
        "row_count": len(rows),
        "group_count": len({row["paper_review_id"] for row in rows}),
        "label_counts": dict(Counter(label_names)),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "baselines": {
            "train_fold_majority": classification_metrics(majority_gold, majority_pred),
            "train_fold_embedding_threshold": classification_metrics(embedding_gold, embedding_pred),
        },
        "feature_verifier": classification_metrics(logistic_gold, logistic_pred),
        "folds": fold_summaries,
        "mean_feature_weights": mean_feature_weights(feature_names, fold_weights)[:12],
    }
    write_json(output_path, payload)
    print(
        "feature_verifier "
        f"macro_f1={payload['feature_verifier']['macro_f1']} "
        f"accuracy={payload['feature_verifier']['accuracy']} "
        f"ungrounded_f1={payload['feature_verifier']['per_label']['Ungrounded']['f1']}"
    )


if __name__ == "__main__":
    main()
