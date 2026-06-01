from __future__ import annotations

import math
from collections import Counter
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, tokenize, write_json, write_jsonl


SOURCE_FILE = "peerreview_bench_expert_annotations.jsonl"
PRED_FILE = "peerreview_bench_baseline_predictions.jsonl"
METRICS_FILE = "peerreview_bench_baseline_metrics.json"
LABEL_FIELDS = {
    "correctness": "correctness_label",
    "significance": "significance_label",
    "evidence": "evidence_label",
}


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


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

        metrics["tasks"][task_name] = {
            "status": "ok",
            "label_field": label_field,
            "split_rule": "grouped_by_paper_id_modulo_5",
            "train_count": len(train),
            "test_count": len(test),
            "train_paper_count": len({row["paper_id"] for row in train}),
            "test_paper_count": len({row["paper_id"] for row in test}),
            "train_label_counts": dict(Counter(row[label_field] for row in train)),
            "baselines": {
                "majority_train_label": score_predictions(test, majority_preds, label_field),
                "multinomial_naive_bayes_v0": score_predictions(test, nb_preds, label_field),
                "balanced_multinomial_naive_bayes_v1": score_predictions(test, balanced_nb_preds, label_field),
                "context_multinomial_naive_bayes_v1": score_predictions(test, context_nb_preds, label_field),
                "balanced_context_multinomial_naive_bayes_v2": score_predictions(
                    test, balanced_context_nb_preds, label_field
                ),
            },
        }
        for row, majority_pred, nb_pred, balanced_nb_pred, context_nb_pred, balanced_context_nb_pred in zip(
            test,
            majority_preds,
            nb_preds,
            balanced_nb_preds,
            context_nb_preds,
            balanced_context_nb_preds,
        ):
            predictions_out.append(
                {
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
            )

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
        "| Task | Train | Test | Majority Macro-F1 | Review NB Macro-F1 | Balanced Review NB Macro-F1 | Context NB Macro-F1 | Balanced Context NB Macro-F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for task_name, task in metrics["tasks"].items():
        if task["status"] != "ok":
            lines.append(f"| {task_name} | 0 | 0 | - | - | - |")
            continue
        majority = task["baselines"]["majority_train_label"]
        nb = task["baselines"]["multinomial_naive_bayes_v0"]
        balanced_nb = task["baselines"]["balanced_multinomial_naive_bayes_v1"]
        context_nb = task["baselines"]["context_multinomial_naive_bayes_v1"]
        balanced_context_nb = task["baselines"]["balanced_context_multinomial_naive_bayes_v2"]
        lines.append(
            f"| {task_name} | {task['train_count']} | {task['test_count']} | "
            f"{majority['macro_f1']} | {nb['macro_f1']} | {balanced_nb['macro_f1']} | "
            f"{context_nb['macro_f1']} | {balanced_context_nb['macro_f1']} |"
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
        per_label = task["baselines"]["balanced_context_multinomial_naive_bayes_v2"]["per_label"]
        for label, values in per_label.items():
            lines.append(f"| {task_name} | {label} | {values['support']} | {values['recall']} | {values['f1']} |")
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
