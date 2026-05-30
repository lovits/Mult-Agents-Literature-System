from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, write_json


EMBEDDING_CACHE_PATH = DATA_DIR / "claimcheck_openrouter_embedding_cache.json"
LABELS = ("Grounded", "Ungrounded")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def vector_cosine(left: list[float], right: list[float]) -> float:
    dot = sum(lv * rv for lv, rv in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def max_claim_similarity(row: dict[str, Any], embeddings: dict[str, list[float]]) -> float:
    if not row["candidate_claims"]:
        return 0.0
    weakness = embeddings[row["weakness_text"]]
    return max(vector_cosine(weakness, embeddings[claim]) for claim in row["candidate_claims"])


def classification_metrics(rows: list[dict[str, Any]], scored: list[tuple[float, str]], threshold: float) -> dict[str, Any]:
    confusion = {gold: {pred: 0 for pred in LABELS} for gold in LABELS}
    correct = 0
    for _, gold in scored:
        pred = "Grounded" if _ >= threshold else "Ungrounded"
        confusion[gold][pred] += 1
        correct += int(gold == pred)

    per_label = {}
    f1_values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
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
        "label_counts": dict(Counter(row["grounding_label"] for row in rows)),
        "per_label": per_label,
        "confusion": confusion,
    }


def best_threshold(rows: list[dict[str, Any]], scored: list[tuple[float, str]]) -> tuple[float, dict[str, Any]]:
    candidates = sorted({0.0, 1.0, *(score for score, _ in scored)})
    evaluated = [(threshold, classification_metrics(rows, scored, threshold)) for threshold in candidates]
    return max(evaluated, key=lambda item: (item[1]["macro_f1"], item[1]["accuracy"]))


def split_score(rows: list[dict[str, Any]], embeddings: dict[str, list[float]]) -> list[tuple[float, str]]:
    return [(max_claim_similarity(row, embeddings), row["grounding_label"]) for row in rows]


def main() -> None:
    ensure_dirs()
    if not EMBEDDING_CACHE_PATH.exists():
        payload = {
            "status": "blocked",
            "reason": "OpenRouter embedding cache missing; run evaluate_claimcheck_openrouter_embeddings.py first.",
        }
        write_json(DATA_DIR / "claimcheck_openrouter_verifier_metrics.json", payload)
        print(payload["reason"])
        return

    embeddings = json.loads(EMBEDDING_CACHE_PATH.read_text(encoding="utf-8"))
    splits = {
        "pilot": read_jsonl(DATA_DIR / "claimcheck_pilot_weaknesses.jsonl"),
        "main": read_jsonl(DATA_DIR / "claimcheck_main_weaknesses.jsonl"),
    }
    scored = {split: split_score(rows, embeddings) for split, rows in splits.items()}

    pilot_threshold, pilot_metrics = best_threshold(splits["pilot"], scored["pilot"])
    main_with_pilot_threshold = classification_metrics(splits["main"], scored["main"], pilot_threshold)
    oracle_threshold, oracle_main = best_threshold(splits["main"], scored["main"])

    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "Grounded/Ungrounded verifier from max OpenRouter embedding similarity",
        "embedding_model": "nvidia/llama-nemotron-embed-vl-1b-v2:free",
        "warning": "This is a diagnostic verifier baseline; pilot split is tiny and skewed.",
        "pilot_selected": {
            "pilot": pilot_metrics,
            "main": main_with_pilot_threshold,
        },
        "oracle_main_threshold_diagnostic": oracle_main,
        "oracle_main_threshold": round(oracle_threshold, 4),
    }
    write_json(DATA_DIR / "claimcheck_openrouter_verifier_metrics.json", payload)
    print(
        "main "
        f"pilot_threshold_macro_f1={main_with_pilot_threshold['macro_f1']} "
        f"oracle_macro_f1={oracle_main['macro_f1']}"
    )


if __name__ == "__main__":
    main()
