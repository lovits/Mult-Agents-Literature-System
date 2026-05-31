from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from bootstrap_silver_labels import silver_label
from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, section_alignment, section_prior, tokenize, write_json, write_jsonl
from evaluate_claimcheck_retrieval import char_ngrams, set_cosine


TOP_K = 5
CANDIDATE_K = 8
RRF_K = 60

GENERATED_SOURCES = {
    "rubric_agent": "rubric_agent_weaknesses.jsonl",
    "glm_reviewer": "glm_reviewer_weaknesses.jsonl",
}


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def expected_sections(category: str) -> list[str]:
    order = {
        "related_work": ["related_work", "introduction", "reference"],
        "experiment": ["experiment", "method", "limitation"],
        "method": ["method", "experiment", "appendix"],
        "reproducibility": ["method", "experiment", "appendix"],
        "clarity": ["introduction", "method", "other"],
        "validity": ["experiment", "method", "limitation"],
        "other": ["abstract", "introduction", "method", "experiment", "other"],
    }
    return order.get(category, order["other"])


def keyword_search(weakness: dict[str, Any], blocks: list[dict[str, Any]]) -> list[tuple[float, dict[str, Any]]]:
    query_terms = {term for term in tokenize(weakness["weakness_text"]) if len(term) >= 4}
    scored = []
    for block in blocks:
        block_terms = set(tokenize(block["text"]))
        overlap = safe_div(len(query_terms & block_terms), len(query_terms))
        if overlap:
            scored.append((overlap + 0.08 * section_prior(weakness["category"], block["section_type"]), block))
    return sorted(scored, key=lambda item: item[0], reverse=True)[:CANDIDATE_K]


def semantic_search(weakness: dict[str, Any], blocks: list[dict[str, Any]]) -> list[tuple[float, dict[str, Any]]]:
    scored = []
    for block in blocks:
        lexical = set_cosine(weakness["weakness_text"], block["text"])
        char = set_cosine(weakness["weakness_text"], block["text"], char_ngrams)
        score = 0.52 * lexical + 0.40 * char + 0.08 * section_prior(weakness["category"], block["section_type"])
        if score:
            scored.append((score, block))
    return sorted(scored, key=lambda item: item[0], reverse=True)[:CANDIDATE_K]


def section_read(weakness: dict[str, Any], blocks: list[dict[str, Any]]) -> list[tuple[float, dict[str, Any]]]:
    targets = expected_sections(weakness["category"])
    scored = []
    for block in blocks:
        if block["section_type"] not in targets:
            continue
        lexical = set_cosine(weakness["weakness_text"], block["text"])
        char = set_cosine(weakness["weakness_text"], block["text"], char_ngrams)
        target_rank = targets.index(block["section_type"])
        score = 0.45 + 0.10 * (len(targets) - target_rank) + 0.30 * lexical + 0.20 * char
        scored.append((score, block))
    return sorted(scored, key=lambda item: item[0], reverse=True)[:CANDIDATE_K]


