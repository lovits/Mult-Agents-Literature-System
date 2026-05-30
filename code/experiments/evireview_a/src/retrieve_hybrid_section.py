from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, section_prior, write_json


TOP_K = 5
BM25_WEIGHT = 0.55
TFIDF_WEIGHT = 0.35
SECTION_WEIGHT = 0.10


def normalize_scores(items: list[dict[str, Any]]) -> dict[str, float]:
    if not items:
        return {}
    max_score = max(float(item["score"]) for item in items) or 1.0
    return {item["block_id"]: float(item["score"]) / max_score for item in items}


def load_retrieval(path):
    mapping = {}
    for row in read_jsonl(path):
        mapping[row["weakness_id"]] = row
    return mapping


def main() -> None:
    ensure_dirs()
    bm25_path = DATA_DIR / "retrieval_bm25_top5.jsonl"
    tfidf_path = DATA_DIR / "retrieval_tfidf_top5.jsonl"
    blocks_path = DATA_DIR / "evidence_blocks.jsonl"
    weakness_path = DATA_DIR / "human_weaknesses.jsonl"
    for path in [bm25_path, tfidf_path, blocks_path, weakness_path]:
        if not path.exists():
            raise SystemExit(f"{path.name} missing; run previous retrieval scripts first")

    bm25 = load_retrieval(bm25_path)
    tfidf = load_retrieval(tfidf_path)
    weaknesses = {row["weakness_id"]: row for row in read_jsonl(weakness_path)}
    block_lookup = {row["block_id"]: row for row in read_jsonl(blocks_path)}

    hybrid_non_empty = 0
    section_non_empty = 0
    hybrid_path = DATA_DIR / "retrieval_hybrid_top5.jsonl"
    section_path = DATA_DIR / "retrieval_section_hybrid_top5.jsonl"
    with hybrid_path.open("w", encoding="utf-8") as hybrid_out, section_path.open("w", encoding="utf-8") as section_out:
        for weakness_id, weakness in weaknesses.items():
            bm25_row = bm25.get(weakness_id, {**weakness, "retrieved": []})
            tfidf_row = tfidf.get(weakness_id, {**weakness, "retrieved": []})
            candidates: dict[str, dict[str, Any]] = {}
            for source_row in [bm25_row, tfidf_row]:
                for retrieved in source_row.get("retrieved", []):
                    block_id = retrieved["block_id"]
                    block = block_lookup[block_id]
                    candidates[block_id] = {
                        "block_id": block_id,
                        "section_path": block["section_path"],
                        "section_type": block["section_type"],
                        "text": block["text"][:900],
                    }

            bm25_scores = normalize_scores(bm25_row.get("retrieved", []))
            tfidf_scores = normalize_scores(tfidf_row.get("retrieved", []))
            scored = []
            section_scored = []
            for block_id, payload in candidates.items():
                hybrid_score = BM25_WEIGHT * bm25_scores.get(block_id, 0.0) + TFIDF_WEIGHT * tfidf_scores.get(block_id, 0.0)
                prior = section_prior(weakness["category_rule"], payload["section_type"])
                section_score = hybrid_score + SECTION_WEIGHT * prior
                scored.append((hybrid_score, payload, prior))
                section_scored.append((section_score, payload, prior))

            scored.sort(key=lambda item: item[0], reverse=True)
            section_scored.sort(key=lambda item: item[0], reverse=True)
            if scored:
                hybrid_non_empty += 1
            if section_scored:
                section_non_empty += 1

            base = {
                "weakness_id": weakness_id,
                "paper_id": weakness["paper_id"],
                "forum": weakness["forum"],
                "weakness_text": weakness["weakness_text"],
                "category_rule": weakness["category_rule"],
                "source_section": weakness["source_section"],
                "top_k": TOP_K,
            }
            hybrid_out.write(
                json.dumps(
                    {
                        **base,
                        "retriever": "hybrid_bm25_tfidf",
                        "weights": {"bm25": BM25_WEIGHT, "tfidf": TFIDF_WEIGHT},
                        "retrieved": [
                            {
                                "rank": rank,
                                "score": round(score, 6),
                                "section_prior": prior,
                                **payload,
                            }
                            for rank, (score, payload, prior) in enumerate(scored[:TOP_K], start=1)
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            section_out.write(
                json.dumps(
                    {
                        **base,
                        "retriever": "section_aware_hybrid",
                        "weights": {"bm25": BM25_WEIGHT, "tfidf": TFIDF_WEIGHT, "section": SECTION_WEIGHT},
                        "retrieved": [
                            {
                                "rank": rank,
                                "score": round(score, 6),
                                "section_prior": prior,
                                **payload,
                            }
                            for rank, (score, payload, prior) in enumerate(section_scored[:TOP_K], start=1)
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    summary = {
        "hybrid": {
            "output": str(hybrid_path.relative_to(DATA_DIR.parent)),
            "non_empty_retrieval_count": hybrid_non_empty,
        },
        "section_aware_hybrid": {
            "output": str(section_path.relative_to(DATA_DIR.parent)),
            "non_empty_retrieval_count": section_non_empty,
        },
        "weights": {"bm25": BM25_WEIGHT, "tfidf": TFIDF_WEIGHT, "section": SECTION_WEIGHT},
        "top_k": TOP_K,
        "note": "Hybrid scores fuse normalized BM25 and TF-IDF candidate scores. Section-aware hybrid adds a lightweight category-to-section prior inspired by rubric-guided grounding.",
    }
    write_json(DATA_DIR / "retrieval_hybrid_summary.json", summary)
    print(f"Wrote {hybrid_path}")
    print(f"Wrote {section_path}")
    print(f"Wrote {DATA_DIR / 'retrieval_hybrid_summary.json'}")


if __name__ == "__main__":
    main()

