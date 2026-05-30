from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    metrics = json.loads((DATA_DIR / "claimcheck_retrieval_metrics.json").read_text(encoding="utf-8"))
    methods = metrics["methods"]
    best_name = metrics["best_main_hit_at_3"]

    lines = [
        "# CLAIMCHECK Claim Retrieval Experiment",
        "",
        "This report evaluates dependency-free retrieval baselines for mapping reviewer weaknesses to source-paper claims.",
        "",
        "## Setup",
        "",
        f"- Dataset: {metrics['dataset']}",
        f"- Task: {metrics['task']}",
        f"- Gold definition: {metrics['gold_definition']}",
        f"- License note: {metrics['warning']}",
        "",
        "## Main Split Results",
        "",
        "| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mapped / Grounded |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, split_metrics in methods.items():
        item = split_metrics["main"]
        lines.append(
            f"| `{name}` | {item['hit_at_1']} | {item['hit_at_3']} | {item['hit_at_5']} | "
            f"{item['hit_at_10']} | {item['mrr']} | {item['mapped_target_count']} / {item['grounded_weakness_count']} |"
        )
    best = methods[best_name]["main"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best main Hit@3: `{best_name}` at {best['hit_at_3']}.",
            "- Character trigram overlap improves top-k coverage over plain token overlap, suggesting that surface-form variation and partial phrase matching matter.",
            "- The absolute scores remain low for a paper-grounding task, so the next experiment should introduce embedding retrieval or an LLM reranker.",
            "- These results strengthen the thesis argument that simple lexical matching is an insufficient verifier backend for grounded peer-review critique.",
        ]
    )
    out_path = REPORT_DIR / "claimcheck_retrieval_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
