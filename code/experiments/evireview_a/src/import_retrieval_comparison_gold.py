from __future__ import annotations

import csv
from collections import Counter

from common import DATA_DIR, GOLD_LABELS, ensure_dirs, write_json, write_jsonl
from import_gold_labels import split_ids


SOURCE_FILE = "retrieval_comparison_annotation_queue.csv"
OUT_FILE = "retrieval_comparison_gold.jsonl"
SUMMARY_FILE = "retrieval_comparison_gold_summary.json"
BEST_RETRIEVER_LABELS = {"section", "hierarchical", "tie", "neither"}


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run build_retrieval_comparison_annotation_queue.py first")

    rows = []
    invalid = []
    total = 0
    with source_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            best_retriever = (row.get("gold_best_retriever") or "").strip().lower()
            gold_label = (row.get("gold_label") or "").strip()
            rationale = (row.get("annotator_rationale") or "").strip()
            if not best_retriever and not gold_label and not rationale:
                continue
            if best_retriever not in BEST_RETRIEVER_LABELS:
                invalid.append({"annotation_id": row["annotation_id"], "issue": f"invalid_best_retriever:{best_retriever}"})
                continue
            if gold_label not in GOLD_LABELS:
                invalid.append({"annotation_id": row["annotation_id"], "issue": f"invalid_label:{gold_label}"})
                continue
            if not rationale:
                invalid.append({"annotation_id": row["annotation_id"], "issue": "missing_rationale"})
                continue

            evidence_ids = split_ids(row.get("gold_evidence_block_ids", ""))
            rows.append(
                {
                    "annotation_id": row["annotation_id"],
                    "weakness_id": row["weakness_id"],
                    "paper_id": row["paper_id"],
                    "forum": row["forum"],
                    "decision": row["decision"],
                    "weakness_text": row["weakness_text"],
                    "category_rule": row["category_rule"],
                    "gold_best_retriever": best_retriever,
                    "gold_label": gold_label,
                    "gold_evidence_block_ids": evidence_ids,
                    "annotator_rationale": rationale,
                    "annotator_confidence": (row.get("annotator_confidence") or "").strip(),
                }
            )

    summary = {
        "source": SOURCE_FILE,
        "total_rows": total,
        "gold_rows": len(rows),
        "best_retriever_counts": dict(Counter(row["gold_best_retriever"] for row in rows)),
        "label_counts": dict(Counter(row["gold_label"] for row in rows)),
        "decision_counts": dict(Counter(row["decision"] for row in rows)),
        "category_counts": dict(Counter(row["category_rule"] for row in rows)),
        "invalid_rows": invalid,
        "status": "ready" if rows and not invalid else "needs_labels" if not invalid else "has_invalid_rows",
        "valid_best_retriever_labels": sorted(BEST_RETRIEVER_LABELS),
    }
    write_jsonl(DATA_DIR / OUT_FILE, rows)
    write_json(DATA_DIR / SUMMARY_FILE, summary)
    print(f"Wrote {DATA_DIR / OUT_FILE}")
    print(f"Wrote {DATA_DIR / SUMMARY_FILE}")
    print(f"gold_rows={len(rows)} status={summary['status']} invalid={len(invalid)}")


if __name__ == "__main__":
    main()
