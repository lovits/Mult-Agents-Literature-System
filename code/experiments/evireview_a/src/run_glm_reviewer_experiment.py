from __future__ import annotations

import csv
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from typing import Any

from bootstrap_silver_labels import silver_label
from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, section_prior, tokenize, write_json, write_jsonl
from evaluate_claimcheck_retrieval import char_ngrams, set_cosine


GENERATOR = "glm_structured_reviewer_v0"
DEFAULT_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4.6v"
DEFAULT_LIMIT = 10
DEFAULT_MAX_ATTEMPTS = 3
TOP_K = 5
API_KEY_ENV_NAMES = ("GLM_API_KEY", "ZHIPU_API_KEY", "ZHIPUAI_API_KEY", "BIGMODEL_API_KEY", "ZAI_API_KEY")


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def resolve_api_key() -> tuple[str | None, str | None]:
    for name in API_KEY_ENV_NAMES:
        value = os.getenv(name)
        if value:
            return value, name
    return None, None


def read_manifest() -> list[dict[str, str]]:
    with (DATA_DIR / "manifest_clean.csv").open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def select_papers(limit: int) -> list[dict[str, str]]:
    rows = read_manifest()
    accepts = [row for row in rows if row["decision"] == "Accept"]
    rejects = [row for row in rows if row["decision"] == "Reject"]
    selected = []
    for reject, accept in zip(rejects, accepts):
        selected.extend([reject, accept])
        if len(selected) >= limit:
            break
    return selected[:limit]


def existing_generated_rows(output_prefix: str) -> list[dict[str, Any]]:
    path = DATA_DIR / f"{output_prefix}_weaknesses.jsonl"
    if not path.exists():
        return []
    return read_jsonl(path)


def section_excerpt(blocks: list[dict[str, Any]], section_type: str, limit: int) -> str:
    selected = [block for block in blocks if block["section_type"] == section_type]
    selected.sort(key=lambda block: block["token_count"], reverse=True)
    return "\n".join(block["text"][:1200] for block in selected[:2])[:limit]


def build_prompt(paper: dict[str, str], blocks: list[dict[str, Any]]) -> str:
    return f"""You are an evidence-grounded ML paper reviewer.

Review the paper using only the supplied excerpts. Generate exactly 3 concrete weaknesses.

Return JSON only:
{{"weaknesses":[{{"weakness_text":"...","category":"experiment|method|related_work|reproducibility|clarity|validity|other","severity":"major|minor","confidence":0.0,"reviewer_role":"experiment_reviewer|method_reviewer|novelty_reviewer|reproducibility_reviewer|clarity_reviewer|validity_reviewer","rationale":"..."}}]}}

Rules:
- Prefer specific, evidence-checkable weaknesses.
- Do not mention missing information unless the excerpts support the concern.
- Avoid generic comments unless you identify the concrete issue.

Title: {paper["title"]}

Abstract:
{section_excerpt(blocks, "abstract", 1000)}

Introduction:
{section_excerpt(blocks, "introduction", 1500)}

Method:
{section_excerpt(blocks, "method", 2000)}

Experiments:
{section_excerpt(blocks, "experiment", 1700)}

Limitations:
{section_excerpt(blocks, "limitation", 800)}
"""


