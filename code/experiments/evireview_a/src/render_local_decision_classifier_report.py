from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


METHOD_LABELS = {
    "majority": "Majority baseline",
    "metadata": "Metadata baseline",
    "human_weakness_upper_bound": "Human weakness upper-bound",
    "silver_evidence_proxy": "Silver evidence proxy",
    "metadata_plus_human_weakness": "Metadata + human weakness",
    "metadata_plus_silver_evidence": "Metadata + silver evidence",
    "fusion_all_proxy": "Fusion proxy",
}


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "local_decision_classifier_metrics.json").read_text(encoding="utf-8"))
    lines = [
        "# Local OpenReview Accept/Reject Classifier",
        "",
        "This report evaluates whether metadata, weakness, and evidence-verification proxy features contain signal for the final OpenReview decision.",
        "",
        "## Setup",
        "",
        f"- Status: `{metrics['status']}`",
        f"- Dataset: {metrics['dataset']}",
        f"- Validation: {metrics['validation']}",
        f"- Papers: {metrics['paper_count']}",
        f"- Decision counts: {metrics['decision_counts']}",
        f"- Silver feature coverage: {metrics['silver_feature_coverage_papers']} papers",
        f"- Warning: {metrics['warning']}",
        "",
        "## Results",
        "",
        "| Method | Features | Accuracy | Macro-F1 | ROC-AUC | Accept F1 | Reject F1 | Fold Macro-F1 mean +/- std |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in metrics["results"]:
        aggregate = result["aggregate"]
        lines.append(
            f"| {METHOD_LABELS.get(result['name'], result['name'])} | {result['feature_count']} | "
            f"{aggregate['accuracy']} | {aggregate['macro_f1']} | {aggregate['roc_auc']} | "
            f"{aggregate['per_label']['Accept']['f1']} | {aggregate['per_label']['Reject']['f1']} | "
            f"{result['fold_macro_f1_mean']} +/- {result['fold_macro_f1_std']} |"
        )

    best = next(result for result in metrics["results"] if result["name"] == metrics["best_method"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best method in this exploratory diagnostic: {METHOD_LABELS.get(best['name'], best['name'])} with Macro-F1 {best['aggregate']['macro_f1']} and ROC-AUC {best['aggregate']['roc_auc']}.",
            "- This is not a final classifier result because human-review weakness features are upper-bound proxies and silver evidence labels are rule-generated.",
            "- The experiment is useful for the thesis because it tests whether evidence-aware features carry decision-related signal before investing in agent-generated weakness classification.",
        ]
    )
    out_path = REPORT_DIR / "local_decision_classifier_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
