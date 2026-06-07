from __future__ import annotations

import math
import os
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, tokenize, write_json
from evaluate_claimcheck_openrouter_embeddings import load_cache
from evaluate_claimcheck_retrieval import prepare_row, safe_div, target_candidate_indices


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "packages" / "evireview_core"))

from evireview_core.retrieval.qdrant import QdrantQueryClient  # noqa: E402


COLLECTION = "claimcheck_live_retrieval"
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
UPSERT_BATCH_SIZE = 64


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def sparse_vectors(row: dict[str, Any], vocabulary: dict[str, int]) -> tuple[list[dict[int, float]], dict[int, float]]:
    tokenized = row["_candidate_tokens"]
    doc_lens = [len(tokens) for tokens in tokenized]
    avgdl = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
    n_docs = len(tokenized)
    k1 = 1.5
    b = 0.75
    docs = []
    for tokens in tokenized:
        vector = {}
        term_counts = Counter(tokens)
        for term, tf in term_counts.items():
            df = row["_df"][term]
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            denom = tf + k1 * (1 - b + b * len(tokens) / avgdl)
            vector[vocabulary[term]] = idf * tf * (k1 + 1) / denom
        docs.append(vector)
    query = {
        vocabulary[term]: float(qtf)
        for term, qtf in Counter(tokenize(row["weakness_text"])).items()
        if term in vocabulary
    }
    return docs, query


def qdrant_sparse(vector: dict[int, float]) -> dict[str, list[float] | list[int]]:
    items = sorted((index, value) for index, value in vector.items() if value)
    return {
        "indices": [index for index, _ in items],
        "values": [value for _, value in items],
    }


def build_points(
    splits: dict[str, list[dict[str, Any]]],
    embeddings: dict[str, list[float]],
    vocabulary: dict[str, int],
) -> list[dict[str, Any]]:
    points = []
    point_id = 1
    for split, rows in splits.items():
        for row_index, row in enumerate(rows):
            doc_vectors, query_vector = sparse_vectors(row, vocabulary)
            row["_sparse_query"] = query_vector
            row["_row_key"] = f"{split}:{row_index}"
            for claim_index, (claim, sparse) in enumerate(zip(row["candidate_claims"], doc_vectors)):
                points.append(
                    {
                        "id": point_id,
                        "vector": {
                            "dense": embeddings[claim],
                            "sparse": qdrant_sparse(sparse),
                        },
                        "payload": {
                            "row_key": row["_row_key"],
                            "claim_index": claim_index,
                        },
                    }
                )
                point_id += 1
    return points


