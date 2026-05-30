from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def fmt_counts(payload: dict[str, int]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in sorted(payload.items()))


def main() -> None:
    ensure_dirs()
    summary = json.loads((DATA_DIR / "claimcheck_summary.json").read_text(encoding="utf-8"))
    metrics = json.loads((DATA_DIR / "claimcheck_baseline_metrics.json").read_text(encoding="utf-8"))
    majority = metrics["baselines"]["majority_pilot_label"]["main"]
    lexical = metrics["baselines"]["weakness_claim_lexical_threshold_v0"]["main"]
    association = metrics["claim_association_lexical_ranking"]["main"]

    lines = [
        "# CLAIMCHECK Paper-grounded Weakness Benchmark",
        "",
        "This experiment checks the stronger benchmark route: reviewer weaknesses grounded to paper claims.",
        "",
        "## Dataset",
        "",
        "- Source repository: https://github.com/JHU-CLSP/CLAIMCHECK",
        "- Paper: https://aclanthology.org/2025.findings-emnlp.1185/",
        "- License note: no upstream LICENSE file was detected; raw and row-level text files are intentionally not committed.",
        f"- Gold definition: {summary['gold_definition']}",
        f"- Pilot: {summary['splits']['pilot']['paper_review_pair_count']} paper-review pairs, {summary['splits']['pilot']['weakness_count']} weaknesses.",
        f"- Main: {summary['splits']['main']['paper_review_pair_count']} paper-review pairs, {summary['splits']['main']['weakness_count']} weaknesses.",
        f"- Main grounding labels: `{fmt_counts(summary['splits']['main']['grounding_label_counts'])}`",
        "",
        "## Grounded / Ungrounded Baselines",
        "",
        "| Baseline | Main Accuracy | Main Macro-F1 | Prediction Counts |",
        "| --- | ---: | ---: | --- |",
        f"| `majority_pilot_label` | {majority['accuracy']} | {majority['macro_f1']} | `{fmt_counts(majority['prediction_counts'])}` |",
        f"| `weakness_claim_lexical_threshold_v0` | {lexical['accuracy']} | {lexical['macro_f1']} | `{fmt_counts(lexical['prediction_counts'])}` |",
        "",
        "## Claim Association Ranking",
        "",
        f"- Grounded weaknesses: {association['grounded_weakness_count']}",
        f"- Mapped targets: {association['mapped_target_count']}",
        f"- Unmapped targets: {association['unmapped_target_count']}",
        f"- Hit@1: {association['hit_at_1']}",
        f"- Hit@3: {association['hit_at_3']}",
        f"- Hit@5: {association['hit_at_5']}",
        f"- MRR: {association['mrr']}",
        "",
        "## Interpretation",
        "",
        "- CLAIMCHECK is closer to the thesis target than SubstanReview because weaknesses are linked to claims from the reviewed paper.",
        "- The simple lexical classifier collapses to the pilot-majority behavior because the pilot split is tiny and highly skewed.",
        "- Lexical ranking still recovers some target claims on the main split, but Hit@3 remains low, showing that paper-claim grounding needs a semantic retriever/verifier rather than keyword overlap.",
        "- This benchmark should be the next target for an LLM or embedding-based verifier, while SubstanReview remains useful for review-internal substantiation.",
    ]
    out_path = REPORT_DIR / "claimcheck_experiment_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
