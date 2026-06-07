from __future__ import annotations

from copy import deepcopy
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json
from evaluate_claimcheck_retrieval import bm25_score, evaluate, prepare_row
from evireview_core.domain.models import Weakness
from evireview_core.workflow.components import category_expansion_query


def planned_rows(rows: list[dict[str, Any]], planner: str) -> list[dict[str, Any]]:
    planned = []
    for source in rows:
        row = deepcopy(source)
        if planner == "category_expansion":
            category = next(iter(row.get("weakness_types", [])), "other")
            row["weakness_text"] = category_expansion_query(
                Weakness(row["weakness_id"], row["paper_review_id"], row["weakness_text"], category)
            )
        planned.append(prepare_row(row))
    return planned


def render(payload: dict[str, Any]) -> str:
    lines = [
        "# Query Planner Ablation On CLAIMCHECK",
        "",
        "Ready-label comparison of direct weakness queries and transparent category-expansion queries using the same BM25 retriever.",
        "",
        "| Planner | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for planner, splits in payload["planners"].items():
        metrics = splits["main"]
        lines.append(
            f"| {planner} | {metrics['hit_at_1']:.4f} | {metrics['hit_at_3']:.4f} | "
            f"{metrics['hit_at_5']:.4f} | {metrics['mrr']:.4f} |"
        )
    lines.extend(
        [
            "",
            f"- Main Hit@3 delta: `{payload['main_hit_at_3_delta']:+.4f}`.",
            "- Metric boundary: gold mapped CLAIMCHECK targets; no manual labels added.",
            "- A negative delta is retained as evidence that naive query expansion should not become the default planner.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    splits = {split: read_jsonl(DATA_DIR / f"claimcheck_{split}_weaknesses.jsonl") for split in ("pilot", "main")}
    planners = {
        planner: {split: evaluate(planned_rows(rows, planner), bm25_score) for split, rows in splits.items()}
        for planner in ("direct", "category_expansion")
    }
    direct = planners["direct"]["main"]["hit_at_3"]
    expanded = planners["category_expansion"]["main"]["hit_at_3"]
    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "query planner ablation",
        "metric_boundary": "gold mapped targets",
        "retriever": "bm25",
        "planners": planners,
        "main_hit_at_3_delta": round(expanded - direct, 4),
        "recommended_default": max(planners, key=lambda name: planners[name]["main"]["hit_at_3"]),
    }
    write_json(DATA_DIR / "query_planner_ablation_metrics.json", payload)
    (REPORT_DIR / "query_planner_ablation_report.md").write_text(render(payload), encoding="utf-8")
    print(f"direct={direct:.4f} category_expansion={expanded:.4f} delta={payload['main_hit_at_3_delta']:+.4f}")


if __name__ == "__main__":
    main()
