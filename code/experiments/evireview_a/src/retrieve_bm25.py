from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

from common import DATA_DIR, ensure_dirs, tokenize, write_json


TOP_K = 5
K1 = 1.5
B = 0.75


def load_jsonl(path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def bm25_scores(query_tokens: list[str], docs: list[dict]) -> list[tuple[float, dict]]:
    if not docs:
        return []
    tokenized = [tokenize(doc["text"]) for doc in docs]
    doc_lens = [len(tokens) for tokens in tokenized]
    avgdl = sum(doc_lens) / len(doc_lens)
    df = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    q_counts = Counter(query_tokens)
    scores = []
    n_docs = len(docs)
    for doc, tokens, doc_len in zip(docs, tokenized, doc_lens):
        tf = Counter(tokens)
        score = 0.0
        for term, qtf in q_counts.items():
            if term not in tf:
                continue
            idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + K1 * (1 - B + B * doc_len / avgdl)
            score += idf * (tf[term] * (K1 + 1) / denom) * qtf
        if score > 0:
            scores.append((score, doc))
    return sorted(scores, key=lambda item: item[0], reverse=True)


def main() -> None:
    ensure_dirs()
    weakness_path = DATA_DIR / "human_weaknesses.jsonl"
    blocks_path = DATA_DIR / "evidence_blocks.jsonl"
    if not weakness_path.exists():
        raise SystemExit("human_weaknesses.jsonl missing; run extract_human_weaknesses.py first")
    if not blocks_path.exists():
        raise SystemExit("evidence_blocks.jsonl missing; run build_evidence_blocks.py first")

    weaknesses = list(load_jsonl(weakness_path))
    blocks_by_paper: dict[str, list[dict]] = defaultdict(list)
    for block in load_jsonl(blocks_path):
        blocks_by_paper[block["paper_id"]].append(block)

    results = []
    non_empty = 0
    with (DATA_DIR / "retrieval_bm25_top5.jsonl").open("w", encoding="utf-8") as out:
        for weakness in weaknesses:
            query_tokens = tokenize(weakness["weakness_text"])
            ranked = bm25_scores(query_tokens, blocks_by_paper.get(weakness["paper_id"], []))[:TOP_K]
            if ranked:
                non_empty += 1
            item = {
                "weakness_id": weakness["weakness_id"],
                "paper_id": weakness["paper_id"],
                "forum": weakness["forum"],
                "weakness_text": weakness["weakness_text"],
                "category_rule": weakness["category_rule"],
                "source_section": weakness["source_section"],
                "top_k": TOP_K,
                "retrieved": [
                    {
                        "rank": rank,
                        "score": round(score, 6),
                        "block_id": doc["block_id"],
                        "section_path": doc["section_path"],
                        "section_type": doc["section_type"],
                        "text": doc["text"][:900],
                    }
                    for rank, (score, doc) in enumerate(ranked, start=1)
                ],
            }
            results.append(item)
            out.write(json.dumps(item, ensure_ascii=False) + "\n")

    section_hits = Counter()
    for item in results:
        for retrieved in item["retrieved"][:1]:
            section_hits[retrieved["section_type"]] += 1
    summary = {
        "weakness_count": len(weaknesses),
        "retrieval_result_count": len(results),
        "non_empty_retrieval_count": non_empty,
        "non_empty_rate": round(non_empty / len(weaknesses), 4) if weaknesses else 0,
        "top_k": TOP_K,
        "bm25_k1": K1,
        "bm25_b": B,
        "top1_section_type_counts": dict(section_hits),
        "note": "This is a lexical BM25 baseline over evidence blocks from the same paper. It is not a gold evidence evaluation yet.",
    }
    write_json(DATA_DIR / "retrieval_bm25_summary.json", summary)
    print(f"Wrote {DATA_DIR / 'retrieval_bm25_top5.jsonl'}")
    print(f"Wrote {DATA_DIR / 'retrieval_bm25_summary.json'}")
    print(f"queries={len(weaknesses)} non_empty={non_empty}")


if __name__ == "__main__":
    main()

