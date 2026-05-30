from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from statistics import mean, pstdev
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json


LABELS = ("Reject", "Accept")
CATEGORIES = ("clarity", "experiment", "method", "other", "related_work", "reproducibility", "validity")
SILVER_LABELS = ("Supported", "Partially Supported", "Mentioned but Not Problem", "Generic / Vague", "Unsupported")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def read_manifest() -> list[dict[str, str]]:
    with (DATA_DIR / "manifest_clean.csv").open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def classification_metrics(gold: list[str], pred: list[str], probabilities: list[float]) -> dict[str, Any]:
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
        "roc_auc": round(roc_auc(gold, probabilities), 4),
        "per_label": per_label,
        "confusion": confusion,
    }


def roc_auc(gold: list[str], probabilities: list[float]) -> float:
    pairs = sorted(zip(probabilities, gold), key=lambda item: item[0])
    positive_count = sum(1 for _, label in pairs if label == "Accept")
    negative_count = len(pairs) - positive_count
    if not positive_count or not negative_count:
        return 0.0

    rank_sum = 0.0
    index = 0
    while index < len(pairs):
        end = index + 1
        while end < len(pairs) and pairs[end][0] == pairs[index][0]:
            end += 1
        average_rank = (index + 1 + end) / 2
        rank_sum += average_rank * sum(1 for _, label in pairs[index:end] if label == "Accept")
        index = end
    return (rank_sum - positive_count * (positive_count + 1) / 2) / (positive_count * negative_count)


def best_threshold(probabilities: list[float], labels: list[str]) -> float:
    candidates = sorted({0.0, 0.5, 1.0, *probabilities})
    best = (0.5, -1.0, -1.0)
    for threshold in candidates:
        pred = ["Accept" if prob >= threshold else "Reject" for prob in probabilities]
        metrics = classification_metrics(labels, pred, probabilities)
        score = (metrics["macro_f1"], metrics["accuracy"])
        if score > (best[1], best[2]):
            best = (threshold, metrics["macro_f1"], metrics["accuracy"])
    return best[0]


def make_stratified_folds(rows: list[dict[str, Any]], fold_count: int = 5) -> list[list[int]]:
    by_label: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_label[row["decision"]].append(index)
    for indices in by_label.values():
        indices.sort(key=lambda index: rows[index]["paper_id"])

    folds: list[list[int]] = [[] for _ in range(fold_count)]
    for label in LABELS:
        for offset, index in enumerate(by_label[label]):
            folds[offset % fold_count].append(index)
    return [sorted(fold) for fold in folds]


def standardize(matrix: list[list[float]], train_indices: list[int]) -> list[list[float]]:
    feature_count = len(matrix[0])
    means = []
    stds = []
    for feature_index in range(feature_count):
        values = [matrix[index][feature_index] for index in train_indices]
        feature_mean = sum(values) / len(values)
        variance = sum((value - feature_mean) ** 2 for value in values) / len(values)
        means.append(feature_mean)
        stds.append(math.sqrt(variance) or 1.0)
    return [[(value - means[index]) / stds[index] for index, value in enumerate(row)] for row in matrix]


def train_logistic(
    matrix: list[list[float]],
    labels: list[int],
    train_indices: list[int],
    epochs: int = 900,
    learning_rate: float = 0.08,
    l2: float = 0.03,
) -> tuple[list[float], float]:
    feature_count = len(matrix[0])
    weights = [0.0] * feature_count
    bias = 0.0
    positive = sum(labels[index] for index in train_indices)
    negative = len(train_indices) - positive
    positive_weight = safe_div(len(train_indices), 2 * positive)
    negative_weight = safe_div(len(train_indices), 2 * negative)
    for _ in range(epochs):
        gradients = [0.0] * feature_count
        bias_gradient = 0.0
        for index in train_indices:
            row = matrix[index]
            target = labels[index]
            prob = sigmoid(bias + sum(weight * value for weight, value in zip(weights, row)))
            sample_weight = positive_weight if target else negative_weight
            error = (prob - target) * sample_weight
            bias_gradient += error
            for feature_index, value in enumerate(row):
                gradients[feature_index] += error * value
        denom = len(train_indices)
        bias -= learning_rate * bias_gradient / denom
        for feature_index in range(feature_count):
            weights[feature_index] -= learning_rate * (gradients[feature_index] / denom + l2 * weights[feature_index])
    return weights, bias


