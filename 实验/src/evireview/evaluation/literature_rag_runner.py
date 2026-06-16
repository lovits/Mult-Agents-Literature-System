import math
import re
from collections import Counter

from pydantic import BaseModel

from evireview.dao.literature import LiteratureCorpus, LiteratureDocument


class LiteratureQuery(BaseModel):
    query_id: str
    query: str
    aspect: str
    as_of_year: int
    gold_doc_ids: list[str]


SYSTEM_NAMES = (
    "L0_no_literature",
    "L1_keyword",
    "L2_hybrid",
    "L3_hybrid_metadata_filter",
)


def run_literature_rag_baselines(
    corpus: LiteratureCorpus,
    queries: list[LiteratureQuery],
    top_k: int = 10,
) -> dict:
    rankings = {
        "L0_no_literature": {query.query_id: [] for query in queries},
        "L1_keyword": {
            query.query_id: _rank_keyword(corpus.documents, query)[:top_k]
            for query in queries
        },
        "L2_hybrid": {
            query.query_id: _rank_hybrid(corpus.documents, query)[:top_k]
            for query in queries
        },
    }
    rankings["L3_hybrid_metadata_filter"] = {
        query.query_id: [
            result
            for result in _rank_hybrid(corpus.documents, query)
            if result["year"] is not None and result["year"] <= query.as_of_year
        ][:top_k]
        for query in queries
    }
    return {
        "protocol": {
            "name": "controlled-literature-rag-v1",
            "frozen_local_corpus": True,
            "online_retrieval": False,
            "metadata_year_filter": True,
            "gold_used_only_for_metrics": True,
            "purpose": "novelty_related_work_and_missing_baseline_support",
        },
        "dataset": corpus.audit_summary(),
        "queries": {
            "count": len(queries),
            "items": [query.model_dump() for query in queries],
        },
        "systems": {
            system: _evaluate_rankings(rankings[system], queries, top_k)
            for system in SYSTEM_NAMES
        },
        "sample_rankings": rankings,
    }


def _rank_keyword(
    documents: list[LiteratureDocument],
    query: LiteratureQuery,
) -> list[dict]:
    scored = [
        _ranking_item(
            document,
            _bm25_like_score(query.query, document.text),
            query,
        )
        for document in documents
    ]
    return _sort(scored)


def _rank_hybrid(
    documents: list[LiteratureDocument],
    query: LiteratureQuery,
) -> list[dict]:
    scored = []
    for document in documents:
        text_score = _bm25_like_score(query.query, document.text)
        title_score = _token_f1(query.query, document.title)
        year_bonus = 0.05 if document.year and document.year <= query.as_of_year else 0.0
        score = 0.65 * text_score + 0.35 * title_score + year_bonus
        scored.append(_ranking_item(document, score, query))
    return _sort(scored)


def _ranking_item(
    document: LiteratureDocument,
    score: float,
    query: LiteratureQuery,
) -> dict:
    return {
        "doc_id": document.doc_id,
        "title": document.title,
        "year": document.year,
        "source_path": document.source_path,
        "score": score,
        "relevance": _token_f1(query.query, f"{document.title} {document.text[:2000]}"),
    }


def _sort(items: list[dict]) -> list[dict]:
    return sorted(
        items,
        key=lambda item: (
            -item["score"],
            item["year"] or 0,
            item["doc_id"],
        ),
    )


def _evaluate_rankings(
    rankings: dict[str, list[dict]],
    queries: list[LiteratureQuery],
    top_k: int,
) -> dict:
    recalls = []
    reciprocal_ranks = []
    relevance_scores = []
    citation_valid = []
    future_leakage = 0
    for query in queries:
        ranking = rankings[query.query_id][:top_k]
        ranked_doc_ids = [item["doc_id"] for item in ranking]
        gold_positions = [
            ranked_doc_ids.index(gold) + 1
            for gold in query.gold_doc_ids
            if gold in ranked_doc_ids
        ]
        recalls.append(bool(gold_positions))
        reciprocal_ranks.append(1 / min(gold_positions) if gold_positions else 0.0)
        relevance_scores.append(
            sum(item["relevance"] for item in ranking) / len(ranking)
            if ranking
            else 0.0
        )
        citation_valid.extend(
            bool(item["title"] and item["source_path"] and item["year"])
            for item in ranking
        )
        future_leakage += sum(
            bool(item["year"] and item["year"] > query.as_of_year)
            for item in ranking
        )
    return {
        "recall@10": sum(recalls) / len(recalls) if recalls else 0.0,
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0.0,
        "literature_relevance@10": sum(relevance_scores) / len(relevance_scores)
        if relevance_scores
        else 0.0,
        "citation_validity_rate": sum(citation_valid) / len(citation_valid)
        if citation_valid
        else 0.0,
        "future_leakage_count": future_leakage,
    }


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _bm25_like_score(query: str, document: str) -> float:
    query_tokens = _tokens(query)
    document_tokens = _tokens(document)
    if not query_tokens or not document_tokens:
        return 0.0
    frequencies = Counter(document_tokens)
    length_norm = math.log(len(document_tokens) + 1)
    return sum(math.log(frequencies[token] + 1) for token in query_tokens) / length_norm


def _token_f1(left: str, right: str) -> float:
    left_tokens = Counter(_tokens(left))
    right_tokens = Counter(_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = sum((left_tokens & right_tokens).values())
    precision = overlap / sum(right_tokens.values())
    recall = overlap / sum(left_tokens.values())
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0