def call_glm(api_key: str, model: str, endpoint: str, prompt: str, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a careful evidence-grounded scientific peer reviewer. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1800,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw_body = response.read().decode("utf-8")
    if not raw_body.strip():
        raise ValueError("GLM API returned an empty response body")
    body = json.loads(raw_body)
    return body["choices"][0]["message"]["content"]


def json_span(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def normalize_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    # Some providers escape a JSON object as a JSON string even with json_object mode.
    if text.startswith('"') and text.endswith('"'):
        try:
            unescaped = json.loads(text)
            if isinstance(unescaped, str):
                text = unescaped.strip()
        except json.JSONDecodeError:
            pass
    return text


def parse_json(text: str) -> dict[str, Any]:
    text = normalize_json_text(text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        candidate = json_span(text)
        if not candidate:
            raise
        payload = json.loads(candidate)
    if isinstance(payload, list):
        payload = {"weaknesses": payload}
    if not isinstance(payload.get("weaknesses"), list):
        raise ValueError("GLM response JSON does not contain weaknesses list")
    return payload


def generate_paper_weaknesses(
    api_key: str,
    model: str,
    endpoint: str,
    paper: dict[str, str],
    blocks: list[dict[str, Any]],
    max_attempts: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors = []
    prompt = build_prompt(paper, blocks)
    for attempt in range(1, max_attempts + 1):
        try:
            content = call_glm(api_key, model, endpoint, prompt)
            payload = parse_json(content)
            rows = []
            for index, item in enumerate(payload["weaknesses"][:3], start=1):
                normalized = normalize_item(item, paper, index, model)
                if normalized["weakness_text"] and len(tokenize(normalized["weakness_text"])) >= 6:
                    rows.append(normalized)
            if rows:
                return rows, errors
            raise ValueError("GLM response contained no usable weakness_text rows")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError, KeyError) as exc:
            errors.append(
                {
                    "paper_id": paper["paper_id"],
                    "attempt": str(attempt),
                    "error": type(exc).__name__,
                    "message": str(exc)[:300],
                }
            )
            time.sleep(min(2 * attempt, 6))
    return [], errors


def normalize_item(raw: dict[str, Any], paper: dict[str, str], index: int, model: str) -> dict[str, Any]:
    category = str(raw.get("category", "other")).strip()
    if category not in {"experiment", "method", "related_work", "reproducibility", "clarity", "validity", "other"}:
        category = "other"
    severity = str(raw.get("severity", "minor")).strip().lower()
    if severity not in {"major", "minor"}:
        severity = "minor"
    try:
        confidence = max(0.0, min(float(raw.get("confidence", 0.5)), 1.0))
    except (TypeError, ValueError):
        confidence = 0.5
    weakness_text = re.sub(r"\s+", " ", str(raw.get("weakness_text", "")).strip())
    return {
        "generated_weakness_id": f"{paper['paper_id']}_{GENERATOR}_{index:02d}",
        "paper_id": paper["paper_id"],
        "forum": paper["forum"],
        "paper_index": paper["paper_index"],
        "title": paper["title"],
        "decision": paper["decision"],
        "weakness_text": weakness_text,
        "category": category,
        "severity": severity,
        "confidence": round(confidence, 4),
        "reviewer_role": str(raw.get("reviewer_role", f"{category}_reviewer")).strip() or f"{category}_reviewer",
        "rationale": re.sub(r"\s+", " ", str(raw.get("rationale", "")).strip()),
        "generator": GENERATOR,
        "model": model,
    }


def combined_similarity(left: str, right: str) -> float:
    return 0.55 * set_cosine(left, right) + 0.45 * set_cosine(left, right, char_ngrams)


def generic_flag(text: str) -> bool:
    lower = text.lower()
    generic = any(term in lower for term in ["unclear", "insufficient", "limited", "not enough", "weak"])
    specific = any(term in lower for term in ["baseline", "ablation", "dataset", "experiment", "method", "hyperparameter", "section", "table"])
    return generic and not specific


def coverage_metrics(generated: list[dict[str, Any]], human: list[dict[str, Any]]) -> dict[str, Any]:
    gen_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    human_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in generated:
        gen_by_paper[row["paper_id"]].append(row)
    for row in human:
        human_by_paper[row["paper_id"]].append(row)

    results = []
    for threshold in (0.12, 0.18, 0.24):
        total = 0
        covered = 0
        for paper_id, human_rows in human_by_paper.items():
            if paper_id not in gen_by_paper:
                continue
            for human_row in human_rows:
                total += 1
                best = max(
                    (combined_similarity(human_row["weakness_text"], gen_row["weakness_text"]) for gen_row in gen_by_paper[paper_id]),
                    default=0.0,
                )
                covered += int(best >= threshold)
        results.append(
            {
                "threshold": threshold,
                "evaluated_human_weakness_count": total,
                "covered_human_weakness_count": covered,
                "human_weakness_recall": round(safe_div(covered, total), 4),
            }
        )
    texts = [row["weakness_text"] for row in generated]
    return {
        "generic_rate": round(safe_div(sum(1 for text in texts if generic_flag(text)), len(texts)), 4),
        "coverage_by_threshold": results,
    }


def retrieve_and_verify(generated: list[dict[str, Any]], blocks_by_paper: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    retrieved_rows = []
    verified_rows = []
    for row in generated:
        scored = []
        for block in blocks_by_paper[row["paper_id"]]:
            lexical = set_cosine(row["weakness_text"], block["text"])
            char = set_cosine(row["weakness_text"], block["text"], char_ngrams)
            prior = section_prior(row["category"], block["section_type"])
            score = 0.45 * lexical + 0.35 * char + 0.20 * prior
            scored.append((score, lexical, char, prior, block))
        scored.sort(key=lambda item: item[0], reverse=True)
        retrieved = [
            {
                "rank": rank,
                "score": round(score, 6),
                "lexical_score": round(lexical, 6),
                "char_score": round(char, 6),
                "section_prior": prior,
                "block_id": block["block_id"],
                "section_path": block["section_path"],
                "section_type": block["section_type"],
                "text": block["text"][:900],
            }
            for rank, (score, lexical, char, prior, block) in enumerate(scored[:TOP_K], start=1)
        ]
        retrieved_row = {**row, "retriever": "glm_section_aware_lexical_v0", "retrieved": retrieved}
        retrieved_rows.append(retrieved_row)
        label, support_score, rationale = silver_label(
            {
                "weakness_text": row["weakness_text"],
                "category_rule": row["category"],
                "retrieved_evidence_top5": retrieved,
            }
        )
        verified_rows.append(
            {
                **row,
                "verifier_label": label,
                "support_score": support_score,
                "evidence_block_ids": [item["block_id"] for item in retrieved[:3]],
                "rank_score": round(row["confidence"] * (1.0 if row["severity"] == "major" else 0.65) * (0.5 + support_score), 6),
                "verifier_rationale": rationale,
            }
        )
    summary = {
        "retrieved_count": len(retrieved_rows),
        "verified_count": len(verified_rows),
        "label_counts": dict(Counter(row["verifier_label"] for row in verified_rows)),
        "mean_support_score": round(safe_div(sum(row["support_score"] for row in verified_rows), len(verified_rows)), 4),
    }
    return retrieved_rows, verified_rows, summary


def render_report(summary: dict[str, Any], coverage: dict[str, Any], verifier_summary: dict[str, Any]) -> None:
    lines = [
        "# GLM-4.6V Structured Reviewer Experiment",
        "",
        "This report validates a GLM-4.6V structured reviewer deployment on the local OpenReview/PRISM sample.",
        "",
        "## Setup",
        "",
        f"- Status: `{summary['status']}`",
        f"- Model: `{summary['model']}`",
        f"- Endpoint: `{summary['endpoint']}`",
        f"- Selected papers: {summary['selected_paper_count']}",
        f"- Generated weaknesses: {summary['generated_weakness_count']}",
        f"- Papers with generation: {summary['papers_with_generation']}",
        f"- Elapsed seconds: {summary['elapsed_seconds']}",
        f"- Warning: {summary['warning']}",
        "",
        "## Coverage Proxy",
        "",
        f"- Generic rate: {coverage.get('generic_rate', 0.0)}",
        "",
        "| Similarity threshold | Evaluated human weaknesses | Covered | Recall |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in coverage.get("coverage_by_threshold", []):
        lines.append(
            f"| {row['threshold']} | {row['evaluated_human_weakness_count']} | {row['covered_human_weakness_count']} | {row['human_weakness_recall']} |"
        )
    lines.extend(
        [
            "",
            "## Verifier Handoff",
            "",
            f"- Retrieved generated weaknesses: {verifier_summary.get('retrieved_count', 0)}",
            f"- Verified generated weaknesses: {verifier_summary.get('verified_count', 0)}",
            f"- Label counts: {verifier_summary.get('label_counts', {})}",
            f"- Mean support score: {verifier_summary.get('mean_support_score', 0.0)}",
            "",
            "## Interpretation",
            "",
            "- This is a small deployment validation, not a full-scale final reviewer result.",
            "- The result should be compared against the deterministic rubric-agent baseline before expanding to all 50 papers.",
            "- Generated weaknesses are immediately passed through local retrieval and silver verifier diagnostics so unsupported comments are visible.",
        ]
    )
    (REPORT_DIR / "glm_reviewer_experiment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    api_key, api_key_source = resolve_api_key()
    model = os.getenv("GLM_MODEL", DEFAULT_MODEL)
    endpoint = os.getenv("GLM_ENDPOINT", DEFAULT_ENDPOINT)
    limit = int(os.getenv("GLM_PAPER_LIMIT", str(DEFAULT_LIMIT)))
    max_attempts = int(os.getenv("GLM_MAX_ATTEMPTS", str(DEFAULT_MAX_ATTEMPTS)))
    output_prefix = "glm_reviewer"
    existing_generated = existing_generated_rows(output_prefix)
    if not api_key:
        previous_summary_path = DATA_DIR / f"{output_prefix}_weaknesses_summary.json"
        previous_summary = json.loads(previous_summary_path.read_text(encoding="utf-8")) if previous_summary_path.exists() else {}
        summary = {
            "status": previous_summary.get("status", "blocked"),
            "reason": f"None of {', '.join(API_KEY_ENV_NAMES)} is set.",
            "model": model,
            "endpoint": endpoint,
            "accepted_api_key_env_names": list(API_KEY_ENV_NAMES),
            "requested_paper_count": limit,
            "existing_generated_weakness_count": len(existing_generated),
            "existing_papers_with_generation": len({row["paper_id"] for row in existing_generated}),
            "warning": "GLM API key is missing; preserved existing generated rows and did not overwrite prior experiment outputs.",
        }
        print(summary["reason"])
        return

    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)
    selected = select_papers(limit)
    generated = list(existing_generated)
    errors = []
    existing_papers = {row["paper_id"] for row in existing_generated}
    started = time.time()
    for paper in selected:
        if paper["paper_id"] in existing_papers:
            continue
        paper_rows, paper_errors = generate_paper_weaknesses(
            api_key,
            model,
            endpoint,
            paper,
            blocks_by_paper[paper["paper_id"]],
            max_attempts,
        )
        generated.extend(paper_rows)
        if paper_errors and not paper_rows:
            errors.append(paper_errors[-1])

    status = "ok" if generated else "blocked"
    summary = {
        "status": status,
        "generator": GENERATOR,
        "model": model,
        "endpoint": endpoint,
        "api_key_source": api_key_source,
        "requested_paper_count": limit,
        "selected_paper_count": len(selected),
        "generated_weakness_count": len(generated),
        "papers_with_generation": len({row["paper_id"] for row in generated}),
        "new_papers_requested": len([paper for paper in selected if paper["paper_id"] not in existing_papers]),
        "existing_papers_preserved": len(existing_papers),
        "max_attempts_per_new_paper": max_attempts,
        "category_counts": dict(Counter(row["category"] for row in generated)),
        "severity_counts": dict(Counter(row["severity"] for row in generated)),
        "elapsed_seconds": round(time.time() - started, 2),
        "errors": errors,
        "warning": "Small GLM-4.6V reviewer diagnostic sample; API key is never written to disk.",
    }
    write_jsonl(DATA_DIR / f"{output_prefix}_weaknesses.jsonl", generated)
    write_json(DATA_DIR / f"{output_prefix}_weaknesses_summary.json", summary)
    coverage = coverage_metrics(generated, read_jsonl(DATA_DIR / "human_weaknesses.jsonl")) if generated else {"coverage_by_threshold": []}
    write_json(DATA_DIR / f"{output_prefix}_coverage_metrics.json", coverage)
    retrieved, verified, verifier_summary = retrieve_and_verify(generated, blocks_by_paper) if generated else ([], [], {})
    write_jsonl(DATA_DIR / f"{output_prefix}_retrieval_top5.jsonl", retrieved)
    write_jsonl(DATA_DIR / f"{output_prefix}_verified_weaknesses.jsonl", verified)
    write_json(DATA_DIR / f"{output_prefix}_verifier_summary.json", verifier_summary)
    render_report(summary, coverage, verifier_summary)
    print(f"glm_reviewer status={status} generated={len(generated)} errors={len(errors)}")


if __name__ == "__main__":
    main()
