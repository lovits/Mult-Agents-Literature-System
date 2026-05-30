from __future__ import annotations

import re
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, normalize_ws, read_jsonl, tokenize, write_json, write_jsonl


POSITIVE_CUES = {
    "because",
    "since",
    "therefore",
    "shown",
    "shows",
    "demonstrate",
    "demonstrates",
    "evidence",
    "example",
    "examples",
    "result",
    "results",
    "experiment",
    "experiments",
    "table",
    "figure",
    "empirical",
    "analysis",
    "support",
    "supports",
    "supported",
    "baseline",
    "ablation",
    "metric",
    "score",
}

UNCERTAINTY_CUES = {
    "unclear",
    "not clear",
    "i wonder",
    "i am not sure",
    "missing",
    "lack",
    "lacks",
    "without",
    "no evidence",
    "does not",
    "do not",
    "fails",
    "question",
    "concern",
}


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def find_claim_window(row: dict[str, Any]) -> str:
    review = row["review_text"]
    start = int(row["claim_start"])
    end = int(row["claim_end"])
    before = review[max(0, start - 180) : start]
    claim = review[start:end]
    after = review[end : min(len(review), end + 520)]
    return normalize_ws(f"{before} {claim} {after}")


def cue_count(text: str, cues: set[str]) -> int:
    lower = text.lower()
    return sum(1 for cue in cues if cue in lower)


def punctuation_strength(text: str) -> float:
    return min(text.count(":") + text.count(";") + text.count("(") + text.count(")"), 4) / 4


def baseline_score(row: dict[str, Any]) -> float:
    window = find_claim_window(row)
    claim = row["claim_text"]
    tokens = tokenize(window)
    positive = cue_count(window, POSITIVE_CUES)
    uncertain = cue_count(window, UNCERTAINTY_CUES)
    has_long_followup = len(tokens) >= 70
    has_numeric = bool(re.search(r"\d", window))
    has_because = "because" in window.lower() or "since" in window.lower()
    polarity_bonus = 0.08 if row["polarity"] == "neg" else 0.0
    short_claim_penalty = 0.12 if len(tokenize(claim)) < 8 else 0.0

    score = 0.28
    score += min(positive, 5) * 0.10
    score += punctuation_strength(window) * 0.10
    score += 0.10 if has_long_followup else 0.0
    score += 0.08 if has_numeric else 0.0
    score += 0.10 if has_because else 0.0
    score += polarity_bonus
    score -= min(uncertain, 4) * 0.06
    score -= short_claim_penalty
    return max(0.0, min(1.0, score))


def predict(score: float, threshold: float) -> str:
    return "Supported" if score >= threshold else "Unsupported"


def metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    labels = ("Supported", "Unsupported")
    confusion = {gold: {pred: 0 for pred in labels} for gold in labels}
    predictions = []
    correct = 0
    for row in rows:
        score = baseline_score(row)
        pred = predict(score, threshold)
        gold = row["substantiation_label"]
        confusion[gold][pred] += 1
        correct += int(gold == pred)
        predictions.append(
            {
                "claim_id": row["claim_id"],
                "split": row["split"],
                "gold_label": gold,
                "pred_label": pred,
                "support_score": round(score, 4),
                "claim_text": row["claim_text"],
                "evidence_count": row["evidence_count"],
            }
        )

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
        f1_values.append(f1)

    return {
        "count": len(rows),
        "threshold": round(threshold, 4),
        "accuracy": round(safe_div(correct, len(rows)), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "label_counts": dict(Counter(row["substantiation_label"] for row in rows)),
        "prediction_counts": dict(Counter(item["pred_label"] for item in predictions)),
        "per_label": per_label,
        "confusion": confusion,
        "predictions": predictions,
    }


def select_threshold(train_rows: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    candidates = [round(i / 100, 2) for i in range(20, 91)]
    scored = [(threshold, metrics(train_rows, threshold)) for threshold in candidates]
    return max(scored, key=lambda item: (item[1]["macro_f1"], item[1]["accuracy"]))


def main() -> None:
    ensure_dirs()
    train_path = DATA_DIR / "substanreview_train_claims.jsonl"
    test_path = DATA_DIR / "substanreview_test_claims.jsonl"
    if not train_path.exists() or not test_path.exists():
        raise SystemExit("SubstanReview claim files missing; run prepare_substanreview.py first")

    train_rows = read_jsonl(train_path)
    test_rows = read_jsonl(test_path)
    threshold, train_metrics = select_threshold(train_rows)
    test_metrics = metrics(test_rows, threshold)
    write_jsonl(DATA_DIR / "substanreview_baseline_predictions.jsonl", test_metrics.pop("predictions"))
    train_metrics.pop("predictions")

    payload = {
        "dataset": "SubstanReview",
        "task": "claim-level substantiation detection",
        "baseline": "transparent_context_cue_v0",
        "threshold_selection": "maximize train Macro-F1 over thresholds 0.20..0.90",
        "gold_definition": "Supported iff an Eval span has a paired Jus span with the same polarity and index.",
        "train": train_metrics,
        "test": test_metrics,
    }
    write_json(DATA_DIR / "substanreview_baseline_metrics.json", payload)
    print(
        "test "
        f"count={test_metrics['count']} "
        f"accuracy={test_metrics['accuracy']} "
        f"macro_f1={test_metrics['macro_f1']} "
        f"threshold={threshold:.2f}"
    )


if __name__ == "__main__":
    main()
