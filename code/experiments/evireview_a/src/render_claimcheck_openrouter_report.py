from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_openrouter_embedding_metrics.json").read_text(encoding="utf-8"))

    lines = [
        "# CLAIMCHECK OpenRouter Embedding Retrieval",
        "",
        "This report records the OpenRouter free-model embedding retrieval experiment for CLAIMCHECK.",
        "",
        "## Setup",
        "",
        f"- Status: `{metrics['status']}`",
        f"- Model: `{metrics['model']}`",
        "- Endpoint: `https://openrouter.ai/api/v1/embeddings`",
    ]
    if metrics["status"] != "ok":
        lines.extend(
            [
                f"- Blocked reason: {metrics['reason']}",
                f"- Required env: `{', '.join(metrics['required_env'])}`",
                "",
                "## Interpretation",
                "",
                "- The script is ready, but the local environment does not currently expose an OpenRouter API key.",
                "- Once `OPENROUTER_API_KEY` is set, rerun the suggested command in the metrics JSON to generate real retrieval scores.",
            ]
        )
    else:
        main = metrics["splits"]["main"]
        lines.extend(
            [
                f"- Texts embedded: {metrics['text_count']}",
                f"- License note: {metrics['warning']}",
                "",
                "## Main Split Results",
                "",
                "| Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mapped / Grounded |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {main['hit_at_1']} | {main['hit_at_3']} | {main['hit_at_5']} | {main['hit_at_10']} | {main['mrr']} | {main['mapped_target_count']} / {main['grounded_weakness_count']} |",
                "",
                "## Interpretation",
                "",
                "- This result should be compared against the current lexical floor: char trigram Hit@3 = 0.375.",
                "- If OpenRouter embeddings do not improve over that floor, the next step should be LLM reranking rather than more embedding-only retrieval.",
            ]
        )

    out_path = REPORT_DIR / "claimcheck_openrouter_embedding_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
