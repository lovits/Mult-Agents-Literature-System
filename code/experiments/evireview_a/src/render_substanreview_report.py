from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def fmt_counts(payload: dict[str, int]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in sorted(payload.items()))


def main() -> None:
    ensure_dirs()
    summary = json.loads((DATA_DIR / "substanreview_summary.json").read_text(encoding="utf-8"))
    metrics = json.loads((DATA_DIR / "substanreview_baseline_metrics.json").read_text(encoding="utf-8"))
    baselines = metrics["baselines"]
    best_name = metrics["best_test_macro_f1"]
    best = baselines[best_name]["test"]

    lines = [
        "# SubstanReview Human-Annotated Verifier Benchmark",
        "",
        "This experiment uses an existing human-annotated peer-review dataset before relying on local silver labels or new manual annotation.",
        "",
        "## Dataset",
        "",
        "- Source repository: https://github.com/YanzhuGuo/SubstanReview",
        "- Paper: https://aclanthology.org/2023.findings-emnlp.684/",
        "- Upstream license: Apache-2.0, saved at `data/substanreview_raw/LICENSE`.",
        f"- Gold definition: {summary['gold_definition']}",
        f"- Train: {summary['splits']['train']['review_count']} reviews, {summary['splits']['train']['claim_count']} Eval spans.",
        f"- Test: {summary['splits']['test']['review_count']} reviews, {summary['splits']['test']['claim_count']} Eval spans.",
        f"- Overall label counts: `{fmt_counts(summary['all']['substantiation_label_counts'])}`",
        "",
        "## Baselines",
        "",
        "| Baseline | Test Accuracy | Test Macro-F1 | Prediction Counts |",
        "| --- | ---: | ---: | --- |",
    ]
    for name, payload in baselines.items():
        test = payload["test"]
        lines.append(
            f"| `{name}` | {test['accuracy']} | {test['macro_f1']} | `{fmt_counts(test['prediction_counts'])}` |"
        )
    lines.extend(
        [
            "",
            f"- Best test Macro-F1: `{best_name}`.",
            f"- Best test gold labels: `{fmt_counts(best['label_counts'])}`",
            "- `transparent_context_cue_v0` selects its threshold on train Macro-F1.",
            "- `multinomial_naive_bayes_v0` is a no-new-dependency supervised bag-of-words verifier over claim-local review context.",
            "",
            "## Best Per-label Test F1",
            "",
            "| Label | Precision | Recall | F1 | Support |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for label, item in sorted(best["per_label"].items()):
        lines.append(f"| {label} | {item['precision']} | {item['recall']} | {item['f1']} | {item['support']} |")
    lines.extend(
        [
            "",
            "## Confusion Matrix",
            "",
            f"- Best baseline confusion: `{best['confusion']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is the first valid gold-label verifier check in the project because the labels come from human annotated Eval/Jus span pairs.",
            "- The task is review-internal substantiation detection, not paper-text grounding. It validates the verifier layer's ability to distinguish claims with explicit support from unsupported review assertions.",
            "- The local OpenReview ICLR 2024 sample remains useful for the end-to-end EviReview-Lite pipeline and paper-evidence retrieval, but it should not be presented as human-gold verifier evaluation until annotated.",
            "- CLAIMCHECK is a closer benchmark for paper-claim grounding and should be added next if its released data is directly accessible.",
        ]
    )
    out_path = REPORT_DIR / "substanreview_experiment_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
