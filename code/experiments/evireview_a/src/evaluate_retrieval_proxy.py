from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, section_alignment, write_json


RETRIEVAL_FILES = {
    "bm25": "retrieval_bm25_top5.jsonl",
    "tfidf_cosine": "retrieval_tfidf_top5.jsonl",
    "hybrid_bm25_tfidf": "retrieval_hybrid_top5.jsonl",
    "section_aware_hybrid": "retrieval_section_hybrid_top5.jsonl",
}


def evaluate_file(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    non_empty = [row for row in rows if row.get("retrieved")]
    top1_aligned = 0
    top3_any_aligned = 0
    section_diversities = []
    top1_sections = Counter()
    avg_top1_scores = []
    avg_top5_scores = []

    for row in rows:
        retrieved = row.get("retrieved", [])
        if not retrieved:
            continue
        top1 = retrieved[0]
        top1_sections[top1["section_type"]] += 1
        if section_alignment(row["category_rule"], top1["section_type"]):
            top1_aligned += 1
        if any(section_alignment(row["category_rule"], item["section_type"]) for item in retrieved[:3]):
            top3_any_aligned += 1
        section_diversities.append(len({item["section_type"] for item in retrieved}))
        avg_top1_scores.append(float(top1["score"]))
        avg_top5_scores.append(mean(float(item["score"]) for item in retrieved))

    denominator = len(rows) or 1
    non_empty_denominator = len(non_empty) or 1
    return {
        "query_count": len(rows),
        "non_empty_count": len(non_empty),
        "non_empty_rate": round(len(non_empty) / denominator, 4),
        "top1_section_alignment_rate": round(top1_aligned / non_empty_denominator, 4),
        "top3_any_section_alignment_rate": round(top3_any_aligned / non_empty_denominator, 4),
        "avg_topk_section_diversity": round(mean(section_diversities), 4) if section_diversities else 0,
        "avg_top1_score": round(mean(avg_top1_scores), 6) if avg_top1_scores else 0,
        "avg_top5_score": round(mean(avg_top5_scores), 6) if avg_top5_scores else 0,
        "top1_section_counts": dict(top1_sections),
    }


def markdown_table(results: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# Retrieval Proxy Evaluation",
        "",
        "These are proxy diagnostics before manual weakness-evidence gold labels are complete. They should not be reported as final retrieval accuracy.",
        "",
        "| Retriever | Non-empty | Top-1 Section Align | Top-3 Any Align | Avg Section Diversity | Avg Top-1 Score |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, result in results.items():
        lines.append(
            f"| {name} | {result['non_empty_rate']:.4f} | {result['top1_section_alignment_rate']:.4f} | "
            f"{result['top3_any_section_alignment_rate']:.4f} | {result['avg_topk_section_diversity']:.4f} | "
            f"{result['avg_top1_score']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `Top-1 Section Align` checks whether the first retrieved block's section type matches a lightweight category-to-section rubric.",
            "- `Top-3 Any Align` is more forgiving and checks whether any of the first three blocks matches the rubric.",
            "- `Avg Section Diversity` helps detect retrieval collapse into one section type.",
            "- Manual gold labels are still required for true Evidence Recall@K and verifier evaluation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    results = {}
    missing = []
    for name, filename in RETRIEVAL_FILES.items():
        path = DATA_DIR / filename
        if not path.exists():
            missing.append(filename)
            continue
        results[name] = evaluate_file(path)

    if missing:
        raise SystemExit(f"Missing retrieval files: {', '.join(missing)}")

    payload = {
        "evaluation_type": "proxy_retrieval_diagnostics",
        "warning": "Proxy diagnostics only; not a replacement for manual weakness-evidence gold labels.",
        "results": results,
    }
    write_json(DATA_DIR / "retrieval_proxy_eval.json", payload)
    report = markdown_table(results)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "retrieval_proxy_eval.md").write_text(report, encoding="utf-8")
    print(f"Wrote {DATA_DIR / 'retrieval_proxy_eval.json'}")
    print(f"Wrote {REPORT_DIR / 'retrieval_proxy_eval.md'}")


if __name__ == "__main__":
    main()