def evaluate_method(
    rows: list[dict[str, Any]],
    query: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> dict[str, Any]:
    grounded = [row for row in rows if row["grounding_label"] == "Grounded"]
    mapped = []
    for row in grounded:
        targets = target_candidate_indices(row)
        if targets:
            mapped.append((row, targets))

    hit_counts = {1: 0, 3: 0, 5: 0, 10: 0}
    reciprocal_rank_total = 0.0
    latencies = []
    for row, targets in mapped:
        started = time.perf_counter()
        points = query(row)
        latencies.append((time.perf_counter() - started) * 1000)
        ranked = [
            int(point["payload"]["claim_index"])
            for point in sorted(
                points,
                key=lambda point: (-float(point["score"]), int(point["payload"]["claim_index"])),
            )
        ]
        for k in hit_counts:
            if targets & set(ranked[:k]):
                hit_counts[k] += 1
        for rank, index in enumerate(ranked, start=1):
            if index in targets:
                reciprocal_rank_total += 1 / rank
                break

    total = len(mapped)
    return {
        "grounded_weakness_count": len(grounded),
        "mapped_target_count": total,
        "unmapped_target_count": len(grounded) - total,
        "hit_at_1": round(safe_div(hit_counts[1], total), 4),
        "hit_at_3": round(safe_div(hit_counts[3], total), 4),
        "hit_at_5": round(safe_div(hit_counts[5], total), 4),
        "hit_at_10": round(safe_div(hit_counts[10], total), 4),
        "mrr": round(safe_div(reciprocal_rank_total, total), 4),
        "latency_ms_mean": round(statistics.fmean(latencies), 3) if latencies else 0.0,
        "latency_ms_p50": round(percentile(latencies, 0.50), 3),
        "latency_ms_p95": round(percentile(latencies, 0.95), 3),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Live Qdrant CLAIMCHECK Retrieval",
        "",
        "Real Qdrant indexing and Query API evaluation on the same ready-label CLAIMCHECK mapped targets.",
        "",
        "| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR | Mean ms | P95 ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, splits in payload["methods"].items():
        metrics = splits["main"]
        lines.append(
            f"| {name} | {metrics['hit_at_1']:.4f} | {metrics['hit_at_3']:.4f} | "
            f"{metrics['hit_at_5']:.4f} | {metrics['mrr']:.4f} | "
            f"{metrics['latency_ms_mean']:.3f} | {metrics['latency_ms_p95']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"- Indexed points: `{payload['index']['point_count']}` in `{payload['index']['elapsed_seconds']:.3f}` seconds.",
            f"- Best main Hit@3: `{payload['best_main_hit_at_3']}`.",
            "- Dense representation: cached OpenRouter embeddings, so this isolates live Qdrant execution from local model changes.",
            "- Sparse representation reproduces the existing per-row BM25 scoring as sparse dot products.",
            "- Queries return the complete filtered candidate set and break equal scores by claim index for reproducible metrics.",
            "- No manual labels or row-level raw CLAIMCHECK outputs were added.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    split_paths = {
        "pilot": DATA_DIR / "claimcheck_pilot_weaknesses.jsonl",
        "main": DATA_DIR / "claimcheck_main_weaknesses.jsonl",
    }
    splits = {
        split: [prepare_row(row) for row in read_jsonl(path)]
        for split, path in split_paths.items()
    }
    embeddings = load_cache()
    if not embeddings:
        raise SystemExit("claimcheck_openrouter_embedding_cache.json missing")
    terms = sorted(
        {
            token
            for rows in splits.values()
            for row in rows
            for text in [row["weakness_text"], *row["candidate_claims"]]
            for token in tokenize(text)
        }
    )
    vocabulary = {term: index for index, term in enumerate(terms)}
    points = build_points(splits, embeddings, vocabulary)

    client = QdrantQueryClient(QDRANT_URL)
    server_info = client.server_info()
    started = time.perf_counter()
    client.recreate_collection(COLLECTION, dense_size=len(next(iter(embeddings.values()))))
    client.create_keyword_index(COLLECTION, "row_key")
    for start in range(0, len(points), UPSERT_BATCH_SIZE):
        client.upsert_points(COLLECTION, points[start : start + UPSERT_BATCH_SIZE])
    index_elapsed = time.perf_counter() - started

    methods = {
        "qdrant_bm25_sparse": lambda row: client.sparse_query(
            COLLECTION, row["_sparse_query"], len(row["candidate_claims"]), {"row_key": row["_row_key"]}
        ),
        "qdrant_openrouter_dense": lambda row: client.dense_query(
            COLLECTION,
            embeddings[row["weakness_text"]],
            len(row["candidate_claims"]),
            {"row_key": row["_row_key"]},
        ),
        "qdrant_bm25_openrouter_rrf_hybrid": lambda row: client.hybrid_query(
            COLLECTION,
            embeddings[row["weakness_text"]],
            row["_sparse_query"],
            len(row["candidate_claims"]),
            filters={"row_key": row["_row_key"]},
        ),
    }
    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "live Qdrant weakness-to-paper-claim retrieval",
        "metric_boundary": "gold mapped targets",
        "qdrant_url": QDRANT_URL,
        "qdrant_version": server_info.get("version", "unknown"),
        "collection": COLLECTION,
        "dense_representation": "nvidia/llama-nemotron-embed-vl-1b-v2:free cached embeddings",
        "sparse_representation": "per-row BM25 sparse dot product",
        "index": {
            "point_count": len(points),
            "vocabulary_size": len(vocabulary),
            "elapsed_seconds": round(index_elapsed, 3),
        },
        "methods": {
            name: {split: evaluate_method(rows, query) for split, rows in splits.items()}
            for name, query in methods.items()
        },
    }
    main_scores = {name: splits["main"]["hit_at_3"] for name, splits in payload["methods"].items()}
    payload["best_main_hit_at_3"] = max(main_scores, key=main_scores.get)
    write_json(DATA_DIR / "live_qdrant_retrieval_metrics.json", payload)
    (REPORT_DIR / "live_qdrant_retrieval_report.md").write_text(render_report(payload), encoding="utf-8")
    print(" ".join(f"{name}={score:.4f}" for name, score in main_scores.items()))


if __name__ == "__main__":
    main()
