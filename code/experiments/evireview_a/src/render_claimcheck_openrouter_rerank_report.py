from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_openrouter_rerank_metrics.json").read_text(encoding="utf-8"))

    lines = [
        "# CLAIMCHECK OpenRouter LLM Reranking",
        "",
        "This report evaluates whether a free OpenRouter chat model improves paper-claim ranking after embedding retrieval.",
        "",
        "## Setup",
        "",
        f"- Status: `{metrics['status']}`",
        f"- Model: `{metrics['model']}`",
        "- Endpoint: `https://openrouter.ai/api/v1/chat/completions`",
    ]
    if metrics["status"] != "ok":
        lines.extend(
            [
                f"- Blocked reason: {metrics['reason']}",
                f"- Required env: `{', '.join(metrics['required_env'])}`",
                "",
                "## Interpretation",
                "",
                "- The script is ready, but the required OpenRouter runtime condition is not satisfied.",
            ]
        )
    else:
        main = metrics["splits"]["main"]
        lines.extend(
            [
                f"- Base retriever: {metrics['base_retriever']}",
                f"- License note: {metrics['warning']}",
                "",
                "## Main Split Results",
                "",
                "| Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Fallbacks | Mapped / Grounded |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {main['hit_at_1']} | {main['hit_at_3']} | {main['hit_at_5']} | {main['hit_at_10']} | {main['mrr']} | {main['fallback_count']} | {main['mapped_target_count']} / {main['grounded_weakness_count']} |",
                "",
                "## Interpretation",
                "",
                "- Compare against embedding-only: Hit@3 = 0.500 and MRR = 0.4067.",
                "- If reranking improves MRR or Hit@1, it is useful even when Hit@3 stays similar.",
                "- If reranking degrades metrics, use OpenRouter chat models for verifier rationales rather than listwise reranking.",
            ]
        )

    out_path = REPORT_DIR / "claimcheck_openrouter_rerank_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
