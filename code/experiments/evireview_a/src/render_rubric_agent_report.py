from __future__ import annotations

import json

from common import DATA_DIR, REPORT_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    generation = json.loads((DATA_DIR / "rubric_agent_weaknesses_summary.json").read_text(encoding="utf-8"))
    coverage = json.loads((DATA_DIR / "rubric_agent_coverage_metrics.json").read_text(encoding="utf-8"))
    retrieval_path = DATA_DIR / "rubric_agent_retrieval_summary.json"
    retrieval = json.loads(retrieval_path.read_text(encoding="utf-8")) if retrieval_path.exists() else None
    lines = [
        "# Rubric-agent Weakness Generation Baseline",
        "",
        "This report evaluates a deterministic rubric-guided reviewer baseline before running expensive or rate-limited LLM review generation.",
        "",
        "## Generation Setup",
        "",
        f"- Generator: `{generation['generator']}`",
        f"- Papers: {generation['paper_count']}",
        f"- Generated weaknesses: {generation['generated_weakness_count']}",
        f"- Mean generated per paper: {generation['mean_generated_per_paper']}",
        f"- Category counts: {generation['category_counts']}",
        f"- Severity counts: {generation['severity_counts']}",
        f"- Warning: {generation['warning']}",
        "",
        "## Coverage Proxy",
        "",
        f"- Human weaknesses: {coverage['human_weakness_count']}",
        f"- Generic rate: {coverage['generic_rate']}",
        f"- Redundancy rate: {coverage['redundancy_rate']}",
        f"- Coverage warning: {coverage['warning']}",
        "",
        "| Similarity threshold | Human weakness recall | Mean paper recall | Covered / Total |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for result in coverage["coverage_by_threshold"]:
        lines.append(
            f"| {result['threshold']} | {result['human_weakness_recall']} | "
            f"{result['mean_paper_recall']} | {result['covered_human_weakness_count']} / {result['human_weakness_count']} |"
        )
    lines.extend(
        [
            "",
            "## Top Lexical Matches",
            "",
            "| Paper | Human weakness | Generated weakness | Similarity | Human category | Generated category |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for item in coverage["top_match_examples"]:
        lines.append(
            f"| {item['paper_id']} | {item['human_weakness_id']} | {item['generated_weakness_id']} | "
            f"{item['similarity']} | {item['human_category']} | {item['generated_category']} |"
        )
    if retrieval:
        lines.extend(
            [
                "",
                "## Retrieval Handoff",
                "",
                f"- Retriever: `{retrieval['retriever']}`",
                f"- Generated weaknesses with retrieval: {retrieval['non_empty_retrieval_count']} / {retrieval['generated_weakness_count']}",
                f"- Top-1 section-prior hit rate: {retrieval['top1_section_prior_hit_rate']}",
                f"- Warning: {retrieval['warning']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This baseline validates the generation interface and creates structured candidate weaknesses for downstream retrieval, verifier, ranker, and classification experiments.",
            "- The overlap-based recall is expected to be conservative because generated rubric critiques are templated while human reviewer weaknesses are more specific.",
            "- The next generation experiment should replace or augment this deterministic baseline with an OpenRouter free-model structured reviewer on a small paper subset.",
        ]
    )

    out_path = REPORT_DIR / "rubric_agent_generation_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
