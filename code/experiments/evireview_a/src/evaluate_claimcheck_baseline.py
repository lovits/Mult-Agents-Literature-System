from __future__ import annotations

import math
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json, write_jsonl


LABELS = ("Grounded", "Ungrounded")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def cosine_set(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / math.sqrt(len(left_tokens) * len(right_tokens))


def target_candidate_indices(row: dict[str, Any], threshold: float = 0.7) -> set[int]:
    indices = set()
    candidates = row["candidate_claims"]
    for target in row["target_claims"]:
        scored = [(cosine_set(target, claim), index) for index, claim in enumerate(candidates)]
        if not scored:
            continue
        score, index = max(scored)
        if score >= threshold:
            indices.add(index)
    return indices


def rank_candidates(row: dict[str, Any]) -> list[int]:
    return sorted(
        range(len(row["candidate_claims"])),
        key=lambda index: cosine_set(row["weakness_text"], row["candidate_claims"][index]),
        reverse=True,
    )


def classification_metrics(rows: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    confusion = {gold: {pred: 0 for pred in LABELS} for gold in LABELS}
    correct = 0
    for row, pred_row in zip(rows, predictions):
        gold = row["grounding_label"]
        pred = pred_row["pred_label"]
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
        "accuracy": round(safe_div(correct, len(rows)), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "label_counts": dict(Counter(row["grounding_label"] for row in rows)),
        "prediction_counts": dict(Counter(row["pred_label"] for row in predictions)),
        "per_label": per_label,
        "confusion": confusion,
    }


def majority_predictions(rows: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    return [
        {
            "baseline": "majority_pilot_label",
            "weakness_id": row["weakness_id"],
            "split": row["split"],
            "gold_label": row["grounding_label"],
            "pred_label": label,
        }
        for row in rows
    ]


def lexical_grounding_score(row: dict[str, Any]) -> float:
    if not row["candidate_claims"]:
        return 0.0
    return max(cosine_set(row["weakness_text"], claim) for claim in row["candidate_claims"])


def lexical_grounding_predictions(rows: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    predictions = []
    for row in rows:
        score = lexical_grounding_score(row)
        predictions.append(
            {
                "baseline": "weakness_claim_lexical_threshold_v0",
                "weakness_id": row["weakness_id"],
                "split": row["split"],
                "gold_label": row["grounding_label"],
                "pred_label": "Grounded" if score >= threshold else "Ungrounded",
                "score": round(score, 4),
            }
        )
    return predictions


def select_threshold(pilot_rows: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    candidates = [round(i / 100, 2) for i in range(0, 81)]
    scored = []
    for threshold in candidates:
        predictions = lexical_grounding_predictions(pilot_rows, threshold)
        metric = classification_metrics(pilot_rows, predictions)
        scored.append((threshold, metric))
    return max(scored, key=lambda item: (item[1]["macro_f1"], item[1]["accuracy"]))


def claim_association_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grounded = [row for row in rows if row["grounding_label"] == "Grounded"]
    mapped = []
    unmapped_count = 0
    for row in grounded:
        indices = target_candidate_indices(row)
        if indices:
            mapped.append((row, indices))
        else:
            unmapped_count += 1

    hit_counts = {1: 0, 3: 0, 5: 0}
    reciprocal_rank_total = 0.0
    for row, target_indices in mapped:
        ranked = rank_candidates(row)
        for k in hit_counts:
            if target_indices & set(ranked[:k]):
                hit_counts[k] += 1
        for rank, index in enumerate(ranked, start=1):
            if index in target_indices:
                reciprocal_rank_total += 1 / rank
                break

    total = len(mapped)
    return {
        "grounded_weakness_count": len(grounded),
        "mapped_target_count": total,
        "unmapped_target_count": unmapped_count,
        "target_mapping_threshold": 0.7,
        "hit_at_1": round(safe_div(hit_counts[1], total), 4),
        "hit_at_3": round(safe_div(hit_counts[3], total), 4),
        "hit_at_5": round(safe_div(hit_counts[5], total), 4),
        "mrr": round(safe_div(reciprocal_rank_total, total), 4),
    }


def main() -> None:
    ensure_dirs()
    pilot_path = DATA_DIR / "claimcheck_pilot_weaknesses.jsonl"
    main_path = DATA_DIR / "claimcheck_main_weaknesses.jsonl"
    if not pilot_path.exists() or not main_path.exists():
        raise SystemExit("CLAIMCHECK weakness files missing; run prepare_claimcheck.py first")

    pilot_rows = read_jsonl(pilot_path)
    main_rows = read_jsonl(main_path)

    majority_label = Counter(row["grounding_label"] for row in pilot_rows).most_common(1)[0][0]
    majority_main = classification_metrics(main_rows, majority_predictions(main_rows, majority_label))

    threshold, pilot_lexical = select_threshold(pilot_rows)
    main_lexical_predictions = lexical_grounding_predictions(main_rows, threshold)
    main_lexical = classification_metrics(main_rows, main_lexical_predictions)
    main_lexical["threshold"] = threshold
    pilot_lexical["threshold"] = threshold

    write_jsonl(DATA_DIR / "claimcheck_baseline_predictions.jsonl", main_lexical_predictions)
    payload = {
        "dataset": "CLAIMCHECK",
        "task": "paper-claim grounded weakness diagnostics",
        "gold_definition": "Grounded iff a weakness has at least one annotator-linked target claim.",
        "baselines": {
            "majority_pilot_label": {
                "description": f"Always predict the pilot-majority label: {majority_label}",
                "main": majority_main,
            },
            "weakness_claim_lexical_threshold_v0": {
                "description": "Predict Grounded if weakness text has enough lexical overlap with any extracted candidate paper claim.",
                "threshold_selection": "maximize pilot Macro-F1 over thresholds 0.00..0.80",
                "pilot": pilot_lexical,
                "main": main_lexical,
            },
        },
        "claim_association_lexical_ranking": {
            "description": "Rank candidate paper claims by lexical overlap with the weakness; evaluate only target claims mappable back to extracted candidate claims.",
            "pilot": claim_association_metrics(pilot_rows),
            "main": claim_association_metrics(main_rows),
        },
    }
    write_json(DATA_DIR / "claimcheck_baseline_metrics.json", payload)
    print(
        "main "
        f"weaknesses={len(main_rows)} "
        f"majority_macro_f1={majority_main['macro_f1']} "
        f"lexical_macro_f1={main_lexical['macro_f1']} "
        f"hit_at_3={payload['claim_association_lexical_ranking']['main']['hit_at_3']}"
    )


if __name__ == "__main__":
    main()