def predict(matrix: list[list[float]], weights: list[float], bias: float, indices: list[int]) -> list[float]:
    return [sigmoid(bias + sum(weight * value for weight, value in zip(weights, matrix[index]))) for index in indices]


def weakness_features(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["paper_id"]].append(row)

    features = {}
    for paper_id, items in grouped.items():
        total = len(items)
        category_counts = Counter(item["category_rule"] for item in items)
        section_counts = Counter(item["source_section"] for item in items)
        severity_counts = Counter(item["severity_hint"] for item in items)
        char_lengths = [int(item["char_len"]) for item in items]
        row = {
            "weakness_count_log": math.log1p(total),
            "weakness_mean_chars_log": math.log1p(sum(char_lengths) / len(char_lengths)),
            "question_ratio": safe_div(section_counts["questions"], total),
            "major_ratio": safe_div(severity_counts["major"], total),
        }
        for category in CATEGORIES:
            row[f"weakness_category_{category}_ratio"] = safe_div(category_counts[category], total)
        features[paper_id] = row
    return features


def silver_features(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["paper_id"]].append(row)

    features = {}
    for paper_id, items in grouped.items():
        total = len(items)
        label_counts = Counter(item["silver_label"] for item in items)
        support_scores = [float(item["silver_support_score"]) for item in items]
        row = {
            "silver_count_log": math.log1p(total),
            "silver_support_mean": sum(support_scores) / len(support_scores),
            "silver_support_max": max(support_scores),
            "silver_support_min": min(support_scores),
        }
        for label in SILVER_LABELS:
            key = label.lower().replace(" / ", "_").replace(" ", "_")
            row[f"silver_label_{key}_ratio"] = safe_div(label_counts[label], total)
        features[paper_id] = row
    return features


def base_metadata_features(row: dict[str, str]) -> dict[str, float]:
    title_tokens = tokenize(row["title"])
    return {
        "keyword_score": float(row["keyword_score"]),
        "keyword_hit_count": float(len([item for item in row["keyword_hits"].split(";") if item.strip()])),
        "markdown_chars_log": math.log1p(float(row["markdown_chars"])),
        "review_text_chars_log": math.log1p(float(row["review_text_chars"])),
        "review_count": float(row["review_count_manifest"]),
        "direct_replies_count": float(row["direct_replies_count_json"]),
        "title_token_count_log": math.log1p(len(title_tokens)),
    }


