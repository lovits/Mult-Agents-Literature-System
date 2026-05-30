from __future__ import annotations

from collections import Counter
from typing import Any

from bootstrap_silver_labels import silver_label
from common import DATA_DIR, ensure_dirs, read_jsonl, write_json, write_jsonl


SOURCE_FILE = "annotation_candidates_section_hybrid.jsonl"


def verify(candidate: dict[str, Any]) -> dict[str, Any]:
    label, score, rationale = silver_label(candidate)
    retrieved = candidate.get("retrieved_evidence_top5", [])
    return {
        "annotation_id": candidate["annotation_id"],
        "paper_id": candidate["paper_id"],
        "weakness_id": candidate["weakness_id"],
        "pred_label": label,
        "support_score": score,
        "evidence_block_ids": [item["block_id"] for item in retrieved[:3]],
        "rationale": rationale,
        "verifier": "rule_based_section_lexical_v0",
    }


def main() -> None:
    ensure_dirs()
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        raise SystemExit(f"{SOURCE_FILE} missing; run build_annotation_candidates.py first")

    predictions = [verify(candidate) for candidate in read_jsonl(source_path)]
    write_jsonl(DATA_DIR / "verifier_rule_based_predictions.jsonl", predictions)
    summary = {
        "source": SOURCE_FILE,
        "prediction_count": len(predictions),
        "label_counts": dict(Counter(item["pred_label"] for item in predictions)),
        "verifier": "rule_based_section_lexical_v0",
        "warning": "This baseline is not evaluated against human gold labels yet. Use it for flow debugging and error inspection only.",
    }
    write_json(DATA_DIR / "verifier_rule_based_summary.json", summary)
    print(f"Wrote {DATA_DIR / 'verifier_rule_based_predictions.jsonl'}")
    print(f"Wrote {DATA_DIR / 'verifier_rule_based_summary.json'}")
    print(f"predictions={len(predictions)} labels={summary['label_counts']}")


if __name__ == "__main__":
    main()

