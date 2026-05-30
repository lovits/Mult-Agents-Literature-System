from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from hashlib import sha256
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json


DEFAULT_MODEL = "qwen/qwen3-next-80b-a3b-instruct:free"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
EMBEDDING_CACHE_PATH = DATA_DIR / "claimcheck_openrouter_embedding_cache.json"
RERANK_CACHE_PATH = DATA_DIR / "claimcheck_openrouter_rerank_cache.json"


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


def load_json(path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def embedding_rank(row: dict[str, Any], embeddings: dict[str, list[float]]) -> list[int]:
    weakness_embedding = embeddings[row["weakness_text"]]
    return sorted(
        range(len(row["candidate_claims"])),
        key=lambda index: vector_cosine(weakness_embedding, embeddings[row["candidate_claims"][index]]),
        reverse=True,
    )


def prompt_for(row: dict[str, Any], ranked_indices: list[int], top_n: int) -> tuple[str, list[int]]:
    selected_indices = ranked_indices[:top_n]
    candidates = "\n".join(
        f"{display_index}. {row['candidate_claims'][claim_index]}"
        for display_index, claim_index in enumerate(selected_indices, start=1)
    )
    prompt = (
        "You are reranking source-paper claims for a scientific peer-review weakness.\n"
        "Pick the claims that most directly support or ground the weakness.\n"
        "Return JSON only, with this exact shape: {\"ranking\": [1, 2, 3, 4, 5]}.\n"
        "Use candidate numbers from the list. Put the best candidate first. Do not explain.\n\n"
        f"Weakness:\n{row['weakness_text']}\n\n"
        f"Candidate paper claims:\n{candidates}\n"
    )
    return prompt, selected_indices


def parse_ranking(text: str, top_n: int) -> list[int]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return []
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
    ranking = payload.get("ranking", [])
    parsed = []
    for item in ranking:
        try:
            value = int(item)
        except (TypeError, ValueError):
            continue
        if 1 <= value <= top_n and value not in parsed:
            parsed.append(value)
    return parsed


def retry_after_seconds(exc: urllib.error.HTTPError) -> float:
    header = exc.headers.get("Retry-After")
    if header:
        try:
            return float(header)
        except ValueError:
            pass
    try:
        body = exc.read().decode("utf-8", errors="replace")
        payload = json.loads(body)
        metadata = payload.get("error", {}).get("metadata", {})
        return float(metadata.get("retry_after_seconds") or metadata.get("retry_after_seconds_raw") or 15)
    except Exception:
        return 15.0


def summarize_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
        payload = json.loads(body)
        error = payload.get("error", {})
        metadata = error.get("metadata", {})
        retry_after = metadata.get("retry_after_seconds") or metadata.get("retry_after_seconds_raw")
        provider = metadata.get("provider_name")
        parts = [f"OpenRouter HTTP error {exc.code}: {error.get('message', 'request failed')}"]
        if provider:
            parts.append(f"provider={provider}")
        if retry_after:
            parts.append(f"retry_after_seconds={retry_after}")
        return "; ".join(parts)
    except Exception:
        return f"OpenRouter HTTP error {exc.code}"


def call_openrouter_chat(prompt: str, model: str, api_key: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a precise JSON-only reranker."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": 80,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        CHAT_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/lovits/Agent-Literature-System",
            "X-Title": "EviReview-Lite",
        },
        method="POST",
    )
    max_retries = int(os.getenv("OPENROUTER_RERANK_RETRIES", "8"))
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.load(response)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= max_retries:
                raise
            wait_seconds = min(max(retry_after_seconds(exc), 5.0), 60.0)
            time.sleep(wait_seconds)
    raise RuntimeError("unreachable OpenRouter retry state")


def rerank(row: dict[str, Any], ranked_indices: list[int], model: str, api_key: str, top_n: int) -> tuple[list[int], bool]:
    prompt, selected_indices = prompt_for(row, ranked_indices, top_n)
    cache = load_json(RERANK_CACHE_PATH)
    cache_key = sha256(f"{model}\n{prompt}".encode("utf-8")).hexdigest()
    if cache_key not in cache:
        content = call_openrouter_chat(prompt, model, api_key)
        cache[cache_key] = {"content": content}
        save_json(RERANK_CACHE_PATH, cache)
        time.sleep(0.5)
    parsed = parse_ranking(cache[cache_key]["content"], top_n)
    if not parsed:
        return ranked_indices, True

    reranked = []
    for display_index in parsed:
        claim_index = selected_indices[display_index - 1]
        if claim_index not in reranked:
            reranked.append(claim_index)
    for claim_index in ranked_indices:
        if claim_index not in reranked:
            reranked.append(claim_index)
    return reranked, False


def evaluate(rows: list[dict[str, Any]], embeddings: dict[str, list[float]], model: str, api_key: str, top_n: int) -> dict[str, Any]:
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
    fallback_count = 0
    for row, target_indices in mapped:
        base_ranked = embedding_rank(row, embeddings)
        ranked, used_fallback = rerank(row, base_ranked, model, api_key, top_n)
        fallback_count += int(used_fallback)
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
        "rerank_input_top_n": top_n,
        "fallback_count": fallback_count,
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
        "task": "OpenRouter free chat reranking over embedding candidates",
        "model": model,
        "reason": reason,
        "required_env": ["OPENROUTER_API_KEY"],
        "suggested_command": "OPENROUTER_API_KEY=... python3 code/experiments/evireview_a/src/evaluate_claimcheck_openrouter_reranker.py",
    }
    write_json(DATA_DIR / "claimcheck_openrouter_rerank_metrics.json", payload)
    print(reason)


def main() -> None:
    ensure_dirs()
    model = os.getenv("OPENROUTER_CHAT_MODEL", DEFAULT_MODEL)
    top_n = int(os.getenv("OPENROUTER_RERANK_TOP_N", "10"))
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        blocked("OPENROUTER_API_KEY is not set; cannot call OpenRouter chat completions.", model)
        return
    if not EMBEDDING_CACHE_PATH.exists():
        blocked("OpenRouter embedding cache missing; run evaluate_claimcheck_openrouter_embeddings.py first.", model)
        return

    split_paths = {
        "pilot": DATA_DIR / "claimcheck_pilot_weaknesses.jsonl",
        "main": DATA_DIR / "claimcheck_main_weaknesses.jsonl",
    }
    if not all(path.exists() for path in split_paths.values()):
        raise SystemExit("CLAIMCHECK weakness files missing; run prepare_claimcheck.py first")

    embeddings = load_json(EMBEDDING_CACHE_PATH)
    splits = {split: read_jsonl(path) for split, path in split_paths.items()}
    try:
        split_metrics = {split: evaluate(rows, embeddings, model, api_key, top_n) for split, rows in splits.items()}
    except urllib.error.HTTPError as exc:
        blocked(summarize_http_error(exc), model)
        return

    payload = {
        "status": "ok",
        "dataset": "CLAIMCHECK",
        "task": "OpenRouter free chat reranking over embedding candidates",
        "model": model,
        "base_retriever": "OpenRouter free embeddings: nvidia/llama-nemotron-embed-vl-1b-v2:free",
        "warning": "Raw CLAIMCHECK text, prompt/response cache, and row-level rankings are not committed.",
        "splits": split_metrics,
    }
    write_json(DATA_DIR / "claimcheck_openrouter_rerank_metrics.json", payload)
    main = payload["splits"]["main"]
    print(f"main hit_at_3={main['hit_at_3']} hit_at_5={main['hit_at_5']} mrr={main['mrr']} fallback={main['fallback_count']}")


if __name__ == "__main__":
    main()
