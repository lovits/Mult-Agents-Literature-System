from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "packages" / "evireview_core"))

from evireview_core.providers.minimax import DEFAULT_ENDPOINT, DEFAULT_MODEL, MiniMaxProvider, ProviderCallError

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, tokenize, write_json, write_jsonl
from run_glm_reviewer_experiment import (
    build_prompt,
    coverage_metrics,
    existing_generated_rows,
    retrieve_and_verify,
    select_papers,
)


GENERATOR = "minimax_structured_reviewer_v1"
OUTPUT_PREFIX = "minimax_reviewer"
DEFAULT_LIMIT = 5


def normalize_item(
    raw: dict[str, Any],
    paper: dict[str, str],
    index: int,
    model: str,
    provider_metadata: dict[str, Any],
) -> dict[str, Any]:
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
    return {
        "generated_weakness_id": f"{paper['paper_id']}_{GENERATOR}_{index:02d}",
        "paper_id": paper["paper_id"],
        "forum": paper["forum"],
        "paper_index": paper["paper_index"],
        "title": paper["title"],
        "decision": paper["decision"],
        "weakness_text": re.sub(r"\s+", " ", str(raw.get("weakness_text", "")).strip()),
        "category": category,
        "severity": severity,
        "confidence": round(confidence, 4),
        "reviewer_role": str(raw.get("reviewer_role", f"{category}_reviewer")).strip() or f"{category}_reviewer",
        "rationale": re.sub(r"\s+", " ", str(raw.get("rationale", "")).strip()),
        "generator": GENERATOR,
        "model": model,
        "provider_metadata": provider_metadata,
    }


def generate_paper_weaknesses(
    provider: MiniMaxProvider,
    paper: dict[str, str],
    blocks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = provider.generate_json(
        "You are a careful evidence-grounded scientific peer reviewer. Return valid JSON only.",
        build_prompt(paper, blocks),
        prompt_version=GENERATOR,
        schema_version="weaknesses_v1",
    )
    weaknesses = result.payload.get("weaknesses")
    if not isinstance(weaknesses, list):
        raise ValueError("MiniMax response JSON does not contain weaknesses list")
    rows = []
    for index, raw in enumerate(weaknesses[:3], start=1):
        if not isinstance(raw, dict):
            continue
        row = normalize_item(raw, paper, index, provider.model, result.metadata)
        if row["weakness_text"] and len(tokenize(row["weakness_text"])) >= 6:
            rows.append(row)
    if not rows:
        raise ValueError("MiniMax response contained no usable weakness rows")
    return rows


def render_report(summary: dict[str, Any], coverage: dict[str, Any], verifier_summary: dict[str, Any]) -> None:
    recall = next(
        (row["human_weakness_recall"] for row in coverage.get("coverage_by_threshold", []) if row["threshold"] == 0.18),
        0.0,
    )
    lines = [
        "# MiniMax M2.7 Structured Reviewer Diagnostic",
        "",
        "This is a provider and Agent-RAG handoff diagnostic on the local OpenReview/PRISM sample, not human-gold evaluation.",
        "",
        "## Result",
        "",
        f"- Status: `{summary['status']}`",
        f"- Model: `{summary['model']}`",
        f"- Selected papers: {summary['selected_paper_count']}",
        f"- Papers with generation: {summary['papers_with_generation']}",
        f"- Generated weaknesses: {summary['generated_weakness_count']}",
        f"- Failed papers: {len(summary['errors'])}",
        f"- Recall@0.18 coverage proxy: {recall}",
        f"- Mean silver support score: {verifier_summary.get('mean_support_score', 0.0)}",
        f"- Silver verifier labels: {verifier_summary.get('label_counts', {})}",
        "",
        "## Boundary",
        "",
        "- The API key was read from `MINIMAX_API_KEY` and was not persisted.",
        "- Generated weaknesses are silver diagnostic outputs.",
        "- Retrieval and verifier metrics are diagnostic proxies and are not final thesis gold metrics.",
    ]
    (REPORT_DIR / f"{OUTPUT_PREFIX}_experiment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    limit = int(os.getenv("MINIMAX_PAPER_LIMIT", str(DEFAULT_LIMIT)))
    provider = MiniMaxProvider(
        endpoint=os.getenv("MINIMAX_ENDPOINT", DEFAULT_ENDPOINT),
        model=os.getenv("MINIMAX_MODEL", DEFAULT_MODEL),
        max_attempts=int(os.getenv("MINIMAX_MAX_ATTEMPTS", "3")),
    )
    selected = select_papers(limit)
    existing = existing_generated_rows(OUTPUT_PREFIX)
    existing_papers = {row["paper_id"] for row in existing}
    generated = list(existing)
    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)
    errors = []
    started = time.time()
    for paper in selected:
        if paper["paper_id"] in existing_papers:
            continue
        try:
            generated.extend(generate_paper_weaknesses(provider, paper, blocks_by_paper[paper["paper_id"]]))
        except (ProviderCallError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append({"paper_id": paper["paper_id"], "error_type": type(exc).__name__})

    summary = {
        "status": "ok" if generated else "blocked",
        "generator": GENERATOR,
        "model": provider.model,
        "endpoint": provider.endpoint,
        "selected_paper_count": len(selected),
        "generated_weakness_count": len(generated),
        "papers_with_generation": len({row["paper_id"] for row in generated}),
        "existing_papers_preserved": len(existing_papers),
        "category_counts": dict(Counter(row["category"] for row in generated)),
        "severity_counts": dict(Counter(row["severity"] for row in generated)),
        "elapsed_seconds": round(time.time() - started, 2),
        "errors": errors,
        "warning": "MiniMax M2.7 provider diagnostic; key is environment-only and metrics are silver diagnostics.",
    }
    write_jsonl(DATA_DIR / f"{OUTPUT_PREFIX}_weaknesses.jsonl", generated)
    write_json(DATA_DIR / f"{OUTPUT_PREFIX}_weaknesses_summary.json", summary)
    coverage = coverage_metrics(generated, read_jsonl(DATA_DIR / "human_weaknesses.jsonl")) if generated else {"coverage_by_threshold": []}
    write_json(DATA_DIR / f"{OUTPUT_PREFIX}_coverage_metrics.json", coverage)
    retrieved, verified, verifier_summary = retrieve_and_verify(generated, blocks_by_paper) if generated else ([], [], {})
    write_jsonl(DATA_DIR / f"{OUTPUT_PREFIX}_retrieval_top5.jsonl", retrieved)
    write_jsonl(DATA_DIR / f"{OUTPUT_PREFIX}_verified_weaknesses.jsonl", verified)
    write_json(DATA_DIR / f"{OUTPUT_PREFIX}_verifier_summary.json", verifier_summary)
    render_report(summary, coverage, verifier_summary)
    print(f"minimax_reviewer status={summary['status']} generated={len(generated)} errors={len(errors)}")


if __name__ == "__main__":
    main()
