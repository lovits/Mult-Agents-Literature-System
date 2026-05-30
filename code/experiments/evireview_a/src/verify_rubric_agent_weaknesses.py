from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from bootstrap_silver_labels import silver_label
from common import DATA_DIR, ensure_dirs, read_jsonl, write_json, write_jsonl


VERIFIER = "rubric_agent_rule_based_section_lexical_v0"


def severity_weight(severity: str) -> float:
    return {"major": 1.0, "minor": 0.65}.get(severity, 0.75)


def label_weight(label: str) -> float:
    return {
        "Supported": 1.0,
        "Partially Supported": 0.75,
        "Mentioned but Not Problem": 0.45,
        "Generic / Vague": 0.2,
        "Unsupported": 0.05,
        "Contradicted": 0.0,
    }.get(label, 0.25)


def verify(row: dict[str, Any]) -> dict[str, Any]:
    candidate = {
        "weakness_text": row["weakness_text"],
        "category_rule": row["category"],
        "retrieved_evidence_top5": row["retrieved"],
    }
    label, support_score, rationale = silver_label(candidate)
    generation_confidence = float(row.get("confidence", 0.0))
    rank_score = generation_confidence * severity_weight(row["severity"]) * label_weight(label) * (0.5 + support_score)
    return {
        "generated_weakness_id": row["generated_weakness_id"],
        "paper_id": row["paper_id"],
        "forum": row["forum"],
        "weakness_text": row["weakness_text"],
        "category": row["category"],
        "severity": row["severity"],
        "reviewer_role": row["reviewer_role"],
        "verifier_label": label,
        "support_score": support_score,
        "evidence_block_ids": [item["block_id"] for item in row["retrieved"][:3]],
        "rank_score": round(rank_score, 6),
        "rationale": rationale,
        "verifier": VERIFIER,
        "warning": "Diagnostic verifier output for generated rubric-agent weaknesses; not human gold.",
    }


def main() -> None:
    ensure_dirs()
    retrieval_path = DATA_DIR / "rubric_agent_retrieval_top5.jsonl"
    if not retrieval_path.exists():
        raise SystemExit("rubric_agent_retrieval_top5.jsonl missing; run retrieve_rubric_agent_evidence.py first")

    generated_lookup = {row["generated_weakness_id"]: row for row in read_jsonl(DATA_DIR / "rubric_agent_weaknesses.jsonl")}
    verified = []
    for row in read_jsonl(retrieval_path):
        merged = {**generated_lookup[row["generated_weakness_id"]], **row}
        verified.append(verify(merged))

    ranked_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in verified:
        ranked_by_paper[row["paper_id"]].append(row)
    for rows in ranked_by_paper.values():
        rows.sort(key=lambda item: item["rank_score"], reverse=True)

    top_rows = []
    for paper_id, rows in ranked_by_paper.items():
        for rank, row in enumerate(rows[:3], start=1):
            top_rows.append(
                {
                    "paper_id": paper_id,
                    "rank": rank,
                    "generated_weakness_id": row["generated_weakness_id"],
                    "category": row["category"],
                    "severity": row["severity"],
                    "verifier_label": row["verifier_label"],
                    "support_score": row["support_score"],
                    "rank_score": row["rank_score"],
                    "evidence_block_ids": row["evidence_block_ids"],
                }
            )

    write_jsonl(DATA_DIR / "rubric_agent_verified_weaknesses.jsonl", verified)
    write_jsonl(DATA_DIR / "rubric_agent_ranked_top3.jsonl", top_rows)
    summary = {
        "verifier": VERIFIER,
        "generated_weakness_count": len(verified),
        "paper_count": len(ranked_by_paper),
        "label_counts": dict(Counter(row["verifier_label"] for row in verified)),
        "category_counts": dict(Counter(row["category"] for row in verified)),
        "severity_counts": dict(Counter(row["severity"] for row in verified)),
        "mean_support_score": round(sum(row["support_score"] for row in verified) / len(verified), 4),
        "mean_rank_score": round(sum(row["rank_score"] for row in verified) / len(verified), 4),
        "top3_count": len(top_rows),
        "top3_label_counts": dict(Counter(row["verifier_label"] for row in top_rows)),
        "warning": "Generated weakness verifier/ranker diagnostics use heuristic silver rules and must not be reported as human evaluation.",
    }
    write_json(DATA_DIR / "rubric_agent_verifier_summary.json", summary)
    print(
        "rubric_agent_verifier "
        f"weaknesses={len(verified)} labels={summary['label_counts']} top3={len(top_rows)}"
    )


if __name__ == "__main__":
    main()
