from __future__ import annotations

from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, load_json, normalize_ws, write_json, write_jsonl


RAW_DIR = DATA_DIR / "claimcheck_raw"


def weakness_types(payload: dict[str, Any]) -> list[str]:
    labels = payload.get("Weakness Annotation", {}).get("weakness_type", {})
    return sorted(key for key, value in labels.items() if value)


def process_split(split: str, filename: str) -> list[dict[str, Any]]:
    records = load_json(RAW_DIR / filename)
    rows = []
    for pair_id, record in records.items():
        meta = record.get("meta", {})
        candidate_claims = meta.get("claims", [])
        weaknesses = record.get("response", {}).get("Weakness associated with claims", [])
        for index, item in enumerate(weaknesses, start=1):
            target_claims = item.get("Target claims") or []
            rows.append(
                {
                    "dataset": "CLAIMCHECK",
                    "split": split,
                    "paper_review_id": pair_id,
                    "weakness_id": f"{split}_{pair_id}_weakness_{index:03d}",
                    "weakness_text": normalize_ws(item.get("Weakness span", "")),
                    "confidence_score": item.get("Weakness confidence score"),
                    "target_claims": [normalize_ws(claim) for claim in target_claims],
                    "target_claim_count": len(target_claims),
                    "grounding_label": "Grounded" if target_claims else "Ungrounded",
                    "weakness_types": weakness_types(item),
                    "candidate_claims": [normalize_ws(claim) for claim in candidate_claims],
                    "candidate_claim_count": len(candidate_claims),
                }
            )
    return rows


def summarize(rows: list[dict[str, Any]], pair_count: int, split: str) -> dict[str, Any]:
    type_counts = Counter(kind for row in rows for kind in row["weakness_types"])
    return {
        "split": split,
        "paper_review_pair_count": pair_count,
        "weakness_count": len(rows),
        "grounding_label_counts": dict(Counter(row["grounding_label"] for row in rows)),
        "target_claim_count_distribution": dict(Counter(str(row["target_claim_count"]) for row in rows)),
        "weakness_type_counts": dict(type_counts),
        "avg_candidate_claim_count": round(
            sum(row["candidate_claim_count"] for row in rows) / len(rows), 4
        )
        if rows
        else 0,
    }


def main() -> None:
    ensure_dirs()
    split_files = {"pilot": "source_pilot.json", "main": "source_main.json"}
    summaries = {}
    all_rows = []
    for split, filename in split_files.items():
        raw_path = RAW_DIR / filename
        if not raw_path.exists():
            raise SystemExit(f"{raw_path} missing; run fetch_claimcheck_texts.py first")
        pair_count = len(load_json(raw_path))
        rows = process_split(split, filename)
        write_jsonl(DATA_DIR / f"claimcheck_{split}_weaknesses.jsonl", rows)
        summaries[split] = summarize(rows, pair_count, split)
        all_rows.extend(rows)
        print(f"{split}: pairs={pair_count} weaknesses={len(rows)} labels={summaries[split]['grounding_label_counts']}")

    write_jsonl(DATA_DIR / "claimcheck_all_weaknesses.jsonl", all_rows)
    write_json(
        DATA_DIR / "claimcheck_summary.json",
        {
            "dataset": "CLAIMCHECK",
            "task": "Weakness-to-paper-claim association and grounding diagnostics",
            "gold_definition": "A weakness is Grounded when CLAIMCHECK annotators linked it to at least one target claim.",
            "source_repository": "https://github.com/JHU-CLSP/CLAIMCHECK",
            "paper": "https://aclanthology.org/2025.findings-emnlp.1185/",
            "license_note": "No upstream LICENSE file detected; raw and row-level text outputs are intentionally gitignored.",
            "splits": summaries,
            "all": summarize(all_rows, summaries["pilot"]["paper_review_pair_count"] + summaries["main"]["paper_review_pair_count"], "all"),
        },
    )


if __name__ == "__main__":
    main()
