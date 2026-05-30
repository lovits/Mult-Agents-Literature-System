from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def load_json_if_exists(name: str):
    path = DATA_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ensure_dirs()
    gold = load_json_if_exists("weakness_evidence_gold_summary.json")
    metrics = load_json_if_exists("verification_metrics_rule_based.json")
    lines = [
        "# Gold Annotation Status",
        "",
        "This report tracks whether the weakness-evidence gold labels are ready for verifier evaluation.",
        "",
        "## Annotation Files",
        "",
        "- Full annotation sheet: `annotation_sheet_section_hybrid.csv`",
        "- Pilot batch: `annotation_pilot_batch_60.csv`",
        "- Annotation guideline: `annotation/annotation_guideline.md`",
        "",
    ]

    if gold is None:
        lines.extend(["## Gold Import", "", "Gold labels have not been imported yet."])
    else:
        lines.extend(
            [
                "## Gold Import",
                "",
                f"- Status: `{gold['status']}`",
                f"- Total rows: {gold['total_rows']}",
                f"- Gold rows: {gold['gold_rows']}",
                f"- Label counts: `{gold['label_counts']}`",
                f"- Invalid rows: {len(gold['invalid_rows'])}",
            ]
        )

    lines.extend(["", "## Verifier Evaluation", ""])
    if metrics is None:
        lines.append("Verifier metrics have not been generated yet.")
    elif metrics.get("status") == "blocked":
        lines.append(f"Blocked: {metrics['reason']}")
    else:
        lines.extend(
            [
                f"- Evaluated count: {metrics['evaluated_count']}",
                f"- Accuracy: {metrics['accuracy']}",
                f"- Macro-F1: {metrics['macro_f1']}",
            ]
        )

    out_path = REPORT_DIR / "gold_annotation_status.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

