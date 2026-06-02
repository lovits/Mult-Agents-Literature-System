from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json, write_jsonl


SOURCE_FILE = "generated_hierarchical_verified_weaknesses.jsonl"
OUT_RANKED = "generated_weakness_ranked_top3.jsonl"
OUT_METRICS = "generated_weakness_ranker_metrics.json"
LABEL_WEIGHTS = {
    "Supported": 1.0,
    "Partially Supported": 0.8,
    "Mentioned but Not Problem": 0.45,
    "Generic / Vague": 0.2,
    "Unsupported": 0.05,
    "Contradicted": 0.0,
}
SEVERITY_WEIGHTS = {
    "major": 1.0,
    "minor": 0.65,
    "unknown": 0.75,
}


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def rank_score(row: dict[str, Any]) -> float:
    support_score = float(row.get("support_score", 0.0))
    label = row.get("verifier_label", "")
    severity = row.get("severity", "unknown")
    label_weight = LABEL_WEIGHTS.get(label, 0.25)
    severity_weight = SEVERITY_WEIGHTS.get(severity, 0.75)
    return round((0.45 + support_score) * label_weight * severity_weight, 6)


def supported_or_better(label: str) -> bool:
    return label in {"Supported", "Partially Supported"}


def summarize(rows: list[dict[str, Any]], ranked_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    top_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_group: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_source[row["source"]].append(row)
        by_group[(row["source"], row["paper_id"])].append(row)
    for row in ranked_rows:
        top_by_source[row["source"]].append(row)

    source_payload = {}
    for source, source_rows in sorted(by_source.items()):
        top_rows = top_by_source[source]
        source_payload[source] = {
            "candidate_count": len(source_rows),
            "paper_count": len({row["paper_id"] for row in source_rows}),
            "top3_count": len(top_rows),
            "candidate_mean_support": round(
                safe_div(sum(float(row.get("support_score", 0.0)) for row in source_rows), len(source_rows)), 4
            ),
            "top3_mean_support": round(
                safe_div(sum(float(row.get("support_score", 0.0)) for row in top_rows), len(top_rows)), 4
            ),
            "candidate_partially_supported_or_better_rate": round(
                safe_div(sum(supported_or_better(row.get("verifier_label", "")) for row in source_rows), len(source_rows)),
                4,
            ),
            "top3_partially_supported_or_better_rate": round(
                safe_div(sum(supported_or_better(row.get("verifier_label", "")) for row in top_rows), len(top_rows)),
                4,
            ),
            "candidate_label_counts": dict(Counter(row.get("verifier_label", "") for row in source_rows)),
            "top3_label_counts": dict(Counter(row.get("verifier_label", "") for row in top_rows)),
            "top3_category_counts": dict(Counter(row.get("category", "") for row in top_rows)),
        }

    return {
        "status": "ok",
        "ranker": "generated_weakness_evidence_aware_ranker_v0",
        "input_file": SOURCE_FILE,
        "candidate_count": len(rows),
        "paper_group_count": len(by_group),
        "top3_count": len(ranked_rows),
        "score_formula": "(0.45 + support_score) * verifier_label_weight * severity_weight",
        "label_weights": LABEL_WEIGHTS,
        "severity_weights": SEVERITY_WEIGHTS,
        "sources": source_payload,
        "warning": "This is a silver-label ranker diagnostic over generated weaknesses, not human gold evaluation.",
    }


def render_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Generated Weakness Evidence-aware Ranker",
        "",
        "This report ranks generated review weaknesses after hierarchical Paper-RAG retrieval and silver verifier diagnostics.",
        "",
        "## Method",
        "",
        f"- Ranker: `{payload['ranker']}`",
        f"- Score formula: `{payload['score_formula']}`",
        "- Inputs: generated weakness severity, silver verifier label, and support score.",
        "- Scope: diagnostic ranking only; labels are not human gold.",
        "",
        "## Results",
        "",
        "| Source | Candidates | Papers | Top-3 rows | Candidate mean support | Top-3 mean support | Candidate partial+ | Top-3 partial+ | Top-3 labels |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for source, row in payload["sources"].items():
        lines.append(
            f"| {source} | {row['candidate_count']} | {row['paper_count']} | {row['top3_count']} | "
            f"{row['candidate_mean_support']} | {row['top3_mean_support']} | "
            f"{row['candidate_partially_supported_or_better_rate']} | "
            f"{row['top3_partially_supported_or_better_rate']} | {row['top3_label_counts']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The ranker converts verifier evidence into an ordered shortlist per paper, which matches the thesis goal of auditable reviewer ranking.",
            "- A useful diagnostic is whether Top-3 rows have higher mean support and higher partially-supported-or-better rate than all candidates.",
            "- Because the verifier labels are silver rules, this should be reported as architecture evidence, not final human evaluation.",
        ]
    )
    (REPORT_DIR / "generated_weakness_ranker_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run retrieve_generated_hierarchical.py first")

    rows = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(source_path):
        enriched = {**row, "rank_score": rank_score(row)}
        rows.append(enriched)
        grouped[(enriched["source"], enriched["paper_id"])].append(enriched)

    ranked_rows = []
    for (source, paper_id), group_rows in sorted(grouped.items()):
        group_rows.sort(key=lambda row: (row["rank_score"], row.get("support_score", 0.0)), reverse=True)
        for rank, row in enumerate(group_rows[:3], start=1):
            ranked_rows.append(
                {
                    "source": source,
                    "paper_id": paper_id,
                    "rank": rank,
                    "generated_weakness_id": row["generated_weakness_id"],
                    "category": row.get("category", ""),
                    "severity": row.get("severity", ""),
                    "verifier_label": row.get("verifier_label", ""),
                    "support_score": row.get("support_score", 0.0),
                    "rank_score": row["rank_score"],
                    "evidence_block_ids": row.get("evidence_block_ids", []),
                    "weakness_text": row.get("weakness_text", ""),
                }
            )

    payload = summarize(rows, ranked_rows)
    write_jsonl(DATA_DIR / OUT_RANKED, ranked_rows)
    write_json(DATA_DIR / OUT_METRICS, payload)
    render_report(payload)
    print(
        "generated_weakness_ranker "
        + " ".join(
            f"{source}_top3_support={row['top3_mean_support']}"
            for source, row in payload["sources"].items()
        )
    )


if __name__ == "__main__":
    main()