def merge_features(*parts: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for part in parts:
        merged.update(part)
    return merged


def evaluate_feature_set(rows: list[dict[str, Any]], feature_rows: list[dict[str, float]], name: str) -> dict[str, Any]:
    feature_names = sorted({key for row in feature_rows for key in row})
    matrix = [[row.get(feature, 0.0) for feature in feature_names] for row in feature_rows]
    labels = [1 if row["decision"] == "Accept" else 0 for row in rows]
    label_names = [row["decision"] for row in rows]
    folds = make_stratified_folds(rows)
    all_indices = set(range(len(rows)))

    out_gold: list[str] = []
    out_pred: list[str] = []
    out_prob: list[float] = []
    fold_metrics = []
    for fold_number, test_indices in enumerate(folds, start=1):
        train_indices = sorted(all_indices - set(test_indices))
        scaled = standardize(matrix, train_indices)
        weights, bias = train_logistic(scaled, labels, train_indices)
        train_prob = predict(scaled, weights, bias, train_indices)
        train_labels = [label_names[index] for index in train_indices]
        threshold = best_threshold(train_prob, train_labels)
        test_prob = predict(scaled, weights, bias, test_indices)
        test_gold = [label_names[index] for index in test_indices]
        test_pred = ["Accept" if prob >= threshold else "Reject" for prob in test_prob]
        out_gold.extend(test_gold)
        out_pred.extend(test_pred)
        out_prob.extend(test_prob)
        fold_metrics.append(
            {
                "fold": fold_number,
                "threshold": round(threshold, 4),
                "test_label_counts": dict(Counter(test_gold)),
                "metrics": classification_metrics(test_gold, test_pred, test_prob),
            }
        )

    aggregate = classification_metrics(out_gold, out_pred, out_prob)
    return {
        "name": name,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "aggregate": aggregate,
        "fold_macro_f1_mean": round(mean(fold["metrics"]["macro_f1"] for fold in fold_metrics), 4),
        "fold_macro_f1_std": round(pstdev(fold["metrics"]["macro_f1"] for fold in fold_metrics), 4),
        "folds": fold_metrics,
    }


def majority_baseline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    folds = make_stratified_folds(rows)
    all_indices = set(range(len(rows)))
    gold: list[str] = []
    pred: list[str] = []
    prob: list[float] = []
    fold_metrics = []
    for test_indices in folds:
        train_indices = sorted(all_indices - set(test_indices))
        majority = Counter(rows[index]["decision"] for index in train_indices).most_common(1)[0][0]
        accept_rate = safe_div(sum(1 for index in train_indices if rows[index]["decision"] == "Accept"), len(train_indices))
        fold_gold = []
        fold_pred = []
        fold_prob = []
        for index in test_indices:
            fold_gold.append(rows[index]["decision"])
            fold_pred.append(majority)
            fold_prob.append(accept_rate)
        gold.extend(fold_gold)
        pred.extend(fold_pred)
        prob.extend(fold_prob)
        fold_metrics.append(classification_metrics(fold_gold, fold_pred, fold_prob))
    return {
        "name": "majority",
        "feature_count": 0,
        "feature_names": [],
        "aggregate": classification_metrics(gold, pred, prob),
        "fold_macro_f1_mean": round(mean(item["macro_f1"] for item in fold_metrics), 4),
        "fold_macro_f1_std": round(pstdev(item["macro_f1"] for item in fold_metrics), 4),
        "folds": [],
    }


def main() -> None:
    ensure_dirs()
    manifest = read_manifest()
    weakness_by_paper = weakness_features(read_jsonl(DATA_DIR / "human_weaknesses.jsonl"))
    silver_by_paper = silver_features(read_jsonl(DATA_DIR / "weakness_evidence_silver.jsonl"))
    rows = [
        {
            "paper_id": row["paper_id"],
            "title": row["title"],
            "decision": row["decision"],
            "metadata": base_metadata_features(row),
            "weakness": weakness_by_paper.get(row["paper_id"], {}),
            "silver": silver_by_paper.get(row["paper_id"], {}),
        }
        for row in manifest
    ]

    feature_sets = {
        "metadata": [row["metadata"] for row in rows],
        "human_weakness_upper_bound": [merge_features(row["weakness"]) for row in rows],
        "silver_evidence_proxy": [merge_features(row["silver"]) for row in rows],
        "metadata_plus_human_weakness": [merge_features(row["metadata"], row["weakness"]) for row in rows],
        "metadata_plus_silver_evidence": [merge_features(row["metadata"], row["silver"]) for row in rows],
        "fusion_all_proxy": [merge_features(row["metadata"], row["weakness"], row["silver"]) for row in rows],
    }
    results = [majority_baseline(rows)]
    results.extend(evaluate_feature_set(rows, features, name) for name, features in feature_sets.items())
    best = max(results, key=lambda item: (item["aggregate"]["macro_f1"], item["aggregate"]["accuracy"]))
    payload = {
        "status": "ok",
        "dataset": "Local PRISM/OpenReview ICLR 2024 sample",
        "task": "Exploratory Accept/Reject classification from metadata, human-review weakness, and silver evidence features",
        "warning": "Exploratory only: human weakness features are an upper-bound proxy, and silver evidence labels are rule-generated debugging labels, not final human gold.",
        "validation": "5-fold stratified cross-validation over 50 papers, with balanced Accept/Reject folds.",
        "paper_count": len(rows),
        "decision_counts": dict(Counter(row["decision"] for row in rows)),
        "silver_feature_coverage_papers": len(silver_by_paper),
        "best_method": best["name"],
        "results": results,
    }
    write_json(DATA_DIR / "local_decision_classifier_metrics.json", payload)
    print(
        "local_decision_classifier "
        f"best={best['name']} macro_f1={best['aggregate']['macro_f1']} "
        f"accuracy={best['aggregate']['accuracy']} auc={best['aggregate']['roc_auc']}"
    )


if __name__ == "__main__":
    main()
