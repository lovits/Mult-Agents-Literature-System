from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json


GOLD_FILE = "retrieval_comparison_gold.jsonl"
SECTION_FILE = "retrieval_section_hybrid_top5.jsonl"
HIERARCHICAL_FILE = "retrieval_human_hierarchical_top5.jsonl"
METRICS_FILE = "retrieval_comparison_gold_metrics.json"
REPORT_FILE = "retrieval_comparison_gold_report.md"


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def block_ids(row: dict[str, Any], k: int) -> set[str]:
    return {item["block_id"] for item in row.get("retrieved", [])[:k]}


def top_score(row: dict[str, Any]) -> float:
    retrieved = row.get("retrieved", [])
    return float(retrieved[0]["score"]) if retrieved else 0.0


def evaluate_hits(gold_rows: list[dict[str, Any]], retrieval_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence_rows = [row for row in gold_rows if row["gold_evidence_block_ids"]]
    hit1 = 0
    hit3 = 0
    hit5 = 0
    missing = []
    for gold in evidence_rows:
        retrieved = retrieval_rows.get(gold["weakness_id"])
        if not retrieved:
            missing.append(gold["weakness_id"])
            continue
        gold_ids = set(gold["gold_evidence_block_ids"])
        hit1 += int(bool(gold_ids & block_ids(retrieved, 1)))
        hit3 += int(bool(gold_ids & block_ids(retrieved, 3)))
        hit5 += int(bool(gold_ids & block_ids(retrieved, 5)))

    denominator = len(evidence_rows)
    return {
        "evidence_labeled_count": denominator,
        "hit_at_1": round(safe_div(hit1, denominator), 4),
        "hit_at_3": round(safe_div(hit3, denominator), 4),
        "hit_at_5": round(safe_div(hit5, denominator), 4),
        "missing_retrieval_count": len(missing),
        "missing_weakness_ids": missing[:20],
    }


def render_report(metrics: dict[str, Any]) -> None:
    if metrics["status"] == "blocked":
        lines = [
            "# Retrieval Comparison Gold Evaluation",
            "",
            f"Blocked: {metrics['reason']}",
            "",
            "Fill `gold_best_retriever`, `gold_label`, `gold_evidence_block_ids`, and `annotator_rationale` in `retrieval_comparison_annotation_queue.csv`, then rerun import and evaluation.",
        ]
    else:
        rows = metrics["retrievers"]
        lines = [
            "# Retrieval Comparison Gold Evaluation",
            "",
            "This report evaluates section-aware retrieval against hierarchical Paper-RAG using manually imported retrieval-comparison gold labels.",
            "",
            "## Winner Labels",
            "",
            f"- Gold rows: {metrics['gold_rows']}",
            f"- Best retriever counts: `{metrics['best_retriever_counts']}`",
            f"- Label counts: `{metrics['label_counts']}`",
            "",
            "## Evidence Hit Rates",
            "",
            "| Retriever | Evidence-labeled rows | Hit@1 | Hit@3 | Hit@5 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for name in ["section_aware_hybrid", "human_hierarchical_paper_rag"]:
            row = rows[name]
            lines.append(
                f"| {name} | {row['evidence_labeled_count']} | {row['hit_at_1']} | {row['hit_at_3']} | {row['hit_at_5']} |"
            )
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "- `gold_best_retriever` captures annotator preference between the two top-k evidence sets.",
                "- Hit@K uses `gold_evidence_block_ids`; it is only meaningful when annotators fill evidence ids.",
                "- Treat this as the formal local retriever comparison once enough rows are labeled.",
            ]
        )
    (REPORT_DIR / REPORT_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    gold_path = DATA_DIR / GOLD_FILE
    if not gold_path.exists():
        metrics = {
            "status": "blocked",
            "reason": f"{GOLD_FILE} missing; run import_retrieval_comparison_gold.py after labeling the comparison queue.",
        }
        write_json(DATA_DIR / METRICS_FILE, metrics)
        render_report(metrics)
        print(metrics["reason"])
        return

    gold_rows = read_jsonl(gold_path)
    if not gold_rows:
        metrics = {
            "status": "blocked",
            "reason": "No retrieval comparison gold rows found. Fill retrieval_comparison_annotation_queue.csv first.",
        }
        write_json(DATA_DIR / METRICS_FILE, metrics)
        render_report(metrics)
        print(metrics["reason"])
        return

    section_rows = {row["weakness_id"]: row for row in read_jsonl(DATA_DIR / SECTION_FILE)}
    hierarchical_rows = {row["weakness_id"]: row for row in read_jsonl(DATA_DIR / HIERARCHICAL_FILE)}
    by_category = defaultdict(list)
    for row in gold_rows:
        by_category[row["category_rule"]].append(row)

    metrics = {
        "status": "ok",
        "gold_rows": len(gold_rows),
        "best_retriever_counts": dict(Counter(row["gold_best_retriever"] for row in gold_rows)),
        "label_counts": dict(Counter(row["gold_label"] for row in gold_rows)),
        "decision_counts": dict(Counter(row["decision"] for row in gold_rows)),
        "category_counts": dict(Counter(row["category_rule"] for row in gold_rows)),
        "retrievers": {
            "section_aware_hybrid": evaluate_hits(gold_rows, section_rows),
            "human_hierarchical_paper_rag": evaluate_hits(gold_rows, hierarchical_rows),
        },
        "mean_top1_score": {
            "section_aware_hybrid": round(safe_div(sum(top_score(section_rows[row["weakness_id"]]) for row in gold_rows), len(gold_rows)), 6),
            "human_hierarchical_paper_rag": round(
                safe_div(sum(top_score(hierarchical_rows[row["weakness_id"]]) for row in gold_rows), len(gold_rows)),
                6,
            ),
        },
        "by_category_best_retriever_counts": {
            category: dict(Counter(row["gold_best_retriever"] for row in rows))
            for category, rows in sorted(by_category.items())
        },
    }
    write_json(DATA_DIR / METRICS_FILE, metrics)
    render_report(metrics)
    print(f"Wrote {DATA_DIR / METRICS_FILE}")
    print(f"gold={len(gold_rows)} best={metrics['best_retriever_counts']}")


if __name__ == "__main__":
    main()
