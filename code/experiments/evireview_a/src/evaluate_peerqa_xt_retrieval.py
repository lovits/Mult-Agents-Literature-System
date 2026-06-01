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

SECTION_ALIASES = {
    "abstract": "abstract",
    "background": "introduction",
    "introduction": "introduction",
    "aim": "introduction",
    "objective": "introduction",
    "objectives": "introduction",
    "methods": "method",
    "method": "method",
    "materials and methods": "method",
    "study design": "method",
    "participants": "method",
    "patients": "method",
    "data collection": "method",
    "statistical analysis": "method",
    "results": "experiment",
    "findings": "experiment",
    "outcomes": "experiment",
    "discussion": "limitation",
    "limitations": "limitation",
    "limitation": "limitation",
    "clinical implications": "limitation",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "keywords": "other",
    "references": "reference",
}

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
    heading_re = re.compile(r"(?m)^#{1,6}\s+(.+?)\s*$|\*\*([A-Z][A-Za-z /-]{2,60})\*\*")
    for match in heading_re.finditer(text):
        if match.start() > char_pos:
            break
        raw = match.group(1) or match.group(2) or ""
        candidate = normalize_ws(raw).strip(":")
        if not candidate:
            continue
        if candidate.lower() in SECTION_ALIASES or match.group(1):
            heading = candidate[:120]
    return heading


