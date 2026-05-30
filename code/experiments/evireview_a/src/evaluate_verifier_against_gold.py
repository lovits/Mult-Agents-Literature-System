from __future__ import annotations

from collections import Counter, defaultdict

from common import DATA_DIR, GOLD_LABELS, ensure_dirs, read_jsonl, write_json


GOLD_FILE = "weakness_evidence_gold.jsonl"
PRED_FILE = "verifier_rule_based_predictions.jsonl"


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def main() -> None:
    ensure_dirs()
    gold_path = DATA_DIR / GOLD_FILE
    pred_path = DATA_DIR / PRED_FILE
    if not pred_path.exists():
        raise SystemExit(f"{PRED_FILE} missing; run verify_evidence_baseline.py first")
    if not gold_path.exists():
        payload = {
            "status": "blocked",
            "reason": f"{GOLD_FILE} missing; fill annotation_sheet_section_hybrid.csv and run import_gold_labels.py first.",
        }
        write_json(DATA_DIR / "verification_metrics_rule_based.json", payload)
        print(payload["reason"])
        return

    gold_rows = read_jsonl(gold_path)
    pred_rows = {row["annotation_id"]: row for row in read_jsonl(pred_path)}
    if not gold_rows:
        payload = {
            "status": "blocked",
            "reason": "No gold rows found. Fill gold_label and annotator_rationale in annotation_sheet_section_hybrid.csv first.",
        }
        write_json(DATA_DIR / "verification_metrics_rule_based.json", payload)
        print(payload["reason"])
        return

    labels = sorted(GOLD_LABELS)
    confusion = {gold: {pred: 0 for pred in labels} for gold in labels}
    missing_predictions = []
    correct = 0
    total = 0
    for gold in gold_rows:
        pred = pred_rows.get(gold["annotation_id"])
        if pred is None:
            missing_predictions.append(gold["annotation_id"])
            continue
        gold_label = gold["gold_label"]
        pred_label = pred["pred_label"]
        if pred_label not in GOLD_LABELS:
            pred_label = "Unsupported"
        confusion[gold_label][pred_label] += 1
        correct += int(gold_label == pred_label)
        total += 1

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

    payload = {
        "status": "ok",
        "gold_count": len(gold_rows),
        "evaluated_count": total,
        "accuracy": round(safe_div(correct, total), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4) if f1_values else 0,
        "label_counts_gold": dict(Counter(row["gold_label"] for row in gold_rows)),
        "per_label": per_label,
        "confusion": confusion,
        "missing_predictions": missing_predictions,
        "verifier": "rule_based_section_lexical_v0",
    }
    write_json(DATA_DIR / "verification_metrics_rule_based.json", payload)
    print(f"Wrote {DATA_DIR / 'verification_metrics_rule_based.json'}")
    print(f"gold={len(gold_rows)} evaluated={total} accuracy={payload['accuracy']} macro_f1={payload['macro_f1']}")


if __name__ == "__main__":
    main()

