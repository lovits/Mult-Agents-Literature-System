from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


METHOD_LABELS = {
    "embedding_max_similarity": "OpenRouter embedding max similarity",
    "bm25_max_similarity": "BM25 max similarity",
    "feature_verifier_probability": "Out-of-fold feature verifier probability",
    "candidate_claim_count": "Candidate claim count",
}


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_evidence_ranker_metrics.json").read_text(encoding="utf-8"))
    lines = [
        "# CLAIMCHECK Evidence-aware Ranker",
        "",
        "This report evaluates whether verifier signals can rank critique weaknesses by paper-groundedness inside each paper-review group.",
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
                f"- Label counts: {metrics['label_counts']}",
                f"- Warning: {metrics['warning']}",
                "",
                "## Ranking Results",
                "",
                "| Method | Groups | MAP | NDCG@3 | NDCG@5 | Top-1 grounded | Bottom-1 ungrounded |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for name, result in metrics["metrics"].items():
            lines.append(
                f"| {METHOD_LABELS.get(name, name)} | {result['evaluated_group_count']} | "
                f"{result['map']} | {result['ndcg_at_3']} | {result['ndcg_at_5']} | "
                f"{result['top1_grounded_rate']} | {result['bottom1_ungrounded_rate']} |"
            )
        best_name, best_result = max(
            metrics["metrics"].items(),
            key=lambda item: (item[1]["map"], item[1]["top1_grounded_rate"]),
        )
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                f"- Best aggregate ranker in this diagnostic: {METHOD_LABELS.get(best_name, best_name)} with MAP {best_result['map']} and Top-1 grounded rate {best_result['top1_grounded_rate']}.",
                "- The out-of-fold feature verifier does not beat BM25 as a ranking signal, so the current ranker should keep retrieval similarity as the primary ordering feature.",
                "- The verifier remains useful as a separate grounded/ungrounded decision module, but its probability should not be treated as a mature evidence-aware ranking score yet.",
            ]
        )

    out_path = REPORT_DIR / "claimcheck_evidence_ranker_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
