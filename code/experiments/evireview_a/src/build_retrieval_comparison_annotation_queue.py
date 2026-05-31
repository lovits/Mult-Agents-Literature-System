from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, section_alignment, write_csv, write_json, write_jsonl


TARGET_SIZE = 300
SECTION_FILE = "retrieval_section_hybrid_top5.jsonl"
HIERARCHICAL_FILE = "retrieval_human_hierarchical_top5.jsonl"
OUT_JSONL = "retrieval_comparison_annotation_queue.jsonl"
OUT_CSV = "retrieval_comparison_annotation_queue.csv"
OUT_SUMMARY = "retrieval_comparison_annotation_queue_summary.json"


def evidence_prefix(prefix: str, row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for idx in range(1, 4):
        item = row.get("retrieved", [])[idx - 1] if idx <= len(row.get("retrieved", [])) else {}
        out[f"{prefix}_{idx}_block_id"] = item.get("block_id", "")
        out[f"{prefix}_{idx}_section_type"] = item.get("section_type", "")
        out[f"{prefix}_{idx}_score"] = item.get("score", "")
        out[f"{prefix}_{idx}_text"] = item.get("text", "")
    return out


def signature(row: dict[str, Any], k: int = 3) -> tuple[str, ...]:
    return tuple(item["block_id"] for item in row.get("retrieved", [])[:k])


def aligned(row: dict[str, Any], rank: int = 0) -> bool:
    retrieved = row.get("retrieved", [])
    if not retrieved or rank >= len(retrieved):
        return False
    return section_alignment(row["category_rule"], retrieved[rank]["section_type"])


def priority_score(section_row: dict[str, Any], hierarchical_row: dict[str, Any]) -> float:
    score = 0.0
    if signature(section_row, 1) != signature(hierarchical_row, 1):
        score += 4.0
    if signature(section_row, 3) != signature(hierarchical_row, 3):
        score += 2.0
    if aligned(hierarchical_row, 0) and not aligned(section_row, 0):
        score += 2.5
    if aligned(section_row, 0) and not aligned(hierarchical_row, 0):
        score += 1.0
    if section_row["category_rule"] in {"related_work", "experiment", "method", "validity"}:
        score += 0.5
    return score


def build_rows(section_rows: dict[str, dict[str, Any]], hierarchical_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for weakness_id, section_row in section_rows.items():
        hierarchical_row = hierarchical_rows.get(weakness_id)
        if not hierarchical_row:
            continue
        candidates.append(
            {
                "weakness_id": weakness_id,
                "paper_id": section_row["paper_id"],
                "forum": section_row["forum"],
                "decision": section_row.get("decision", hierarchical_row.get("decision", "")),
                "title": hierarchical_row.get("title", ""),
                "weakness_text": section_row["weakness_text"],
                "category_rule": section_row["category_rule"],
                "source_section": section_row["source_section"],
                "section_top1_aligned": aligned(section_row, 0),
                "hierarchical_top1_aligned": aligned(hierarchical_row, 0),
                "top1_same": signature(section_row, 1) == signature(hierarchical_row, 1),
                "top3_same": signature(section_row, 3) == signature(hierarchical_row, 3),
                "priority_score": priority_score(section_row, hierarchical_row),
                **evidence_prefix("section", section_row),
                **evidence_prefix("hierarchical", hierarchical_row),
                "gold_best_retriever": "",
                "gold_label": "",
                "gold_evidence_block_ids": "",
                "annotator_rationale": "",
                "annotator_confidence": "",
            }
        )
    return candidates


def select_queue(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_decision_category = defaultdict(list)
    for row in candidates:
        by_decision_category[(row["decision"], row["category_rule"])].append(row)
    for rows in by_decision_category.values():
        rows.sort(key=lambda row: (-row["priority_score"], row["paper_id"], row["weakness_id"]))

    selected = []
    buckets = sorted(by_decision_category, key=lambda key: (key[0], key[1]))
    while len(selected) < TARGET_SIZE and any(by_decision_category.values()):
        for bucket in buckets:
            if by_decision_category[bucket] and len(selected) < TARGET_SIZE:
                selected.append(by_decision_category[bucket].pop(0))

    selected_ids = {row["weakness_id"] for row in selected}
    if len(selected) < TARGET_SIZE:
        remaining = [row for row in candidates if row["weakness_id"] not in selected_ids]
        remaining.sort(key=lambda row: (-row["priority_score"], row["paper_id"], row["weakness_id"]))
        selected.extend(remaining[: TARGET_SIZE - len(selected)])

    for idx, row in enumerate(selected, start=1):
        ordered = {"annotation_id": f"retrieval_cmp_{idx:04d}"}
        ordered.update(row)
        row.clear()
        row.update(ordered)
    return selected


def render_report(summary: dict[str, Any]) -> None:
    lines = [
        "# Retrieval Comparison Annotation Queue",
        "",
        "This queue prepares human gold labels for comparing section-aware retrieval and hierarchical Paper-RAG.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Candidate pairs | {summary['candidate_pairs']} |",
        f"| Selected rows | {summary['selected_rows']} |",
        f"| Top-1 disagreement rate | {summary['top1_disagreement_rate']} |",
        f"| Top-3 disagreement rate | {summary['top3_disagreement_rate']} |",
        "",
        "## Selected Category Counts",
        "",
        "| Category | Rows |",
        "| --- | ---: |",
    ]
    for category, count in summary["selected_category_counts"].items():
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## Labeling Target",
            "",
            "- Fill `gold_best_retriever` with `section`, `hierarchical`, `tie`, or `neither`.",
            "- Fill `gold_label` using the existing weakness-evidence label schema.",
            "- Fill `gold_evidence_block_ids` with the supporting evidence block ids when any evidence is useful.",
        ]
    )
    (REPORT_DIR / "retrieval_comparison_annotation_queue.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    section_path = DATA_DIR / SECTION_FILE
    hierarchical_path = DATA_DIR / HIERARCHICAL_FILE
    if not section_path.exists():
        raise SystemExit(f"{SECTION_FILE} missing; run retrieve_hybrid_section.py first")
    if not hierarchical_path.exists():
        raise SystemExit(f"{HIERARCHICAL_FILE} missing; run retrieve_human_hierarchical.py first")

    section_rows = {row["weakness_id"]: row for row in read_jsonl(section_path)}
    hierarchical_rows = {row["weakness_id"]: row for row in read_jsonl(hierarchical_path)}
    candidates = build_rows(section_rows, hierarchical_rows)
    selected = select_queue(candidates)

    fieldnames = list(selected[0].keys()) if selected else []
    write_jsonl(DATA_DIR / OUT_JSONL, selected)
    write_csv(DATA_DIR / OUT_CSV, selected, fieldnames)

    summary = {
        "status": "ready",
        "section_retrieval_file": SECTION_FILE,
        "hierarchical_retrieval_file": HIERARCHICAL_FILE,
        "candidate_pairs": len(candidates),
        "selected_rows": len(selected),
        "target_size": TARGET_SIZE,
        "top1_disagreement_rate": round(sum(not row["top1_same"] for row in candidates) / max(1, len(candidates)), 4),
        "top3_disagreement_rate": round(sum(not row["top3_same"] for row in candidates) / max(1, len(candidates)), 4),
        "selected_decision_counts": dict(Counter(row["decision"] for row in selected)),
        "selected_category_counts": dict(Counter(row["category_rule"] for row in selected)),
        "gold_columns": ["gold_best_retriever", "gold_label", "gold_evidence_block_ids", "annotator_rationale", "annotator_confidence"],
        "warning": "This is an annotation queue, not an automatic evaluation result.",
    }
    write_json(DATA_DIR / OUT_SUMMARY, summary)
    render_report(summary)
    print(
        "retrieval_comparison_queue "
        f"pairs={summary['candidate_pairs']} "
        f"selected={summary['selected_rows']} "
        f"top1_disagreement={summary['top1_disagreement_rate']}"
    )


if __name__ == "__main__":
    main()
