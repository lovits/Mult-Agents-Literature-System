from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from common import DATA_DIR, REPORT_DIR, classify_weakness_category, ensure_dirs, read_jsonl, tokenize, write_json, write_jsonl


SOURCE_FILE = "peerreview_bench_expert_annotations.jsonl"
PRED_FILE = "peerreview_bench_baseline_predictions.jsonl"
METRICS_FILE = "peerreview_bench_baseline_metrics.json"
LABEL_FIELDS = {
    "correctness": "correctness_label",
    "significance": "significance_label",
    "evidence": "evidence_label",
}
EVIDENCE_POSITIVE_LABEL = "Requires More"
EVIDENCE_NEGATIVE_LABEL = "Sufficient"
WEAKNESS_CATEGORIES = ("clarity", "experiment", "method", "other", "related_work", "reproducibility", "validity")
EVIDENCE_DEMAND_MARKERS = (
    "not provide",
    "does not provide",
    "no evidence",
    "lack of evidence",
    "lacks evidence",
    "insufficient evidence",
    "needs more",
    "requires more",
    "should provide",
    "should include",
    "missing",
    "unclear",
    "not clear",
    "not supported",
    "unsupported",
    "justify",
    "justification",
    "more details",
    "more detail",
    "additional",
    "ablation",
    "baseline",
    "experiment",
    "evaluation",
    "statistical",
    "significance",
    "dataset",
    "data",
    "analysis",
    "citation",
    "reference",
    "comparison",
)
SUFFICIENT_EVIDENCE_MARKERS = (
    "the paper shows",
    "the authors show",
    "results show",
    "table",
    "figure",
    "appendix",
    "equation",
    "section",
    "reported",
    "demonstrate",
    "demonstrates",
    "empirical",
    "experiment",
)
HEDGE_MARKERS = ("may", "might", "could", "possibly", "perhaps", "unclear", "not clear", "seems", "appears")
STRONG_CLAIM_MARKERS = ("major", "significant", "critical", "serious", "fundamental", "important")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def split_rows(rows: list[dict[str, Any]], label_field: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labeled = [row for row in rows if row[label_field] != "Unlabeled"]
    paper_ids = sorted({row["paper_id"] for row in labeled})
    test_papers = {paper_id for idx, paper_id in enumerate(paper_ids) if idx % 5 == 0}
    train = [row for row in labeled if row["paper_id"] not in test_papers]
    test = [row for row in labeled if row["paper_id"] in test_papers]
    return train, test


def train_majority(rows: list[dict[str, Any]], label_field: str) -> str:
    counts = Counter(row[label_field] for row in rows)
    return counts.most_common(1)[0][0] if counts else "Unlabeled"


def review_item_text(row: dict[str, Any]) -> str:
    return row["review_item"]


def context_text(row: dict[str, Any]) -> str:
    return " ".join(
        [
            row.get("paper_title", ""),
            row.get("paper_excerpt", ""),
            row.get("review_item", ""),
            row.get("annotator_comments", ""),
        ]
    )


def marker_count(text: str, markers: tuple[str, ...]) -> int:
    lower = text.lower()
    return sum(lower.count(marker) for marker in markers)


def evidence_feature_row(row: dict[str, Any]) -> dict[str, float]:
    review = row.get("review_item", "")
    paper_context = " ".join([row.get("paper_title", ""), row.get("paper_excerpt", "")])
    review_tokens = tokenize(review)
    review_token_set = set(review_tokens)
    paper_token_set = set(tokenize(paper_context))
    sentences = [sentence for sentence in re.split(r"[.!?]+", review) if sentence.strip()]
    category = classify_weakness_category(review)

    features = {
        "avg_sentence_len_scaled": safe_div(len(review_tokens), len(sentences)) / 40,
        "evidence_demand_count_log": math.log1p(marker_count(review, EVIDENCE_DEMAND_MARKERS)),
        "has_citation_year": 1.0 if re.search(r"\b(?:19|20)\d{2}\b", review) else 0.0,
        "hedge_count_log": math.log1p(marker_count(review, HEDGE_MARKERS)),
        "mentions_experiment": 1.0
        if re.search(r"\b(experiment|ablation|baseline|evaluation|dataset|metric|result)\b", review.lower())
        else 0.0,
        "mentions_missing": 1.0
        if re.search(r"\b(missing|lack|lacks|insufficient|not provide|no evidence|unclear|not clear)\b", review.lower())
        else 0.0,
        "mentions_table_figure": 1.0
        if re.search(r"\b(table|figure|fig\.|appendix|section)\b", review.lower())
        else 0.0,
        "number_count_log": math.log1p(len(re.findall(r"\d+(?:\.\d+)?", review))),
        "paper_overlap_ratio": safe_div(len(review_token_set & paper_token_set), len(review_token_set)),
        "question_count_log": math.log1p(review.count("?")),
        "quote_count_log": math.log1p(review.count('"') + review.count("'")),
        "review_char_count_log": math.log1p(len(review)),
        "review_token_count_log": math.log1p(len(review_tokens)),
        "sentence_count_log": math.log1p(len(sentences)),
        "strong_claim_count_log": math.log1p(marker_count(review, STRONG_CLAIM_MARKERS)),
        "sufficient_marker_count_log": math.log1p(marker_count(review, SUFFICIENT_EVIDENCE_MARKERS)),
        "url_count_log": math.log1p(len(re.findall(r"https?://|doi\b|arxiv", review.lower()))),
    }
    for known_category in WEAKNESS_CATEGORIES:
        features[f"category_{known_category}"] = 1.0 if category == known_category else 0.0
    return features


def feature_matrix(rows: list[dict[str, Any]], feature_names: list[str] | None = None) -> tuple[list[list[float]], list[str]]:
    feature_rows = [evidence_feature_row(row) for row in rows]
    names = feature_names or sorted(feature_rows[0])
    return [[features[name] for name in names] for features in feature_rows], names


def standardize(matrix: list[list[float]], train_indices: list[int]) -> list[list[float]]:
    feature_count = len(matrix[0])
    means = []
    stds = []
    for feature_index in range(feature_count):
        values = [matrix[index][feature_index] for index in train_indices]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means.append(mean)
        stds.append(math.sqrt(variance) or 1.0)
    return [[(value - means[index]) / stds[index] for index, value in enumerate(row)] for row in matrix]


def train_binary_logistic(
    matrix: list[list[float]],
    labels: list[int],
    train_indices: list[int],
    epochs: int = 1200,
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
        gradients = [0.0] * feature_count
        bias_gradient = 0.0
        for index in train_indices:
            probability = sigmoid(bias + sum(weight * value for weight, value in zip(weights, matrix[index])))
            sample_weight = positive_weight if labels[index] else negative_weight
            error = (probability - labels[index]) * sample_weight
            bias_gradient += error
            for feature_index, value in enumerate(matrix[index]):
                gradients[feature_index] += error * value
        denom = len(train_indices)
        bias -= learning_rate * bias_gradient / denom
        for feature_index in range(feature_count):
            weights[feature_index] -= learning_rate * (gradients[feature_index] / denom + l2 * weights[feature_index])
    return weights, bias


def predict_logistic_probabilities(matrix: list[list[float]], weights: list[float], bias: float) -> list[float]:
    return [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in matrix]


def best_probability_threshold(rows: list[dict[str, Any]], scores: list[float], label_field: str) -> float:
    candidates = sorted({0.0, 1.0, *scores})
    best_threshold = 0.5
    best_key = (-1.0, -1.0, -1.0)
    for threshold in candidates:
        predictions = [EVIDENCE_POSITIVE_LABEL if score >= threshold else EVIDENCE_NEGATIVE_LABEL for score in scores]
        metrics = score_predictions(rows, predictions, label_field)
        positive_recall = metrics["per_label"][EVIDENCE_POSITIVE_LABEL]["recall"]
        positive_f1 = metrics["per_label"][EVIDENCE_POSITIVE_LABEL]["f1"]
        key = (metrics["macro_f1"], positive_recall, positive_f1)
        if key > best_key:
            best_key = key
            best_threshold = threshold
    return best_threshold


def train_evidence_feature_model(
    train: list[dict[str, Any]], test: list[dict[str, Any]], label_field: str
) -> tuple[list[str], dict[str, Any], list[str], list[float], list[dict[str, float]]]:
    all_rows = train + test
    matrix, feature_names = feature_matrix(all_rows)
    train_indices = list(range(len(train)))
    scaled = standardize(matrix, train_indices)
    labels = [1 if row[label_field] == EVIDENCE_POSITIVE_LABEL else 0 for row in all_rows]
    weights, bias = train_binary_logistic(scaled, labels, train_indices)
    probabilities = predict_logistic_probabilities(scaled, weights, bias)
    threshold = best_probability_threshold(train, probabilities[: len(train)], label_field)
    test_probabilities = probabilities[len(train) :]
    predictions = [
        EVIDENCE_POSITIVE_LABEL if probability >= threshold else EVIDENCE_NEGATIVE_LABEL
        for probability in test_probabilities
    ]
    metrics = score_predictions(test, predictions, label_field)
    metrics["probability_threshold"] = round(threshold, 4)
    metrics["feature_count"] = len(feature_names)
    mean_weights = sorted(
        (
            {"feature": name, "weight": round(weight, 4)}
            for name, weight in zip(feature_names, weights)
        ),
        key=lambda item: abs(item["weight"]),
        reverse=True,
    )
    return feature_names, metrics, predictions, test_probabilities, mean_weights[:12]


def train_nb(rows: list[dict[str, Any]], label_field: str, text_getter=review_item_text) -> dict[str, Any]:
    labels = sorted({row[label_field] for row in rows})
    priors = Counter(row[label_field] for row in rows)
    token_counts = {label: Counter() for label in labels}
    token_totals = Counter()
    vocab = set()
    for row in rows:
        label = row[label_field]
        counts = Counter(tokenize(text_getter(row)))
        for token, count in counts.items():
            clipped = min(count, 3)
            token_counts[label][token] += clipped
            token_totals[label] += clipped
            vocab.add(token)
    return {
        "labels": labels,
        "priors": priors,
        "token_counts": token_counts,
        "token_totals": token_totals,
        "vocab": vocab,
        "alpha": 1.0,
        "train_count": len(rows),
    }


def prior_log_probability(label: str, model: dict[str, Any], mode: str) -> float:
    labels = model["labels"]
    if mode == "empirical":
        return math.log((model["priors"][label] + 1) / (model["train_count"] + len(labels)))
    if mode == "inverse_frequency":
        return math.log(model["train_count"] / (len(labels) * model["priors"][label]))
    if mode == "uniform":
        return -math.log(len(labels))
    raise ValueError(f"Unknown prior mode: {mode}")


def predict_nb(row: dict[str, Any], model: dict[str, Any], text_getter=review_item_text, prior_mode: str = "empirical") -> str:
    labels = model["labels"]
    vocab_size = max(1, len(model["vocab"]))
    counts = Counter(tokenize(text_getter(row)))
    best_label = labels[0] if labels else "Unlabeled"
    best_score = -float("inf")
    for label in labels:
        log_prob = prior_log_probability(label, model, prior_mode)
        denom = model["token_totals"][label] + model["alpha"] * vocab_size
        for token, count in counts.items():
            if token not in model["vocab"]:
                continue
            token_prob = (model["token_counts"][label][token] + model["alpha"]) / denom
            log_prob += min(count, 3) * math.log(token_prob)
        if log_prob > best_score:
            best_score = log_prob
            best_label = label
    return best_label


def score_predictions(gold_rows: list[dict[str, Any]], predictions: list[str], label_field: str) -> dict[str, Any]:
    labels = sorted({row[label_field] for row in gold_rows} | set(predictions))
    confusion = {gold: {pred: 0 for pred in labels} for gold in labels}
    correct = 0
    for row, pred in zip(gold_rows, predictions):
        gold = row[label_field]
        confusion[gold][pred] += 1
        correct += int(gold == pred)

    per_label = {}
    f1_values = []
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        support = sum(confusion[label].values())
        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }
        if support:
            f1_values.append(f1)

    return {
        "count": len(gold_rows),
        "accuracy": round(safe_div(correct, len(gold_rows)), 4),
        "macro_f1": round(safe_div(sum(f1_values), len(f1_values)), 4),
        "label_counts": dict(Counter(row[label_field] for row in gold_rows)),
        "prediction_counts": dict(Counter(predictions)),
        "per_label": per_label,
        "confusion": confusion,
    }


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run prepare_peerreview_bench.py first")
    rows = read_jsonl(source_path)

    metrics = {
        "status": "ok",
        "dataset": "prometheus-eval/peerreview-bench",
        "source_file": SOURCE_FILE,
        "row_count": len(rows),
        "tasks": {},
    }
    predictions_out = []
    for task_name, label_field in LABEL_FIELDS.items():
        train, test = split_rows(rows, label_field)
        if not train or not test:
            metrics["tasks"][task_name] = {
                "status": "skipped",
                "reason": f"Not enough labeled rows for {label_field}",
                "labeled_rows": len(train) + len(test),
            }
            continue

        majority_label = train_majority(train, label_field)
        majority_preds = [majority_label for _ in test]
        nb_model = train_nb(train, label_field, review_item_text)
        nb_preds = [predict_nb(row, nb_model, review_item_text) for row in test]
        balanced_nb_preds = [
            predict_nb(row, nb_model, review_item_text, prior_mode="inverse_frequency") for row in test
        ]
        context_nb_model = train_nb(train, label_field, context_text)
        context_nb_preds = [predict_nb(row, context_nb_model, context_text) for row in test]
        balanced_context_nb_preds = [
            predict_nb(row, context_nb_model, context_text, prior_mode="inverse_frequency") for row in test
        ]
        evidence_feature_names: list[str] = []
        evidence_feature_preds: list[str] = []
        evidence_feature_scores: list[float] = []
        evidence_feature_weights: list[dict[str, float]] = []
        evidence_feature_metrics: dict[str, Any] | None = None
        if task_name == "evidence":
            (
                evidence_feature_names,
                evidence_feature_metrics,
                evidence_feature_preds,
                evidence_feature_scores,
                evidence_feature_weights,
            ) = train_evidence_feature_model(train, test, label_field)

        baselines = {
            "majority_train_label": score_predictions(test, majority_preds, label_field),
            "multinomial_naive_bayes_v0": score_predictions(test, nb_preds, label_field),
            "balanced_multinomial_naive_bayes_v1": score_predictions(test, balanced_nb_preds, label_field),
            "context_multinomial_naive_bayes_v1": score_predictions(test, context_nb_preds, label_field),
            "balanced_context_multinomial_naive_bayes_v2": score_predictions(
                test, balanced_context_nb_preds, label_field
            ),
        }
        if evidence_feature_metrics is not None:
            baselines["evidence_aware_feature_logistic_v1"] = evidence_feature_metrics

        task_payload = {
            "status": "ok",
            "label_field": label_field,
            "split_rule": "grouped_by_paper_id_modulo_5",
            "train_count": len(train),
            "test_count": len(test),
            "train_paper_count": len({row["paper_id"] for row in train}),
            "test_paper_count": len({row["paper_id"] for row in test}),
            "train_label_counts": dict(Counter(row[label_field] for row in train)),
            "baselines": baselines,
        }
        if task_name == "evidence":
            task_payload["evidence_aware_features"] = {
                "feature_names": evidence_feature_names,
                "mean_feature_weights": evidence_feature_weights,
                "positive_label": EVIDENCE_POSITIVE_LABEL,
                "negative_label": EVIDENCE_NEGATIVE_LABEL,
                "method": "balanced binary logistic regression on review/context evidence proxy features",
            }
        metrics["tasks"][task_name] = task_payload

        for index, (row, majority_pred, nb_pred, balanced_nb_pred, context_nb_pred, balanced_context_nb_pred) in enumerate(
            zip(
            test,
            majority_preds,
            nb_preds,
            balanced_nb_preds,
            context_nb_preds,
            balanced_context_nb_preds,
            )
        ):
            prediction_row = {
                "task": task_name,
                "row_index": row["row_index"],
                "paper_id": row["paper_id"],
                "gold_label": row[label_field],
                "majority_pred": majority_pred,
                "nb_pred": nb_pred,
                "balanced_nb_pred": balanced_nb_pred,
                "context_nb_pred": context_nb_pred,
                "balanced_context_nb_pred": balanced_context_nb_pred,
                "review_item": row["review_item"],
            }
            if task_name == "evidence":
                prediction_row["evidence_feature_pred"] = evidence_feature_preds[index]
                prediction_row["evidence_feature_probability"] = round(evidence_feature_scores[index], 4)
            predictions_out.append(prediction_row)

    write_json(DATA_DIR / METRICS_FILE, metrics)
    write_jsonl(DATA_DIR / PRED_FILE, predictions_out)

    lines = [
        "# PeerReview Bench Ready-label Baseline",
        "",
        "This experiment uses an external dataset with existing expert annotations, so no new manual labels are required.",
        "",
        "- Dataset: https://huggingface.co/datasets/prometheus-eval/peerreview-bench",
        "- License: CC-BY-4.0",
        f"- Local rows used: {len(rows)}",
        "",
        "| Task | Train | Test | Majority Macro-F1 | Review NB Macro-F1 | Balanced Review NB Macro-F1 | Context NB Macro-F1 | Balanced Context NB Macro-F1 | Evidence-aware Feature Macro-F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for task_name, task in metrics["tasks"].items():
        if task["status"] != "ok":
            lines.append(f"| {task_name} | 0 | 0 | - | - | - | - | - |")
            continue
        majority = task["baselines"]["majority_train_label"]
        nb = task["baselines"]["multinomial_naive_bayes_v0"]
        balanced_nb = task["baselines"]["balanced_multinomial_naive_bayes_v1"]
        context_nb = task["baselines"]["context_multinomial_naive_bayes_v1"]
        balanced_context_nb = task["baselines"]["balanced_context_multinomial_naive_bayes_v2"]
        evidence_feature = task["baselines"].get("evidence_aware_feature_logistic_v1")
        evidence_feature_value = evidence_feature["macro_f1"] if evidence_feature else "-"
        lines.append(
            f"| {task_name} | {task['train_count']} | {task['test_count']} | "
            f"{majority['macro_f1']} | {nb['macro_f1']} | {balanced_nb['macro_f1']} | "
            f"{context_nb['macro_f1']} | {balanced_context_nb['macro_f1']} | {evidence_feature_value} |"
        )
    lines.extend(
        [
            "",
            "Split rule: grouped by `paper_id` with a deterministic 80/20 paper-level split, so rows from the same paper do not appear in both train and test.",
            "",
            "## Balanced Context NB Per-label Recall",
            "",
            "| Task | Label | Support | Recall | F1 |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for task_name, task in metrics["tasks"].items():
        if task["status"] != "ok":
            continue
        per_label_source = task["baselines"].get(
            "evidence_aware_feature_logistic_v1",
            task["baselines"]["balanced_context_multinomial_naive_bayes_v2"],
        )
        per_label = per_label_source["per_label"]
        for label, values in per_label.items():
            lines.append(f"| {task_name} | {label} | {values['support']} | {values['recall']} | {values['f1']} |")
    evidence_task = metrics["tasks"].get("evidence", {})
    if evidence_task.get("status") == "ok" and "evidence_aware_features" in evidence_task:
        evidence_feature_metrics = evidence_task["baselines"]["evidence_aware_feature_logistic_v1"]
        previous_evidence = evidence_task["baselines"]["balanced_context_multinomial_naive_bayes_v2"]
        lines.extend(
            [
                "",
                "## Evidence-aware Feature Baseline",
                "",
                "| Model | Macro-F1 | Accuracy | Requires More recall | Requires More F1 | Threshold |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
                f"| Balanced context NB | {previous_evidence['macro_f1']} | {previous_evidence['accuracy']} | "
                f"{previous_evidence['per_label'][EVIDENCE_POSITIVE_LABEL]['recall']} | "
                f"{previous_evidence['per_label'][EVIDENCE_POSITIVE_LABEL]['f1']} | - |",
                f"| Evidence-aware feature logistic | {evidence_feature_metrics['macro_f1']} | "
                f"{evidence_feature_metrics['accuracy']} | "
                f"{evidence_feature_metrics['per_label'][EVIDENCE_POSITIVE_LABEL]['recall']} | "
                f"{evidence_feature_metrics['per_label'][EVIDENCE_POSITIVE_LABEL]['f1']} | "
                f"{evidence_feature_metrics['probability_threshold']} |",
                "",
                "Top feature weights:",
                "",
                "| Feature | Weight |",
                "| --- | ---: |",
            ]
        )
        for item in evidence_task["evidence_aware_features"]["mean_feature_weights"]:
            lines.append(f"| `{item['feature']}` | {item['weight']} |")
    lines.extend(
        [
            "",
            "## Best Macro-F1 Baseline By Task",
            "",
            "| Task | Best baseline | Macro-F1 | Accuracy | Note |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for task_name, task in metrics["tasks"].items():
        if task["status"] != "ok":
            continue
        best_name, best_values = max(task["baselines"].items(), key=lambda item: item[1]["macro_f1"])
        note = "review item priority signal" if task_name == "significance" else "context helps verifier signal"
        lines.append(f"| {task_name} | {best_name} | {best_values['macro_f1']} | {best_values['accuracy']} | {note} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a direct no-manual-label verifier/ranker-quality baseline aligned with the thesis modules.",
            "- `correctness`, `significance`, and `evidence` map to verifier correctness, ranker priority, and evidence-grounding dimensions.",
            "- The grouped split is stricter than row-level random/modulo splitting because it blocks same-paper leakage.",
            "- Context NB concatenates paper title, short paper excerpt, review item, and annotator comments. It is still a simple lexical floor, not a final verifier.",
            "- Balanced NB uses an inverse-frequency prior to expose minority-class recall trade-offs; it should be reported with Macro-F1 and per-label recall, not accuracy alone.",
            "- The current baseline is intentionally transparent; stronger LLM or embedding models can be added after this floor is stable.",
        ]
    )
    (REPORT_DIR / "peerreview_bench_baseline_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {DATA_DIR / METRICS_FILE}")
    print(f"Wrote {REPORT_DIR / 'peerreview_bench_baseline_report.md'}")


if __name__ == "__main__":
    main()
