from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, section_prior, write_json, write_jsonl
from evaluate_claimcheck_retrieval import char_ngrams, set_cosine


TOP_K = 5
LEXICAL_WEIGHT = 0.45
CHAR_WEIGHT = 0.35
SECTION_WEIGHT = 0.20


def score_block(weakness: dict[str, Any], block: dict[str, Any]) -> tuple[float, float, float, float]:
    lexical = set_cosine(weakness["weakness_text"], block["text"])
    char = set_cosine(weakness["weakness_text"], block["text"], char_ngrams)
    prior = section_prior(weakness["category"], block["section_type"])
    score = LEXICAL_WEIGHT * lexical + CHAR_WEIGHT * char + SECTION_WEIGHT * prior
    return score, lexical, char, prior


def main() -> None:
    ensure_dirs()
    generated_path = DATA_DIR / "rubric_agent_weaknesses.jsonl"
    if not generated_path.exists():
        raise SystemExit("rubric_agent_weaknesses.jsonl missing; run generate_rubric_agent_weaknesses.py first")

    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)

    rows = []
    top1_section_hits = 0
    non_empty = 0
    for weakness in read_jsonl(generated_path):
        scored = []
        for block in blocks_by_paper.get(weakness["paper_id"], []):
            score, lexical, char, prior = score_block(weakness, block)
            scored.append((score, lexical, char, prior, block))
        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[:TOP_K]
        if top:
            non_empty += 1
            top1_section_hits += int(top[0][3] > 0)
        rows.append(
            {
                "generated_weakness_id": weakness["generated_weakness_id"],
                "paper_id": weakness["paper_id"],
                "forum": weakness["forum"],
                "weakness_text": weakness["weakness_text"],
                "category": weakness["category"],
                "severity": weakness["severity"],
                "reviewer_role": weakness["reviewer_role"],
                "retriever": "rubric_section_aware_lexical_v0",
                "top_k": TOP_K,
                "weights": {"lexical": LEXICAL_WEIGHT, "char": CHAR_WEIGHT, "section": SECTION_WEIGHT},
                "retrieved": [
                    {
                        "rank": rank,
                        "score": round(score, 6),
                        "lexical_score": round(lexical, 6),
                        "char_score": round(char, 6),
                        "section_prior": prior,
                        "block_id": block["block_id"],
                        "section_path": block["section_path"],
                        "section_type": block["section_type"],
                        "text": block["text"][:900],
                    }
                    for rank, (score, lexical, char, prior, block) in enumerate(top, start=1)
                ],
            }
        )

    write_jsonl(DATA_DIR / "rubric_agent_retrieval_top5.jsonl", rows)
    summary = {
        "retriever": "rubric_section_aware_lexical_v0",
        "generated_weakness_count": len(rows),
        "non_empty_retrieval_count": non_empty,
        "top1_section_prior_hit_rate": round(top1_section_hits / non_empty, 4) if non_empty else 0.0,
        "category_counts": dict(Counter(row["category"] for row in rows)),
        "weights": {"lexical": LEXICAL_WEIGHT, "char": CHAR_WEIGHT, "section": SECTION_WEIGHT},
        "warning": "Retrieval is for deterministic generated weakness pipeline validation; evidence support still needs verifier evaluation.",
    }
    write_json(DATA_DIR / "rubric_agent_retrieval_summary.json", summary)
    print(
        "rubric_agent_retrieval "
        f"weaknesses={len(rows)} non_empty={non_empty} top1_section_hit={summary['top1_section_prior_hit_rate']}"
    )


if __name__ == "__main__":
    main()
