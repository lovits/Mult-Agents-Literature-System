from __future__ import annotations

import json
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, section_alignment, tokenize, write_json, write_jsonl


SOURCE_FILE = "annotation_candidates_section_hybrid.jsonl"
VAGUE_TERMS = {
    "unclear",
    "insufficient",
    "limited",
    "weak",
    "lack",
    "missing",
    "not enough",
    "not clear",
    "confusing",
}


def query_coverage(weakness_text: str, evidence_texts: list[str]) -> float:
    query_terms = {term for term in tokenize(weakness_text) if len(term) >= 4}
    if not query_terms:
        return 0.0
    evidence_terms = set()
    for text in evidence_texts:
        evidence_terms.update(tokenize(text))
    return len(query_terms & evidence_terms) / len(query_terms)


def generic_score(text: str) -> float:
    lower = text.lower()
    score = 0.0
    if len(tokenize(text)) < 8:
        score += 0.4
    if any(term in lower for term in VAGUE_TERMS):
        score += 0.25
    if not any(term in lower for term in ["experiment", "baseline", "method", "dataset", "result", "citation", "related", "model"]):
        score += 0.2
    return min(score, 1.0)


def silver_label(candidate: dict[str, Any]) -> tuple[str, float, str]:
    retrieved = candidate.get("retrieved_evidence_top5", [])
    evidence_texts = [item.get("text", "") for item in retrieved[:3]]
    coverage = query_coverage(candidate["weakness_text"], evidence_texts)
    top1 = retrieved[0] if retrieved else {}
    top1_aligned = section_alignment(candidate["category_rule"], top1.get("section_type", ""))
    top3_aligned = any(section_alignment(candidate["category_rule"], item.get("section_type", "")) for item in retrieved[:3])
    vague = generic_score(candidate["weakness_text"])

    if vague >= 0.6 and coverage < 0.35:
        return "Generic / Vague", round(0.25 + coverage * 0.25, 4), "Silver rule: weak query specificity and low evidence term coverage."
    if coverage >= 0.52 and top1_aligned:
        return "Supported", round(0.75 + min(coverage, 1.0) * 0.2, 4), "Silver rule: high term coverage and aligned top-1 evidence section."
    if coverage >= 0.35 and top3_aligned:
        return "Partially Supported", round(0.45 + coverage * 0.3, 4), "Silver rule: moderate term coverage and at least one aligned top-3 evidence section."
    if coverage < 0.18:
        return "Unsupported", round(coverage, 4), "Silver rule: very low overlap between weakness and retrieved evidence."
    return "Mentioned but Not Problem", round(0.25 + coverage * 0.25, 4), "Silver rule: related lexical evidence without enough support signal."


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run build_annotation_candidates.py first")

    rows = []
    for candidate in read_jsonl(source_path):
        label, score, rationale = silver_label(candidate)
        retrieved = candidate.get("retrieved_evidence_top5", [])
        rows.append(
            {
                "annotation_id": candidate["annotation_id"],
                "paper_id": candidate["paper_id"],
                "weakness_id": candidate["weakness_id"],
                "weakness_text": candidate["weakness_text"],
                "category_rule": candidate["category_rule"],
                "decision": candidate["decision"],
                "silver_label": label,
                "silver_support_score": score,
                "silver_evidence_block_ids": [item["block_id"] for item in retrieved[:3]],
                "silver_rationale": rationale,
                "warning": "Silver labels are for pipeline debugging only and must not be reported as human gold labels.",
            }
        )

    write_jsonl(DATA_DIR / "weakness_evidence_silver.jsonl", rows)
    summary = {
        "source": SOURCE_FILE,
        "silver_count": len(rows),
        "label_counts": dict(Counter(row["silver_label"] for row in rows)),
        "decision_counts": dict(Counter(row["decision"] for row in rows)),
        "warning": "Silver labels are heuristic labels for debugging evidence-verification flow only.",
    }
    write_json(DATA_DIR / "weakness_evidence_silver_summary.json", summary)
    print(f"Wrote {DATA_DIR / 'weakness_evidence_silver.jsonl'}")
    print(f"Wrote {DATA_DIR / 'weakness_evidence_silver_summary.json'}")
    print(f"rows={len(rows)} labels={summary['label_counts']}")


if __name__ == "__main__":
    main()

