from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, cosine_sparse, ensure_dirs, read_jsonl, tokenize, write_json


TOP_K = 5


def build_idf(docs: list[dict[str, Any]]) -> dict[str, float]:
    df = Counter()
    for doc in docs:
        df.update(set(tokenize(doc["text"])))
    n_docs = len(docs)
    return {term: math.log((n_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}


def vectorize(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    max_tf = max(counts.values())
    return {term: (0.5 + 0.5 * count / max_tf) * idf.get(term, 0.0) for term, count in counts.items()}


def main() -> None:
    ensure_dirs()
    weakness_path = DATA_DIR / "human_weaknesses.jsonl"
    blocks_path = DATA_DIR / "evidence_blocks.jsonl"
    if not weakness_path.exists():
        raise SystemExit("human_weaknesses.jsonl missing; run extract_human_weaknesses.py first")
    if not blocks_path.exists():
        raise SystemExit("evidence_blocks.jsonl missing; run build_evidence_blocks.py first")

    weaknesses = read_jsonl(weakness_path)
    blocks = read_jsonl(blocks_path)
    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in blocks:
        blocks_by_paper[block["paper_id"]].append(block)

    idf_by_paper: dict[str, dict[str, float]] = {}
    vectors_by_paper: dict[str, list[tuple[dict[str, float], dict[str, Any]]]] = {}
    for paper_id, paper_blocks in blocks_by_paper.items():
        idf = build_idf(paper_blocks)
        idf_by_paper[paper_id] = idf
        vectors_by_paper[paper_id] = [(vectorize(block["text"], idf), block) for block in paper_blocks]

    non_empty = 0
    out_path = DATA_DIR / "retrieval_tfidf_top5.jsonl"
    with out_path.open("w", encoding="utf-8") as out:
        for weakness in weaknesses:
            idf = idf_by_paper.get(weakness["paper_id"], {})
            query_vec = vectorize(weakness["weakness_text"], idf)
            ranked = []
            for doc_vec, block in vectors_by_paper.get(weakness["paper_id"], []):
                score = cosine_sparse(query_vec, doc_vec)
                if score > 0:
                    ranked.append((score, block))
            ranked.sort(key=lambda item: item[0], reverse=True)
            top = ranked[:TOP_K]
            if top:
                non_empty += 1
            item = {
                "weakness_id": weakness["weakness_id"],
                "paper_id": weakness["paper_id"],
                "forum": weakness["forum"],
                "weakness_text": weakness["weakness_text"],
                "category_rule": weakness["category_rule"],
                "source_section": weakness["source_section"],
                "retriever": "tfidf_cosine",
                "top_k": TOP_K,
                "retrieved": [
                    {
                        "rank": rank,
                        "score": round(score, 6),
                        "block_id": block["block_id"],
                        "section_path": block["section_path"],
                        "section_type": block["section_type"],
                        "text": block["text"][:900],
                    }
                    for rank, (score, block) in enumerate(top, start=1)
                ],
            }
            out.write(json.dumps(item, ensure_ascii=False) + "\n")

    summary = {
        "retriever": "tfidf_cosine",
        "weakness_count": len(weaknesses),
        "non_empty_retrieval_count": non_empty,
        "non_empty_rate": round(non_empty / len(weaknesses), 4) if weaknesses else 0,
        "top_k": TOP_K,
        "note": "Dependency-free lexical TF-IDF cosine baseline. This is not neural dense retrieval.",
    }
    write_json(DATA_DIR / "retrieval_tfidf_summary.json", summary)
    print(f"Wrote {out_path}")
    print(f"Wrote {DATA_DIR / 'retrieval_tfidf_summary.json'}")
    print(f"queries={len(weaknesses)} non_empty={non_empty}")


if __name__ == "__main__":
    main()

