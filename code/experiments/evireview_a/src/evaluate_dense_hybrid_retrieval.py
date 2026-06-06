from __future__ import annotations

from collections import defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json
from evaluate_claimcheck_retrieval import (
    bm25_score,
    evaluate,
    prepare_row,
    rank_indices,
)
from evaluate_claimcheck_openrouter_embeddings import load_cache, vector_cosine


RRF_K = 60


def dense_score(row: dict[str, Any], claim: str) -> float:
    return row["_dense_scores"].get(claim, 0.0)


def attach_dense_and_rrf_scores(rows: list[dict[str, Any]], embeddings: dict[str, list[float]]) -> None:
    for row in rows:
        query = embeddings.get(row["weakness_text"])
        if query is None:
            raise SystemExit("embedding cache is incomplete for a weakness")
        row["_dense_scores"] = {}
        for claim in row["candidate_claims"]:
            vector = embeddings.get(claim)
            if vector is None:
                raise SystemExit("embedding cache is incomplete for a candidate claim")
            row["_dense_scores"][claim] = vector_cosine(query, vector)
        scores: dict[int, float] = defaultdict(float)
        for score_fn in (bm25_score, dense_score):
            for rank, index in enumerate(rank_indices(row, score_fn), start=1):
                scores[index] += 1.0 / (RRF_K + rank)
        row["_rrf_scores"] = {
            claim: scores[index]
            for index, claim in enumerate(row["candidate_claims"])
        }


def rrf_score(row: dict[str, Any], claim: str) -> float:
    return row["_rrf_scores"].get(claim, 0.0)


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# CLAIMCHECK Dense And Hybrid Retrieval",
        "",
        "Ready-label comparison on the same mapped CLAIMCHECK targets. Dense retrieval reuses the committed experiment's OpenRouter embedding cache; hybrid retrieval fuses BM25 and dense ranks with RRF.",
        "",
        "| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, splits in payload["methods"].items():
        metrics = splits["main"]
        lines.append(
            f"| {name} | {metrics['hit_at_1']:.4f} | {metrics['hit_at_3']:.4f} | "
            f"{metrics['hit_at_5']:.4f} | {metrics['mrr']:.4f} |"
        )
    lines.extend(
        [
            "",
            f"- Best main Hit@3: `{payload['best_main_hit_at_3']}`.",
            "- Metric boundary: gold mapped targets supplied by CLAIMCHECK; no manual labels were added.",
            "- Qdrant is an execution adapter for the same dense+sparse RRF contract, not a separate accuracy method in this local comparison.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    splits = {}
    for split in ("pilot", "main"):
        path = DATA_DIR / f"claimcheck_{split}_weaknesses.jsonl"
        if not path.exists():
            raise SystemExit(f"{path.name} missing; run prepare_claimcheck.py first")
        splits[split] = [prepare_row(row) for row in read_jsonl(path)]

    embeddings = load_cache()
    if not embeddings:
        raise SystemExit("claimcheck_openrouter_embedding_cache.json missing")
    for rows in splits.values():
        attach_dense_and_rrf_scores(rows, embeddings)

    methods = {
        "bm25_sparse": bm25_score,
        "openrouter_dense": dense_score,
        "bm25_openrouter_rrf_hybrid": rrf_score,
    }
    payload = {
        "dataset": "CLAIMCHECK",
        "task": "weakness-to-paper-claim retrieval",
        "metric_boundary": "gold",
        "dense_representation": "nvidia/llama-nemotron-embed-vl-1b-v2:free cached embeddings",
        "fusion": "reciprocal_rank_fusion",
        "rrf_k": RRF_K,
        "methods": {
            name: {split: evaluate(rows, score_fn) for split, rows in splits.items()}
            for name, score_fn in methods.items()
        },
    }
    main_scores = {name: metrics["main"]["hit_at_3"] for name, metrics in payload["methods"].items()}
    payload["best_main_hit_at_3"] = max(main_scores, key=main_scores.get)
    write_json(DATA_DIR / "dense_hybrid_retrieval_metrics.json", payload)
    (REPORT_DIR / "dense_hybrid_retrieval_report.md").write_text(render_report(payload), encoding="utf-8")
    print(" ".join(f"{name}={score:.4f}" for name, score in main_scores.items()))


if __name__ == "__main__":
    main()
