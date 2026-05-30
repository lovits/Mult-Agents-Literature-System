from __future__ import annotations

import csv
from collections import Counter

from common import DATA_DIR, GOLD_LABELS, ensure_dirs, write_json, write_jsonl


SOURCE_FILE = "annotation_sheet_section_hybrid.csv"
OUT_FILE = "weakness_evidence_gold.jsonl"
SUMMARY_FILE = "weakness_evidence_gold_summary.json"


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in (value or "").replace(";", ",").split(",") if item.strip()]


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run export_annotation_sheet.py first")

    rows = []
    invalid = []
    total = 0
    with source_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            label = (row.get("gold_label") or "").strip()
            if not label:
                continue
            if label not in GOLD_LABELS:
                invalid.append({"annotation_id": row["annotation_id"], "issue": f"invalid_label:{label}"})
                continue
            if not (row.get("annotator_rationale") or "").strip():
                invalid.append({"annotation_id": row["annotation_id"], "issue": "missing_rationale"})
                continue
            evidence_ids = split_ids(row.get("gold_evidence_block_ids", ""))
            rows.append(
                {
                    "annotation_id": row["annotation_id"],
                    "paper_id": row["paper_id"],
                    "forum": row["forum"],
                    "decision": row["decision"],
                    "weakness_id": row["weakness_id"],
                    "weakness_text": row["weakness_text"],
                    "category_rule": row["category_rule"],
                    "severity_hint": row["severity_hint"],
                    "gold_label": label,
                    "gold_evidence_block_ids": evidence_ids,
                    "annotator_rationale": row["annotator_rationale"].strip(),
                    "annotator_confidence": (row.get("annotator_confidence") or "").strip(),
                }
            )

    write_jsonl(DATA_DIR / OUT_FILE, rows)
    summary = {
        "source": SOURCE_FILE,
        "total_rows": total,
        "gold_rows": len(rows),
        "label_counts": dict(Counter(row["gold_label"] for row in rows)),
        "decision_counts": dict(Counter(row["decision"] for row in rows)),
        "invalid_rows": invalid,
        "status": "ready" if rows and not invalid else "needs_labels" if not invalid else "has_invalid_rows",
    }
    write_json(DATA_DIR / SUMMARY_FILE, summary)
    print(f"Wrote {DATA_DIR / OUT_FILE}")
    print(f"Wrote {DATA_DIR / SUMMARY_FILE}")
    print(f"gold_rows={len(rows)} status={summary['status']} invalid={len(invalid)}")


if __name__ == "__main__":
    main()