def merge_candidates(
    weakness: dict[str, Any],
    tool_results: dict[str, list[tuple[float, dict[str, Any]]]],
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for tool_name, results in tool_results.items():
        for rank, (tool_score, block) in enumerate(results, start=1):
            block_id = block["block_id"]
            state = merged.setdefault(
                block_id,
                {
                    "block": block,
                    "rrf_score": 0.0,
                    "tool_scores": {},
                    "tool_ranks": {},
                },
            )
            state["rrf_score"] += 1.0 / (RRF_K + rank)
            state["tool_scores"][tool_name] = round(tool_score, 6)
            state["tool_ranks"][tool_name] = rank

    rows = []
    for state in merged.values():
        block = state["block"]
        lexical = set_cosine(weakness["weakness_text"], block["text"])
        char = set_cosine(weakness["weakness_text"], block["text"], char_ngrams)
        prior = section_prior(weakness["category"], block["section_type"])
        final_score = state["rrf_score"] + 0.25 * lexical + 0.20 * char + 0.10 * prior
        rows.append(
            {
                "score": round(final_score, 6),
                "rrf_score": round(state["rrf_score"], 6),
                "lexical_score": round(lexical, 6),
                "char_score": round(char, 6),
                "section_prior": prior,
                "block": block,
                "tool_scores": state["tool_scores"],
                "tool_ranks": state["tool_ranks"],
            }
        )
    return sorted(rows, key=lambda item: item["score"], reverse=True)[:TOP_K]


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
    trace = {
        "target_sections": expected_sections(weakness["category"]),
        "tool_candidate_counts": {name: len(rows) for name, rows in tool_results.items()},
        "tools_used": [name for name, rows in tool_results.items() if rows],
    }
    return {
        **weakness,
        "retriever": "generated_hierarchical_paper_rag_v0",
        "retrieval_trace": trace,
        "retrieved": retrieved,
    }


def normalize_source_row(source: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": source,
        "generated_weakness_id": row["generated_weakness_id"],
        "paper_id": row["paper_id"],
        "forum": row.get("forum", row["paper_id"]),
        "weakness_text": row["weakness_text"],
        "category": row.get("category", "other"),
        "severity": row.get("severity", "unknown"),
        "reviewer_role": row.get("reviewer_role", ""),
        "confidence": row.get("confidence"),
    }


def summarize(retrieved_rows: list[dict[str, Any]], verified_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    verified_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in retrieved_rows:
        by_source[row["source"]].append(row)
    for row in verified_rows:
        verified_by_source[row["source"]].append(row)

    sources = {}
    for source, rows in sorted(by_source.items()):
        verified = verified_by_source[source]
        top1_aligned = sum(
            1
            for row in rows
            if row["retrieved"] and section_alignment(row["category"], row["retrieved"][0]["section_type"])
        )
        top3_aligned = sum(
            1
            for row in rows
            if any(section_alignment(row["category"], item["section_type"]) for item in row["retrieved"][:3])
        )
        support_scores = [row["support_score"] for row in verified]
        label_counts = Counter(row["verifier_label"] for row in verified)
        top1_tools = []
        for row in rows:
            if not row["retrieved"]:
                continue
            tool_ranks = row["retrieved"][0]["tool_ranks"]
            top1_tools.append(min(tool_ranks.items(), key=lambda item: item[1])[0] if tool_ranks else "none")
        sources[source] = {
            "generated_weakness_count": len(rows),
            "non_empty_retrieval_count": sum(1 for row in rows if row["retrieved"]),
            "top1_section_alignment_rate": round(safe_div(top1_aligned, len(rows)), 4),
            "top3_section_alignment_rate": round(safe_div(top3_aligned, len(rows)), 4),
            "mean_support_score": round(safe_div(sum(support_scores), len(support_scores)), 4),
            "partially_supported_or_better_rate": round(
                safe_div(label_counts.get("Partially Supported", 0) + label_counts.get("Supported", 0), len(verified)),
                4,
            ),
            "label_counts": dict(label_counts),
            "top1_tool_mix": dict(Counter(top1_tools)),
        }

    return {
        "status": "ok",
        "retriever": "generated_hierarchical_paper_rag_v0",
        "sources": sources,
        "warning": "Silver verifier labels are diagnostics only; compare trends, not final truth.",
    }


def render_report(summary: dict[str, Any]) -> None:
    lines = [
        "# Hierarchical Paper-RAG Retrieval Experiment",
        "",
        "This report evaluates a transparent hierarchical retrieval interface for generated review weaknesses.",
        "",
        "## Retrieval Tools",
        "",
        "- `keyword_search`: exact term overlap with section prior.",
        "- `semantic_search`: lexical + character n-gram similarity with section prior.",
        "- `section_read`: category-guided reads over expected paper sections.",
        "- `RRF merge`: reciprocal-rank fusion plus lexical, character, and section scores.",
        "",
        "## Results",
        "",
        "| Source | Weaknesses | Top-1 section align | Top-3 section align | Mean support | Partially-supported-or-better | Labels |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for source, row in summary["sources"].items():
        lines.append(
            f"| {source} | {row['generated_weakness_count']} | {row['top1_section_alignment_rate']} | "
            f"{row['top3_section_alignment_rate']} | {row['mean_support_score']} | "
            f"{row['partially_supported_or_better_rate']} | {row['label_counts']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The hierarchical interface makes retrieval decisions auditable as explicit tool traces.",
            "- This is an architecture diagnostic: current labels still come from the silver verifier, not human gold.",
            "- Next step: compare this retriever against section-aware lexical retrieval on human-labeled gold items when the gold set reaches 200-300 items.",
        ]
    )
    (REPORT_DIR / "hierarchical_paper_rag_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)

    generated_rows = []
    for source, filename in GENERATED_SOURCES.items():
        path = DATA_DIR / filename
        if path.exists():
            generated_rows.extend(normalize_source_row(source, row) for row in read_jsonl(path))

    retrieved_rows = []
    verified_rows = []
    for weakness in generated_rows:
        retrieved_row = retrieve_one(weakness, blocks_by_paper.get(weakness["paper_id"], []))
        retrieved_rows.append(retrieved_row)
        label, support_score, rationale = silver_label(
            {
                "weakness_text": retrieved_row["weakness_text"],
                "category_rule": retrieved_row["category"],
                "retrieved_evidence_top5": retrieved_row["retrieved"],
            }
        )
        verified_rows.append(
            {
                **{key: retrieved_row[key] for key in ("source", "generated_weakness_id", "paper_id", "weakness_text", "category", "severity")},
                "verifier_label": label,
                "support_score": support_score,
                "evidence_block_ids": [item["block_id"] for item in retrieved_row["retrieved"][:3]],
                "verifier_rationale": rationale,
                "retriever": retrieved_row["retriever"],
            }
        )

    write_jsonl(DATA_DIR / "generated_hierarchical_retrieval_top5.jsonl", retrieved_rows)
    write_jsonl(DATA_DIR / "generated_hierarchical_verified_weaknesses.jsonl", verified_rows)
    summary = summarize(retrieved_rows, verified_rows)
    write_json(DATA_DIR / "generated_hierarchical_retrieval_summary.json", summary)
    render_report(summary)
    print(
        "generated_hierarchical_retrieval "
        + " ".join(
            f"{source}_support={row['mean_support_score']}"
            for source, row in summary["sources"].items()
        )
    )


if __name__ == "__main__":
    main()
