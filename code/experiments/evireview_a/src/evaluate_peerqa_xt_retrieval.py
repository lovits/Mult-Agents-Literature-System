from __future__ import annotations

import json
import math
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any

from common import DATA_DIR, REPORT_DIR, cosine_sparse, ensure_dirs, normalize_ws, tokenize, write_json, write_jsonl


DATASET_ID = "UKPLab/PeerQA-XT"
CONFIG = "default"
DEFAULT_SPLIT = "test"
DEFAULT_LIMIT = 80
PAGE_SIZE = 100
TOP_K_VALUES = (1, 3, 5)
CHUNK_TOKENS = 170
CHUNK_OVERLAP = 45
MIN_ANSWER_RECALL = 0.35
OUT_METRICS = "peerqa_xt_retrieval_metrics.json"
OUT_PREDICTIONS = "peerqa_xt_retrieval_predictions.jsonl"

STOPWORDS = {
    "about",
    "after",
    "also",
    "among",
    "and",
    "are",
    "because",
    "been",
    "being",
    "between",
    "both",
    "can",
    "could",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "into",
    "may",
    "more",
    "most",
    "not",
    "our",
    "out",
    "over",
    "paper",
    "study",
    "such",
    "than",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "those",
    "through",
    "using",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def fetch_rows(split: str, offset: int, length: int) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "dataset": DATASET_ID,
            "config": CONFIG,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )
    with urllib.request.urlopen(f"https://datasets-server.huggingface.co/rows?{params}", timeout=90) as response:
        return json.load(response)


def fetch_sample(split: str, limit: int) -> tuple[list[dict[str, Any]], int | None]:
    rows: list[dict[str, Any]] = []
    offset = 0
    total_available = None
    while len(rows) < limit:
        payload = fetch_rows(split, offset, min(PAGE_SIZE, limit - len(rows)))
        total_available = payload.get("num_rows_total")
        batch = payload.get("rows") or []
        if not batch:
            break
        rows.extend(item["row"] | {"row_index": item["row_idx"]} for item in batch)
        offset += len(batch)
    return rows, total_available


def answer_terms(answer: str) -> set[str]:
    return {
        token
        for token in tokenize(answer)
        if len(token) >= 3 and token not in STOPWORDS and not token.isdigit()
    }


def heading_for_position(text: str, char_pos: int) -> str:
    heading = "document"
    for match in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text):
        if match.start() > char_pos:
            break
        heading = normalize_ws(match.group(1))[:120] or heading
    return heading


def chunk_paper(text: str) -> list[dict[str, Any]]:
    tokens = list(re.finditer(r"\S+", text))
    chunks = []
    if not tokens:
        return chunks
    step = max(1, CHUNK_TOKENS - CHUNK_OVERLAP)
    for chunk_idx, start in enumerate(range(0, len(tokens), step)):
        end = min(len(tokens), start + CHUNK_TOKENS)
        if end <= start:
            break
        char_start = tokens[start].start()
        char_end = tokens[end - 1].end()
        chunk_text = normalize_ws(text[char_start:char_end])
        if len(chunk_text) < 80:
            continue
        chunks.append(
            {
                "chunk_id": f"c{chunk_idx:04d}",
                "chunk_index": chunk_idx,
                "heading": heading_for_position(text, char_start),
                "text": chunk_text,
                "token_count": end - start,
            }
        )
        if end == len(tokens):
            break
    return chunks