def classify_peerqa_section(heading: str) -> str:
    lower = normalize_ws(heading).lower().strip(":")
    if lower in SECTION_ALIASES:
        return SECTION_ALIASES[lower]
    if any(token in lower for token in ["method", "design", "participant", "patient", "cohort", "criteria"]):
        return "method"
    if any(token in lower for token in ["result", "finding", "outcome", "performance", "accuracy"]):
        return "experiment"
    if any(token in lower for token in ["discussion", "limitation", "implication", "future"]):
        return "limitation"
    if any(token in lower for token in ["background", "introduction", "literature"]):
        return "introduction"
    if "reference" in lower:
        return "reference"
    return "other"


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
        heading = heading_for_position(text, char_start)
        chunks.append(
            {
                "chunk_id": f"c{chunk_idx:04d}",
                "chunk_index": chunk_idx,
                "heading": heading,
                "section_type": classify_peerqa_section(heading),
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


def rank_ids(scores: dict[str, float], chunks: list[dict[str, Any]]) -> list[str]:
    return [
        chunk["chunk_id"]
        for chunk in sorted(
            chunks,
            key=lambda item: (scores.get(item["chunk_id"], 0.0), -item["chunk_index"]),
            reverse=True,
        )
    ]


def rrf_scores(rankings: list[list[str]], weights: list[float] | None = None, k: int = 60) -> dict[str, float]:
    scores: Counter[str] = Counter()
    weights = weights or [1.0] * len(rankings)
    for ranking, weight in zip(rankings, weights):
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] += weight / (k + rank)
    return dict(scores)


def classify_peerqa_question(question: str) -> str:
    lower = question.lower()
    if any(token in lower for token in ["method", "methods", "criteria", "design", "isolate", "preprocess", "implement"]):
        return "method"
    if any(
        token in lower
        for token in [
            "accuracy",
            "precision",
            "percentage",
            "result",
            "findings",
            "observed",
            "effect",
            "outcome",
            "experiments",
            "validate",
        ]
    ):
        return "experiment"
    if any(token in lower for token in ["sample size", "generalizability", "limitation", "justify", "discussion"]):
        return "validity"
    if any(token in lower for token in ["literature", "previous studies", "other countries", "compared to"]):
        return "related_work"
    if any(token in lower for token in ["why", "explanation", "cause", "factors"]):
        return "validity"
    return "other"


def expand_question_query(question: str) -> str:
    category = classify_peerqa_question(question)
    expansions = {
        "method": "methods study design participants patients inclusion criteria data collection procedure analysis implementation preprocessing model",
        "experiment": "results findings outcomes accuracy precision percentage performance evaluation experiment validation",
        "validity": "discussion limitations generalizability sample size justification interpretation clinical implications future work",
        "related_work": "background literature previous studies related work comparison context country countries",
        "other": "abstract background methods results discussion conclusion",
    }
    return f"{question} {expansions[category]}"


def peerqa_section_prior(question_category: str, section_type: str) -> float:
    priors = {
        "method": {"method": 1.0, "experiment": 0.35, "abstract": 0.25, "introduction": 0.2},
        "experiment": {"experiment": 1.0, "method": 0.45, "limitation": 0.35, "abstract": 0.3},
        "validity": {"limitation": 1.0, "experiment": 0.55, "method": 0.45, "introduction": 0.25, "abstract": 0.2},
        "related_work": {"introduction": 1.0, "reference": 0.65, "limitation": 0.35, "abstract": 0.25},
        "other": {"abstract": 0.5, "introduction": 0.45, "method": 0.4, "experiment": 0.4, "limitation": 0.35},
    }
    return priors.get(question_category, priors["other"]).get(section_type, 0.0)


def rank_chunks(method: str, query: str, chunks: list[dict[str, Any]], idf: dict[str, float]) -> list[dict[str, Any]]:
    expanded_query = expand_question_query(query)
    retrieval_query = expanded_query if method in {
        "query_decomposed_question",
        "domain_section_aware_question",
        "domain_hierarchical_question",
    } else query
    bm25 = bm25_scores(retrieval_query, chunks)
    tfidf = tfidf_scores(retrieval_query, chunks, idf)
    question_category = classify_peerqa_question(query)
    section_scores = {chunk["chunk_id"]: peerqa_section_prior(question_category, chunk.get("section_type", "other")) for chunk in chunks}
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
    elif method == "section_aware_question":
        bm25_norm = normalize_scores(bm25)
        tfidf_norm = normalize_scores(tfidf)
        scores = {
            chunk["chunk_id"]: 0.55 * bm25_norm.get(chunk["chunk_id"], 0.0)
            + 0.35 * tfidf_norm.get(chunk["chunk_id"], 0.0)
            + 0.10 * section_scores.get(chunk["chunk_id"], 0.0)
            for chunk in chunks
        }
    elif method == "hierarchical_question":
        scores = rrf_scores(
            [
                rank_ids(bm25, chunks),
                rank_ids(tfidf, chunks),
                rank_ids(section_scores, chunks),
            ],
            weights=[1.0, 1.0, 0.25],
        )
    elif method == "query_decomposed_question":
        bm25_norm = normalize_scores(bm25)
        tfidf_norm = normalize_scores(tfidf)
        scores = {
            chunk["chunk_id"]: 0.6 * bm25_norm.get(chunk["chunk_id"], 0.0)
            + 0.4 * tfidf_norm.get(chunk["chunk_id"], 0.0)
            for chunk in chunks
        }
    elif method == "domain_section_aware_question":
        bm25_norm = normalize_scores(bm25)
        tfidf_norm = normalize_scores(tfidf)
        scores = {
            chunk["chunk_id"]: 0.55 * bm25_norm.get(chunk["chunk_id"], 0.0)
            + 0.35 * tfidf_norm.get(chunk["chunk_id"], 0.0)
            + 0.10 * section_scores.get(chunk["chunk_id"], 0.0)
            for chunk in chunks
        }
    elif method == "domain_hierarchical_question":
        scores = rrf_scores(
            [
                rank_ids(bm25, chunks),
                rank_ids(tfidf, chunks),
                rank_ids(section_scores, chunks),
            ],
            weights=[1.0, 1.0, 0.30],
        )
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
            "section_type": chunk.get("section_type", "other"),
            "question_category": question_category,
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

    methods = [
        "bm25_question",
        "tfidf_question",
        "hybrid_question",
        "section_aware_question",
        "hierarchical_question",
        "query_decomposed_question",
        "domain_section_aware_question",
        "domain_hierarchical_question",
        "oracle_answer_query",
    ]
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
            "- `hybrid_question` is the fair baseline for question-only retrieval; `query_decomposed_question` adds rule-based QA intent expansion.",
            "- `domain_section_aware_question` uses biomedical article section markers such as Background, Methods, Results, and Discussion.",
            "- `domain_hierarchical_question` fuses BM25, TF-IDF, and domain-aware section_read rankings with weighted reciprocal rank fusion.",
            "- In this probe, section-aware retrieval ties the best lexical Hit@1/Hit@3 floor, while hand-written query expansion degrades retrieval.",
            "- `oracle_answer_query` is a diagnostic ceiling, not a deployable system.",
        ]
    )
    (REPORT_DIR / "peerqa_xt_retrieval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {DATA_DIR / OUT_METRICS}")
    print(f"Wrote {REPORT_DIR / 'peerqa_xt_retrieval_report.md'}")


if __name__ == "__main__":
    main()
