from __future__ import annotations

import csv
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl


SOURCE_FILE = "annotation_candidates_section_hybrid.jsonl"
OUT_FILE = "annotation_sheet_section_hybrid.csv"
TOP_K = 5


def evidence_columns(candidate: dict[str, Any]) -> dict[str, str]:
    cols: dict[str, str] = {}
    retrieved = candidate.get("retrieved_evidence_top5", [])
    for i in range(1, TOP_K + 1):
        item = retrieved[i - 1] if i <= len(retrieved) else {}
        cols[f"evidence_{i}_block_id"] = item.get("block_id", "")
        cols[f"evidence_{i}_section_type"] = item.get("section_type", "")
        cols[f"evidence_{i}_section_path"] = item.get("section_path", "")
        cols[f"evidence_{i}_score"] = item.get("score", "")
        cols[f"evidence_{i}_text"] = item.get("text", "")
    return cols


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run build_annotation_candidates.py first")

    rows = []
    for candidate in read_jsonl(source_path):
        row = {
            "annotation_id": candidate["annotation_id"],
            "paper_id": candidate["paper_id"],
            "forum": candidate["forum"],
            "decision": candidate["decision"],
            "title": candidate["title"],
            "weakness_id": candidate["weakness_id"],
            "weakness_text": candidate["weakness_text"],
            "category_rule": candidate["category_rule"],
            "severity_hint": candidate["severity_hint"],
            "source_section": candidate["source_section"],
            "retriever": candidate["retriever"],
            **evidence_columns(candidate),
            "gold_label": "",
            "gold_evidence_block_ids": "",
            "annotator_rationale": "",
            "annotator_confidence": "",
        }
        rows.append(row)

    out_path = DATA_DIR / OUT_FILE
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()