def build_idf(chunks: list[dict[str, Any]]) -> dict[str, float]:
    df = Counter()
    for chunk in chunks:
        df.update(set(tokenize(chunk["text"])))
    n_docs = len(chunks)
    return {term: math.log((n_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}


def vectorize(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    max_tf = max(counts.values())
    return {term: (0.5 + 0.5 * count / max_tf) * idf.get(term, 0.0) for term, count in counts.items()}


def bm25_scores(query: str, chunks: list[dict[str, Any]]) -> dict[str, float]:
    query_terms = Counter(tokenize(query))
    if not query_terms or not chunks:
        return {}
    docs = [Counter(tokenize(chunk["text"])) for chunk in chunks]
    doc_lens = [sum(doc.values()) for doc in docs]
    avg_len = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
    df = Counter()
    for doc in docs:
        df.update(set(doc))
    k1 = 1.4
    b = 0.75
    scores = {}
    for chunk, doc, doc_len in zip(chunks, docs, doc_lens):
        score = 0.0
        for term, qtf in query_terms.items():
            tf = doc.get(term, 0)
            if not tf:
                continue
            idf = math.log(1 + (len(chunks) - df[term] + 0.5) / (df[term] + 0.5))
            score += qtf * idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_len))
        scores[chunk["chunk_id"]] = score
    return scores


def tfidf_scores(query: str, chunks: list[dict[str, Any]], idf: dict[str, float]) -> dict[str, float]:
    query_vec = vectorize(query, idf)
    scores = {}
    for chunk in chunks:
        score = cosine_sparse(query_vec, vectorize(chunk["text"], idf))
        scores[chunk["chunk_id"]] = score
    return scores


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    max_score = max(scores.values()) if scores else 0.0
    if max_score <= 0:
        return {key: 0.0 for key in scores}
    return {key: value / max_score for key, value in scores.items()}


def rank_chunks(method: str, query: str, chunks: list[dict[str, Any]], idf: dict[str, float]) -> list[dict[str, Any]]:
    bm25 = bm25_scores(query, chunks)
    tfidf = tfidf_scores(query, chunks, idf)
    if method == "bm25_question":
        scores = bm25
    elif method == "tfidf_question":
        scores = tfidf
    elif method == "hybrid_question":
        bm25_norm = normalize_scores(bm25)
        tfidf_norm = normalize_scores(tfidf)
        scores = {
            chunk["chunk_id"]: 0.6 * bm25_norm.get(chunk["chunk_id"], 0.0)
            + 0.4 * tfidf_norm.get(chunk["chunk_id"], 0.0)
            for chunk in chunks
        }
    elif method == "oracle_answer_query":
        scores = bm25_scores(query, chunks)
    else:
        raise ValueError(f"Unknown method: {method}")

    ranked = sorted(chunks, key=lambda chunk: scores.get(chunk["chunk_id"], 0.0), reverse=True)
    return [
        {
            "rank": rank,
            "chunk_id": chunk["chunk_id"],
            "score": round(scores.get(chunk["chunk_id"], 0.0), 6),
            "heading": chunk["heading"],
            "text": chunk["text"][:700],
        }
        for rank, chunk in enumerate(ranked[: max(TOP_K_VALUES)], start=1)
    ]


def coverage_at_k(retrieved: list[dict[str, Any]], terms: set[str], k: int) -> float:
    if not terms:
        return 0.0
    joined = " ".join(item["text"] for item in retrieved[:k])
    found = set(tokenize(joined)) & terms
    return len(found) / len(terms)


def evaluate_method(rows: list[dict[str, Any]], method: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    predictions = []
    coverage_sums = Counter()
    hit_counts = Counter()
    usable_rows = 0
    for row in rows:
        chunks = chunk_paper(row.get("paper", ""))
        terms = answer_terms(row.get("answer", ""))
        if not chunks or not terms:
            continue
        usable_rows += 1
        idf = build_idf(chunks)
        query = row["answer"] if method == "oracle_answer_query" else row["question"]
        retrieved = rank_chunks(method, query, chunks, idf)
        per_k = {}
        for k in TOP_K_VALUES:
            coverage = coverage_at_k(retrieved, terms, k)
            coverage_sums[k] += coverage
            hit_counts[k] += int(coverage >= MIN_ANSWER_RECALL)
            per_k[f"answer_token_recall_at_{k}"] = round(coverage, 4)
            per_k[f"answer_support_hit_at_{k}"] = coverage >= MIN_ANSWER_RECALL
        predictions.append(
            {
                "method": method,
                "row_index": row["row_index"],
                "pid": row["pid"],
                "qid": row["qid"],
                "domain": row.get("domain", ""),
                "question": normalize_ws(row["question"]),
                "answer": normalize_ws(row["answer"]),
                "answer_term_count": len(terms),
                "paper_chunk_count": len(chunks),
                **per_k,
                "retrieved": retrieved,
            }
        )

    metrics = {
        "usable_rows": usable_rows,
        "min_answer_recall_for_hit": MIN_ANSWER_RECALL,
    }
    for k in TOP_K_VALUES:
        metrics[f"mean_answer_token_recall_at_{k}"] = round(coverage_sums[k] / usable_rows, 4) if usable_rows else 0.0
        metrics[f"answer_support_hit_at_{k}"] = round(hit_counts[k] / usable_rows, 4) if usable_rows else 0.0
    return metrics, predictions


def main() -> None:
    ensure_dirs()
    split = os.getenv("PEERQA_XT_SPLIT", DEFAULT_SPLIT)
    limit = int(os.getenv("PEERQA_XT_LIMIT", str(DEFAULT_LIMIT)))
    rows, total_available = fetch_sample(split, limit)

    methods = ["bm25_question", "tfidf_question", "hybrid_question", "oracle_answer_query"]
    metrics = {
        "status": "ok",
        "dataset_id": DATASET_ID,
        "config": CONFIG,
        "split": split,
        "source_url": f"https://huggingface.co/datasets/{DATASET_ID}",
        "license": "cc-by-nc-sa-4.0",
        "total_available_rows": total_available,
        "downloaded_rows": len(rows),
        "limit": limit,
        "chunk_tokens": CHUNK_TOKENS,
        "chunk_overlap": CHUNK_OVERLAP,
        "evaluation_note": "Answer-support retrieval proxy: a hit requires retrieved chunks to cover at least 35% of non-stopword answer tokens. The dataset has answers but no gold evidence spans.",
        "methods": {},
    }
    all_predictions = []
    for method in methods:
        method_metrics, method_predictions = evaluate_method(rows, method)
        metrics["methods"][method] = method_metrics
        all_predictions.extend(method_predictions)

    write_json(DATA_DIR / OUT_METRICS, metrics)
    write_jsonl(DATA_DIR / OUT_PREDICTIONS, all_predictions)

    lines = [
        "# PeerQA-XT Paper-RAG Retrieval Baseline",
        "",
        "This experiment uses PeerQA-XT as a no-new-manual-label Paper-RAG QA dataset.",
        "",
        f"- Dataset: https://huggingface.co/datasets/{DATASET_ID}",
        "- Paper: https://arxiv.org/abs/2502.13668",
        "- License: CC-BY-NC-SA-4.0",
        f"- Split / rows used: `{split}` / {len(rows)} of {total_available}",
        "- Gold evidence spans are not provided, so this report uses answer-token support as a retrieval proxy.",
        "",
        "| Method | Rows | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in methods:
        item = metrics["methods"][method]
        lines.append(
            f"| {method} | {item['usable_rows']} | {item['answer_support_hit_at_1']} | "
            f"{item['answer_support_hit_at_3']} | {item['answer_support_hit_at_5']} | "
            f"{item['mean_answer_token_recall_at_5']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- PeerQA-XT fits the thesis retrieval module because each row has a peer-review-derived question, a final answer, and full paper context.",
            "- `hybrid_question` is the fair baseline for question-only retrieval; `oracle_answer_query` is a diagnostic ceiling, not a deployable system.",
            "- The next improvement should add section-aware / hierarchical retrieval tools and compare them against this question-only floor.",
        ]
    )
    (REPORT_DIR / "peerqa_xt_retrieval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {DATA_DIR / OUT_METRICS}")
    print(f"Wrote {REPORT_DIR / 'peerqa_xt_retrieval_report.md'}")


if __name__ == "__main__":
    main()

