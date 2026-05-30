from __future__ import annotations

import re
import math
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


def prediction_metrics(rows: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    labels = ("Supported", "Unsupported")
    confusion = {gold: {pred: 0 for pred in labels} for gold in labels}
    correct = 0
    for row, prediction in zip(rows, predictions):
        pred = prediction["pred_label"]
        gold = row["substantiation_label"]
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
        f1_values.append(f1)

    return {
        "count": len(rows),
        "accuracy": round(safe_div(correct, len(rows)), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "label_counts": dict(Counter(row["substantiation_label"] for row in rows)),
        "prediction_counts": dict(Counter(item["pred_label"] for item in predictions)),
        "per_label": per_label,
        "confusion": confusion,
        "predictions": predictions,
    }


def cue_predictions(rows: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    predictions = []
    for row in rows:
        score = baseline_score(row)
        predictions.append(
            {
                "baseline": "transparent_context_cue_v0",
                "claim_id": row["claim_id"],
                "split": row["split"],
                "gold_label": row["substantiation_label"],
                "pred_label": predict(score, threshold),
                "support_score": round(score, 4),
                "claim_text": row["claim_text"],
                "evidence_count": row["evidence_count"],
            }
        )
    return predictions


def cue_metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    result = prediction_metrics(rows, cue_predictions(rows, threshold))
    result["threshold"] = round(threshold, 4)
    return result


def select_threshold(train_rows: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    candidates = [round(i / 100, 2) for i in range(20, 91)]
    scored = [(threshold, cue_metrics(train_rows, threshold)) for threshold in candidates]
    return max(scored, key=lambda item: (item[1]["macro_f1"], item[1]["accuracy"]))


def majority_predictions(rows: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    return [
        {
            "baseline": "majority_train_label",
            "claim_id": row["claim_id"],
            "split": row["split"],
            "gold_label": row["substantiation_label"],
            "pred_label": label,
            "support_score": 1.0 if label == "Supported" else 0.0,
            "claim_text": row["claim_text"],
            "evidence_count": row["evidence_count"],
        }
        for row in rows
    ]


def train_naive_bayes(train_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = ("Supported", "Unsupported")
    priors = Counter(row["substantiation_label"] for row in train_rows)
    token_counts = {label: Counter() for label in labels}
    token_totals = Counter()
    vocabulary = set()
    for row in train_rows:
        label = row["substantiation_label"]
        counts = Counter(tokenize(find_claim_window(row)))
        for token, count in counts.items():
            clipped = min(count, 3)
            token_counts[label][token] += clipped
            token_totals[label] += clipped
            vocabulary.add(token)
    return {
        "labels": labels,
        "priors": priors,
        "token_counts": token_counts,
        "token_totals": token_totals,
        "vocabulary": vocabulary,
        "alpha": 1.0,
        "train_count": len(train_rows),
    }


def naive_bayes_score(row: dict[str, Any], model: dict[str, Any]) -> tuple[str, dict[str, float]]:
    scores = {}
    vocab = model["vocabulary"]
    vocab_size = len(vocab)
    for label in model["labels"]:
        score = math.log((model["priors"][label] + model["alpha"]) / (model["train_count"] + model["alpha"] * 2))
        denominator = model["token_totals"][label] + model["alpha"] * vocab_size
        for token, count in Counter(tokenize(find_claim_window(row))).items():
            if token not in vocab:
                continue
            numerator = model["token_counts"][label][token] + model["alpha"]
            score += min(count, 3) * math.log(numerator / denominator)
        scores[label] = score
    return max(scores, key=scores.get), scores


def naive_bayes_predictions(rows: list[dict[str, Any]], model: dict[str, Any]) -> list[dict[str, Any]]:
    predictions = []
    for row in rows:
        pred, scores = naive_bayes_score(row, model)
        # Convert log-score gap to a bounded diagnostic score, not a calibrated probability.
        gap = scores["Supported"] - scores["Unsupported"]
        support_score = 1 / (1 + math.exp(-max(-20, min(20, gap))))
        predictions.append(
            {
                "baseline": "multinomial_naive_bayes_v0",
                "claim_id": row["claim_id"],
                "split": row["split"],
                "gold_label": row["substantiation_label"],
                "pred_label": pred,
                "support_score": round(support_score, 4),
                "claim_text": row["claim_text"],
                "evidence_count": row["evidence_count"],
            }
        )
    return predictions


def compact_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    copied = dict(payload)
    copied.pop("predictions", None)
    return copied


def main() -> None:
    ensure_dirs()
    train_path = DATA_DIR / "substanreview_train_claims.jsonl"
    test_path = DATA_DIR / "substanreview_test_claims.jsonl"
    if not train_path.exists() or not test_path.exists():
        raise SystemExit("SubstanReview claim files missing; run prepare_substanreview.py first")

    train_rows = read_jsonl(train_path)
    test_rows = read_jsonl(test_path)

    threshold, train_metrics = select_threshold(train_rows)
    cue_test = cue_metrics(test_rows, threshold)

    majority_label = Counter(row["substantiation_label"] for row in train_rows).most_common(1)[0][0]
    majority_test = prediction_metrics(test_rows, majority_predictions(test_rows, majority_label))

    nb_model = train_naive_bayes(train_rows)
    nb_train = prediction_metrics(train_rows, naive_bayes_predictions(train_rows, nb_model))
    nb_test = prediction_metrics(test_rows, naive_bayes_predictions(test_rows, nb_model))

    all_predictions = []
    all_predictions.extend(cue_test["predictions"])
    all_predictions.extend(majority_test["predictions"])
    all_predictions.extend(nb_test["predictions"])
    write_jsonl(DATA_DIR / "substanreview_baseline_predictions.jsonl", all_predictions)

    payload = {
        "dataset": "SubstanReview",
        "task": "claim-level substantiation detection",
        "gold_definition": "Supported iff an Eval span has a paired Jus span with the same polarity and index.",
        "baselines": {
            "majority_train_label": {
                "description": f"Always predict the train-majority label: {majority_label}",
                "test": compact_metrics(majority_test),
            },
            "transparent_context_cue_v0": {
                "description": "Handwritten lexical/context cues around the Eval span.",
                "threshold_selection": "maximize train Macro-F1 over thresholds 0.20..0.90",
                "train": compact_metrics(train_metrics),
                "test": compact_metrics(cue_test),
            },
            "multinomial_naive_bayes_v0": {
                "description": "Standard-library supervised bag-of-words verifier over claim-local context.",
                "train": compact_metrics(nb_train),
                "test": compact_metrics(nb_test),
            },
        },
        "best_test_macro_f1": "multinomial_naive_bayes_v0",
    }
    write_json(DATA_DIR / "substanreview_baseline_metrics.json", payload)
    print(
        "test "
        f"count={nb_test['count']} "
        f"majority_macro_f1={majority_test['macro_f1']} "
        f"cue_macro_f1={cue_test['macro_f1']} "
        f"nb_macro_f1={nb_test['macro_f1']} "
        f"nb_accuracy={nb_test['accuracy']}"
    )


if __name__ == "__main__":
    main()
