from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_openrouter_verifier_metrics.json").read_text(encoding="utf-8"))
    lines = [
        "# CLAIMCHECK OpenRouter Embedding Verifier",
        "",
        "This report evaluates whether max embedding similarity can classify CLAIMCHECK weaknesses as Grounded or Ungrounded.",
        "",
        "## Setup",
        "",
        f"- Status: `{metrics['status']}`",
    ]
    if metrics["status"] != "ok":
        lines.extend([f"- Blocked reason: {metrics['reason']}"])
    else:
        pilot_main = metrics["pilot_selected"]["main"]
        oracle = metrics["oracle_main_threshold_diagnostic"]
        lines.extend(
            [
                f"- Embedding model: `{metrics['embedding_model']}`",
                f"- Warning: {metrics['warning']}",
                "",
                "## Main Split Results",
                "",
                "| Setting | Threshold | Accuracy | Macro-F1 | Grounded F1 | Ungrounded F1 |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
                f"| Pilot-selected threshold | {pilot_main['threshold']} | {pilot_main['accuracy']} | {pilot_main['macro_f1']} | {pilot_main['per_label']['Grounded']['f1']} | {pilot_main['per_label']['Ungrounded']['f1']} |",
                f"| Oracle main threshold diagnostic | {metrics['oracle_main_threshold']} | {oracle['accuracy']} | {oracle['macro_f1']} | {oracle['per_label']['Grounded']['f1']} | {oracle['per_label']['Ungrounded']['f1']} |",
                "",
                "## Interpretation",
                "",
                "- Embedding similarity is useful for retrieval, but threshold-only classification is not a reliable verifier.",
                "- The pilot-selected threshold collapses because the pilot set has only one Ungrounded item.",
                "- Even the oracle main threshold remains modest, so the next verifier should use richer features or an LLM judgment prompt.",
            ]
        )
    out_path = REPORT_DIR / "claimcheck_openrouter_verifier_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
