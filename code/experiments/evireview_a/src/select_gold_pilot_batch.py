from __future__ import annotations

import csv
from collections import Counter, defaultdict

from common import DATA_DIR, ensure_dirs


SOURCE_FILE = "annotation_sheet_section_hybrid.csv"
OUT_FILE = "annotation_pilot_batch_60.csv"
TARGET_SIZE = 60


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run export_annotation_sheet.py first")

    with source_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    by_decision = defaultdict(list)
    for row in rows:
        by_decision[row["decision"]].append(row)

    selected = []
    per_decision_target = TARGET_SIZE // max(1, len(by_decision))
    for decision in sorted(by_decision):
        by_category = defaultdict(list)
        for row in by_decision[decision]:
            by_category[row["category_rule"]].append(row)
        for rows_in_category in by_category.values():
            rows_in_category.sort(key=lambda row: row["annotation_id"])

        decision_selected = []
        categories = sorted(by_category, key=lambda cat: (len(by_category[cat]), cat))
        while len(decision_selected) < per_decision_target and any(by_category.values()):
            for category in categories:
                if by_category[category] and len(decision_selected) < per_decision_target:
                    decision_selected.append(by_category[category].pop(0))

        for row in decision_selected:
            out_row = dict(row)
            out_row["pilot_batch"] = "pilot_60"
            selected.append(out_row)

    if len(selected) < TARGET_SIZE:
        used = {row["annotation_id"] for row in selected}
        remaining = [row for row in rows if row["annotation_id"] not in used]
        selected_category_counts = Counter(row["category_rule"] for row in selected)
        remaining.sort(key=lambda row: (selected_category_counts[row["category_rule"]], row["decision"], row["annotation_id"]))
        for row in remaining[: TARGET_SIZE - len(selected)]:
            row = dict(row)
            row["pilot_batch"] = "pilot_60"
            selected.append(row)

    out_path = DATA_DIR / OUT_FILE
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0].keys()))
        writer.writeheader()
        writer.writerows(selected)

    print(f"Wrote {out_path}")
    print(f"rows={len(selected)} decisions={dict(Counter(row['decision'] for row in selected))}")
    print(f"categories={dict(Counter(row['category_rule'] for row in selected))}")


if __name__ == "__main__":
    main()
