from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from evireview_core.domain.models import EvidenceBlock
from evireview_core.parsing.markdown_sections import tokenize


@dataclass(frozen=True)
class RetrievedEvidence:
    block_id: str
    paper_id: str
    section_path: str
    section_type: str
    text: str
    rank: int
    score: float
    retriever: str


def bm25_scores(
    query_tokens: list[str],
    docs: list[EvidenceBlock],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[tuple[float, EvidenceBlock]]:
    if not docs:
        return []

    tokenized_docs = [tokenize(doc.text) for doc in docs]
    doc_lens = [len(tokens) for tokens in tokenized_docs]
    avgdl = sum(doc_lens) / len(doc_lens) if doc_lens else 0.0
    if avgdl == 0.0:
        return []

    df: Counter[str] = Counter()
    for tokens in tokenized_docs:
        df.update(set(tokens))

    q_counts = Counter(query_tokens)
    n_docs = len(docs)
    scored: list[tuple[float, EvidenceBlock]] = []
    for doc, tokens, doc_len in zip(docs, tokenized_docs, doc_lens):
        tf = Counter(tokens)
        score = 0.0
        for term, qtf in q_counts.items():
            if term not in tf:
                continue
            idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * (tf[term] * (k1 + 1) / denom) * qtf
        if score > 0:
            scored.append((round(score, 6), doc))
    return sorted(scored, key=lambda item: item[0], reverse=True)


def bm25_search(query: str, docs: list[EvidenceBlock], top_k: int = 5) -> list[RetrievedEvidence]:
    ranked = bm25_scores(tokenize(query), docs)[:top_k]
    return [
        RetrievedEvidence(
            block_id=doc.block_id,
            paper_id=doc.paper_id,
            section_path=doc.section_path,
            section_type=doc.section_type,
            text=doc.text,
            rank=rank,
            score=score,
            retriever="bm25",
        )
        for rank, (score, doc) in enumerate(ranked, start=1)
    ]
