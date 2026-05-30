from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def metric_row(name: str, metrics: dict) -> str:
    return (
        f"| {name} | {metrics['accuracy']} | {metrics['macro_f1']} | "
        f"{metrics['per_label']['Grounded']['f1']} | {metrics['per_label']['Ungrounded']['f1']} |"
    )


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_feature_verifier_metrics.json").read_text(encoding="utf-8"))
    lines = [
        "# CLAIMCHECK Feature Verifier",
        "",
        "This report evaluates whether a lightweight feature-fusion verifier can classify CLAIMCHECK weaknesses as Grounded or Ungrounded.",
        "",
        "## Setup",
        "",
        f"- Status: `{metrics['status']}`",
    ]
    if metrics["status"] != "ok":
        lines.append(f"- Blocked reason: {metrics['reason']}")
    else:
        lines.extend(
            [
                f"- Dataset: {metrics['dataset']}",
                f"- Validation: {metrics['validation']}",
                f"- Rows: {metrics['row_count']}",
                f"- Paper-review groups: {metrics['group_count']}",
                f"- Features: {metrics['feature_count']}",
                f"- Warning: {metrics['warning']}",
                "- Leakage controls:",
            ]
        )
        for control in metrics["leakage_controls"]:
            lines.append(f"  - {control}")
        lines.extend(
            [
                "",
                "## Cross-Validation Results",
                "",
                "| Method | Accuracy | Macro-F1 | Grounded F1 | Ungrounded F1 |",
                "| --- | ---: | ---: | ---: | ---: |",
                metric_row("Train-fold majority baseline", metrics["baselines"]["train_fold_majority"]),
                metric_row("Train-fold embedding threshold", metrics["baselines"]["train_fold_embedding_threshold"]),
                metric_row("Feature-fusion verifier", metrics["feature_verifier"]),
                "",
                "## Highest-Magnitude Mean Weights",
                "",
                "| Feature | Mean logistic weight |",
                "| --- | ---: |",
            ]
        )
        for item in metrics["mean_feature_weights"]:
            lines.append(f"| `{item['feature']}` | {item['mean_weight']} |")
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "- The feature-fusion verifier improves the Ungrounded class compared with a majority baseline, but it is not yet a deployable final verifier.",
                "- The result supports the architecture decision that RAG retrieval and verifier judgment should be separate modules.",
                "- The next experiment should add an LLM-as-judge prompt on a small, rate-limited subset or train a stronger supervised verifier if a larger licensed split is available.",
            ]
        )

    out_path = REPORT_DIR / "claimcheck_feature_verifier_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
