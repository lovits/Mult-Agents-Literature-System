from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, section_alignment, write_json, write_jsonl
from retrieve_generated_hierarchical import merge_candidates, keyword_search, safe_div, section_read, semantic_search


def normalize_human_weakness(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "weakness_id": row["weakness_id"],
        "paper_id": row["paper_id"],
        "forum": row["forum"],
        "paper_index": row["paper_index"],
        "title": row["title"],
        "decision": row["decision"],
        "source": row["source"],
        "review_number": row["review_number"],
        "source_section": row["source_section"],
        "weakness_text": row["weakness_text"],
        "category": row["category_rule"],
        "category_rule": row["category_rule"],
        "severity_hint": row["severity_hint"],
    }


def retrieve_one(weakness: dict[str, Any], blocks: list[dict[str, Any]]) -> dict[str, Any]:
    tool_results = {
        "keyword_search": keyword_search(weakness, blocks),
        "semantic_search": semantic_search(weakness, blocks),
        "section_read": section_read(weakness, blocks),
    }
    merged = merge_candidates(weakness, tool_results)
    retrieved = []
    for rank, item in enumerate(merged, start=1):
        block = item["block"]
        retrieved.append(
            {
                "rank": rank,
                "score": item["score"],
                "rrf_score": item["rrf_score"],
                "lexical_score": item["lexical_score"],
                "char_score": item["char_score"],
                "section_prior": item["section_prior"],
                "block_id": block["block_id"],
                "section_path": block["section_path"],
                "section_type": block["section_type"],
                "tool_scores": item["tool_scores"],
                "tool_ranks": item["tool_ranks"],
                "text": block["text"][:900],
            }
        )
    return {
        **weakness,
        "retriever": "human_hierarchical_paper_rag_v0",
        "top_k": 5,
        "retrieval_trace": {
            "tool_candidate_counts": {name: len(rows) for name, rows in tool_results.items()},
            "tools_used": [name for name, rows in tool_results.items() if rows],
        },
        "retrieved": retrieved,
    }


def top_tool(row: dict[str, Any]) -> str:
    if not row["retrieved"]:
        return "none"
    tool_ranks = row["retrieved"][0].get("tool_ranks", {})
    return min(tool_ranks.items(), key=lambda item: item[1])[0] if tool_ranks else "none"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    non_empty = [row for row in rows if row["retrieved"]]
    top1_aligned = sum(
        1
        for row in non_empty
        if section_alignment(row["category_rule"], row["retrieved"][0]["section_type"])
    )
    top3_aligned = sum(
        1
        for row in non_empty
        if any(section_alignment(row["category_rule"], item["section_type"]) for item in row["retrieved"][:3])
    )
    by_category = defaultdict(list)
    for row in rows:
        by_category[row["category_rule"]].append(row)

    return {
        "status": "ok",
        "retriever": "human_hierarchical_paper_rag_v0",
        "query_count": len(rows),
        "non_empty_count": len(non_empty),
        "non_empty_rate": round(safe_div(len(non_empty), len(rows)), 4),
        "top1_section_alignment_rate": round(safe_div(top1_aligned, len(non_empty)), 4),
        "top3_any_section_alignment_rate": round(safe_div(top3_aligned, len(non_empty)), 4),
        "decision_counts": dict(Counter(row["decision"] for row in rows)),
        "category_counts": dict(Counter(row["category_rule"] for row in rows)),
        "top1_tool_mix": dict(Counter(top_tool(row) for row in non_empty)),
        "by_category": {
            category: {
                "query_count": len(category_rows),
                "top1_section_alignment_rate": round(
                    safe_div(
                        sum(
                            1
                            for row in category_rows
                            if row["retrieved"] and section_alignment(row["category_rule"], row["retrieved"][0]["section_type"])
                        ),
                        sum(1 for row in category_rows if row["retrieved"]),
                    ),
                    4,
                ),
            }
            for category, category_rows in sorted(by_category.items())
        },
        "warning": "Proxy diagnostics only. Use human gold labels for true evidence recall and verifier accuracy.",
    }


def render_report(summary: dict[str, Any]) -> None:
    lines = [
        "# Human Weakness Hierarchical Paper-RAG",
        "",
        "This report applies the hierarchical Paper-RAG retriever to human reviewer weaknesses.",
        "",
        "## Overall",
        "",
        "| Queries | Non-empty | Top-1 section align | Top-3 any align | Top-1 tool mix |",
        "| ---: | ---: | ---: | ---: | --- |",
        f"| {summary['query_count']} | {summary['non_empty_rate']} | "
        f"{summary['top1_section_alignment_rate']} | {summary['top3_any_section_alignment_rate']} | "
        f"{summary['top1_tool_mix']} |",
        "",
        "## Category Diagnostics",
        "",
        "| Category | Queries | Top-1 section align |",
        "| --- | ---: | ---: |",
    ]
    for category, row in summary["by_category"].items():
        lines.append(f"| {category} | {row['query_count']} | {row['top1_section_alignment_rate']} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a proxy retrieval diagnostic over existing human reviewer weaknesses.",
            "- It prepares a direct comparison with section-aware retrieval once gold weakness-evidence labels are available.",
            "- The next required evidence is human annotation of whether retrieved blocks truly support each weakness.",
        ]
    )
    (REPORT_DIR / "human_hierarchical_retrieval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)

    rows = []
    for raw_weakness in read_jsonl(DATA_DIR / "human_weaknesses.jsonl"):
        weakness = normalize_human_weakness(raw_weakness)
        rows.append(retrieve_one(weakness, blocks_by_paper[weakness["paper_id"]]))

    summary = summarize(rows)
    write_jsonl(DATA_DIR / "retrieval_human_hierarchical_top5.jsonl", rows)
    write_json(DATA_DIR / "retrieval_human_hierarchical_summary.json", summary)
    render_report(summary)
    print(
        "human_hierarchical_retrieval "
        f"queries={summary['query_count']} "
        f"top1_align={summary['top1_section_alignment_rate']} "
        f"top3_align={summary['top3_any_section_alignment_rate']}"
    )


if __name__ == "__main__":
    main()
