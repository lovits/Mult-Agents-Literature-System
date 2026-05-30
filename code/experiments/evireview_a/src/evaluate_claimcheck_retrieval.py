from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Callable

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency path
    np = None


ScoreFn = Callable[[dict[str, Any], str], float]


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def char_ngrams(text: str, n: int = 3) -> list[str]:
    normalized = re.sub(r"\s+", " ", (text or "").lower()).strip()
    if len(normalized) < n:
        return [normalized] if normalized else []
    return [normalized[index : index + n] for index in range(len(normalized) - n + 1)]


def set_cosine(left: str, right: str, analyzer: Callable[[str], list[str]] = tokenize) -> float:
    left_tokens = set(analyzer(left))
    right_tokens = set(analyzer(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / math.sqrt(len(left_tokens) * len(right_tokens))


def sparse_cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(term, 0.0) for term, value in left.items())
    if dot == 0:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def target_candidate_indices(row: dict[str, Any], threshold: float = 0.7) -> set[int]:
    indices = set()
    for target in row["target_claims"]:
        scored = [(set_cosine(target, claim), index) for index, claim in enumerate(row["candidate_claims"])]
        if not scored:
            continue
        score, index = max(scored)
        if score >= threshold:
            indices.add(index)
    return indices


def lexical_score(row: dict[str, Any], claim: str) -> float:
    return set_cosine(row["weakness_text"], claim)


def char_ngram_score(row: dict[str, Any], claim: str) -> float:
    return set_cosine(row["weakness_text"], claim, char_ngrams)


def tfidf_vector(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(text))
    if not counts:
        return {}
    max_tf = max(counts.values())
    return {term: (0.5 + 0.5 * count / max_tf) * idf.get(term, 0.0) for term, count in counts.items()}


def build_row_idf(row: dict[str, Any]) -> dict[str, float]:
    docs = [row["weakness_text"], *row["candidate_claims"]]
    df = Counter()
    for doc in docs:
        df.update(set(tokenize(doc)))
    n_docs = len(docs)
    return {term: math.log((n_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}


def tfidf_score(row: dict[str, Any], claim: str) -> float:
    idf = row["_idf"]
    query_vec = tfidf_vector(row["weakness_text"], idf)
    claim_vec = tfidf_vector(claim, idf)
    return sparse_cosine(query_vec, claim_vec)


def bm25_score(row: dict[str, Any], claim: str) -> float:
    docs = row["candidate_claims"]
    if not docs:
        return 0.0
    tokenized = row["_candidate_tokens"]
    doc_lens = [len(tokens) for tokens in tokenized]
    avgdl = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
    df = row["_df"]
    tf = Counter(tokenize(claim))
    doc_len = len(tokenize(claim))
    score = 0.0
    k1 = 1.5
    b = 0.75
    n_docs = len(docs)
    for term, qtf in Counter(tokenize(row["weakness_text"])).items():
        if term not in tf:
            continue
        idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
        denom = tf[term] + k1 * (1 - b + b * doc_len / avgdl)
        score += idf * (tf[term] * (k1 + 1) / denom) * qtf
    return score


def hybrid_score(row: dict[str, Any], claim: str) -> float:
    scores = row["_normalized_scores"][claim]
    return 0.25 * scores["lexical"] + 0.25 * scores["char_ngram"] + 0.25 * scores["tfidf"] + 0.25 * scores["bm25"]


def lsa_score(row: dict[str, Any], claim: str) -> float:
    return row.get("_lsa_scores", {}).get(claim, 0.0)


def prepare_row(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    row["_idf"] = build_row_idf(row)
    row["_candidate_tokens"] = [tokenize(claim) for claim in row["candidate_claims"]]
    df = Counter()
    for tokens in row["_candidate_tokens"]:
        df.update(set(tokens))
    row["_df"] = df

    raw_scores = {}
    for claim in row["candidate_claims"]:
        raw_scores[claim] = {
            "lexical": lexical_score(row, claim),
            "char_ngram": char_ngram_score(row, claim),
            "tfidf": tfidf_score(row, claim),
            "bm25": bm25_score(row, claim),
        }
    max_by_name = {
        name: max((scores[name] for scores in raw_scores.values()), default=0.0)
        for name in ("lexical", "char_ngram", "tfidf", "bm25")
    }
    row["_normalized_scores"] = {
        claim: {
            name: safe_div(value, max_by_name[name])
            for name, value in scores.items()
        }
        for claim, scores in raw_scores.items()
    }
    return row


def attach_lsa_scores(rows: list[dict[str, Any]], dims: int = 128, max_terms: int = 800) -> None:
    if np is None:
        return

    texts = []
    keys = []
    token_frequency = Counter()
    document_frequency = Counter()
    for row_index, row in enumerate(rows):
        indexed_texts = [("weakness", None, row["weakness_text"])]
        indexed_texts.extend(("claim", claim_index, claim) for claim_index, claim in enumerate(row["candidate_claims"]))
        for kind, claim_index, text in indexed_texts:
            texts.append(text)
            keys.append((kind, row_index, claim_index))
            tokens = tokenize(text)
            token_frequency.update(tokens)
            document_frequency.update(set(tokens))

    doc_count = len(texts)
    terms = [
        term
        for term, _ in token_frequency.most_common()
        if 2 <= document_frequency[term] <= 0.7 * doc_count
    ][:max_terms]
    if not terms:
        return

    vocabulary = {term: index for index, term in enumerate(terms)}
    matrix = np.zeros((doc_count, len(vocabulary)), dtype=np.float32)
    for row_index, text in enumerate(texts):
        counts = Counter(token for token in tokenize(text) if token in vocabulary)
        if not counts:
            continue
        max_tf = max(counts.values())
        for term, count in counts.items():
            idf = math.log((doc_count + 1) / (document_frequency[term] + 1)) + 1
            matrix[row_index, vocabulary[term]] = (0.5 + 0.5 * count / max_tf) * idf

    left, singular_values, _ = np.linalg.svd(matrix, full_matrices=False)
    dim_count = min(dims, left.shape[1])
    embeddings = left[:, :dim_count] * singular_values[:dim_count]
    index_by_key = {key: index for index, key in enumerate(keys)}

    for row_index, row in enumerate(rows):
        weakness_vec = embeddings[index_by_key[("weakness", row_index, None)]]
        weakness_norm = float(np.linalg.norm(weakness_vec))
        scores = {}
        for claim_index, claim in enumerate(row["candidate_claims"]):
            claim_vec = embeddings[index_by_key[("claim", row_index, claim_index)]]
            claim_norm = float(np.linalg.norm(claim_vec))
            scores[claim] = float(weakness_vec @ claim_vec / (weakness_norm * claim_norm)) if weakness_norm and claim_norm else 0.0
        row["_lsa_scores"] = scores


def rank_indices(row: dict[str, Any], score_fn: ScoreFn) -> list[int]:
    return sorted(
        range(len(row["candidate_claims"])),
        key=lambda index: score_fn(row, row["candidate_claims"][index]),
        reverse=True,
    )


def evaluate(rows: list[dict[str, Any]], score_fn: ScoreFn) -> dict[str, Any]:
    grounded = [row for row in rows if row["grounding_label"] == "Grounded"]
    mapped = []
    unmapped_count = 0
    for row in grounded:
        target_indices = target_candidate_indices(row)
        if target_indices:
            mapped.append((row, target_indices))
        else:
            unmapped_count += 1

    hit_counts = {1: 0, 3: 0, 5: 0, 10: 0}
    reciprocal_rank_total = 0.0
    for row, target_indices in mapped:
        ranked = rank_indices(row, score_fn)
        for k in hit_counts:
            if target_indices & set(ranked[:k]):
                hit_counts[k] += 1
        for rank, index in enumerate(ranked, start=1):
            if index in target_indices:
                reciprocal_rank_total += 1 / rank
                break

    total = len(mapped)
    return {
        "grounded_weakness_count": len(grounded),
        "mapped_target_count": total,
        "unmapped_target_count": unmapped_count,
        "target_mapping_threshold": 0.7,
        "hit_at_1": round(safe_div(hit_counts[1], total), 4),
        "hit_at_3": round(safe_div(hit_counts[3], total), 4),
        "hit_at_5": round(safe_div(hit_counts[5], total), 4),
        "hit_at_10": round(safe_div(hit_counts[10], total), 4),
        "mrr": round(safe_div(reciprocal_rank_total, total), 4),
    }


def main() -> None:
    ensure_dirs()
    pilot_path = DATA_DIR / "claimcheck_pilot_weaknesses.jsonl"
    main_path = DATA_DIR / "claimcheck_main_weaknesses.jsonl"
    if not pilot_path.exists() or not main_path.exists():
        raise SystemExit("CLAIMCHECK weakness files missing; run prepare_claimcheck.py first")

    splits = {
        "pilot": [prepare_row(row) for row in read_jsonl(pilot_path)],
        "main": [prepare_row(row) for row in read_jsonl(main_path)],
    }
    for rows in splits.values():
        attach_lsa_scores(rows)

    methods: dict[str, ScoreFn] = {
        "lexical_token_overlap": lexical_score,
        "char_trigram_overlap": char_ngram_score,
        "tfidf_cosine": tfidf_score,
        "bm25": bm25_score,
        "hybrid_equal_weight": hybrid_score,
    }
    skipped_methods = {}
    if np is None:
        skipped_methods["lsa_tfidf_svd_128"] = "numpy is not installed"
    else:
        methods["lsa_tfidf_svd_128"] = lsa_score

    payload = {
        "dataset": "CLAIMCHECK",
        "task": "weakness-to-paper-claim retrieval",
        "gold_definition": "Target claims are mapped back to extracted candidate claims by token cosine >= 0.7 before ranking evaluation.",
        "warning": "Raw CLAIMCHECK text and row-level rankings are not committed because no upstream repository LICENSE was detected.",
        "optional_dependency_note": "lsa_tfidf_svd_128 uses numpy when available and is skipped otherwise.",
        "skipped_methods": skipped_methods,
        "methods": {
            name: {split: evaluate(rows, method) for split, rows in splits.items()}
            for name, method in methods.items()
        },
    }
    main_scores = {
        name: metrics["main"]["hit_at_3"]
        for name, metrics in payload["methods"].items()
    }
    payload["best_main_hit_at_3"] = max(main_scores, key=main_scores.get)
    write_json(DATA_DIR / "claimcheck_retrieval_metrics.json", payload)
    print(
        "main Hit@3 "
        + " ".join(f"{name}={score}" for name, score in sorted(main_scores.items()))
        + f" best={payload['best_main_hit_at_3']}"
    )


if __name__ == "__main__":
    main()
