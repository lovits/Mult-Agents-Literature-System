from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json


DEFAULT_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
CACHE_PATH = DATA_DIR / "claimcheck_openrouter_embedding_cache.json"


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def token_set_cosine(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / math.sqrt(len(left_tokens) * len(right_tokens))


def vector_cosine(left: list[float], right: list[float]) -> float:
    dot = sum(lv * rv for lv, rv in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def target_candidate_indices(row: dict[str, Any], threshold: float = 0.7) -> set[int]:
    indices = set()
    for target in row["target_claims"]:
        scored = [(token_set_cosine(target, claim), index) for index, claim in enumerate(row["candidate_claims"])]
        if not scored:
            continue
        score, index = max(scored)
        if score >= threshold:
            indices.add(index)
    return indices


def load_cache() -> dict[str, list[float]]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, list[float]]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache) + "\n", encoding="utf-8")


def openrouter_embeddings(texts: list[str], model: str, api_key: str, batch_size: int = 64) -> dict[str, list[float]]:
    cache = load_cache()
    missing = [text for text in dict.fromkeys(texts) if text not in cache]
    for start in range(0, len(missing), batch_size):
        batch = missing[start : start + batch_size]
        payload = json.dumps({"model": model, "input": batch}).encode("utf-8")
        request = urllib.request.Request(
            OPENROUTER_EMBEDDINGS_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/lovits/Agent-Literature-System",
                "X-Title": "EviReview-Lite",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        for text, item in zip(batch, data.get("data", [])):
            cache[text] = item["embedding"]
        save_cache(cache)
        time.sleep(0.2)
    return {text: cache[text] for text in texts}


def collect_texts(rows: list[dict[str, Any]]) -> list[str]:
    texts = []
    for row in rows:
        texts.append(row["weakness_text"])
        texts.extend(row["candidate_claims"])
    return list(dict.fromkeys(texts))


def evaluate(rows: list[dict[str, Any]], embeddings: dict[str, list[float]]) -> dict[str, Any]:
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
        weakness_embedding = embeddings[row["weakness_text"]]
        ranked = sorted(
            range(len(row["candidate_claims"])),
            key=lambda index: vector_cosine(weakness_embedding, embeddings[row["candidate_claims"][index]]),
            reverse=True,
        )
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


def blocked(reason: str, model: str) -> None:
    payload = {
        "status": "blocked",
        "dataset": "CLAIMCHECK",
        "task": "OpenRouter free embedding retrieval",
        "model": model,
        "reason": reason,
        "required_env": ["OPENROUTER_API_KEY"],
        "suggested_command": "OPENROUTER_API_KEY=... python3 code/experiments/evireview_a/src/evaluate_claimcheck_openrouter_embeddings.py",
    }
    write_json(DATA_DIR / "claimcheck_openrouter_embedding_metrics.json", payload)
    print(reason)


def main() -> None:
    ensure_dirs()
    model = os.getenv("OPENROUTER_EMBEDDING_MODEL", DEFAULT_MODEL)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        blocked("OPENROUTER_API_KEY is not set; cannot call OpenRouter embeddings.", model)
        return

    split_paths = {
        "pilot": DATA_DIR / "claimcheck_pilot_weaknesses.jsonl",
        "main": DATA_DIR / "claimcheck_main_weaknesses.jsonl",
    }
    if not all(path.exists() for path in split_paths.values()):
        raise SystemExit("CLAIMCHECK weakness files missing; run prepare_claimcheck.py first")

    splits = {split: read_jsonl(path) for split, path in split_paths.items()}
    texts = collect_texts([row for rows in splits.values() for row in rows])
    try:
        embeddings = openrouter_embeddings(texts, model, api_key)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        blocked(f"OpenRouter HTTP error {exc.code}: {body[:500]}", model)
        return

    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "OpenRouter free embedding retrieval",
        "model": model,
        "text_count": len(texts),
        "warning": "Raw CLAIMCHECK text, embeddings cache, and row-level rankings are not committed.",
        "splits": {split: evaluate(rows, embeddings) for split, rows in splits.items()},
    }
    write_json(DATA_DIR / "claimcheck_openrouter_embedding_metrics.json", payload)
    main = payload["splits"]["main"]
    print(f"main hit_at_3={main['hit_at_3']} hit_at_5={main['hit_at_5']} mrr={main['mrr']}")


if __name__ == "__main__":
    main()
