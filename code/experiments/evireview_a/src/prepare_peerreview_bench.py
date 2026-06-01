from __future__ import annotations

import os
import urllib.parse
import urllib.request
import json
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, normalize_ws, write_json, write_jsonl


DATASET_ID = "prometheus-eval/peerreview-bench"
CONFIG = "expert_annotation"
SPLIT = "eval"
OUT_FILE = "peerreview_bench_expert_annotations.jsonl"
SUMMARY_FILE = "peerreview_bench_summary.json"
DEFAULT_LIMIT = 300
PAGE_SIZE = 100


def fetch_rows(offset: int, length: int) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "dataset": DATASET_ID,
            "config": CONFIG,
            "split": SPLIT,
            "offset": offset,
            "length": length,
        }
    )
    with urllib.request.urlopen(f"https://datasets-server.huggingface.co/rows?{params}", timeout=60) as response:
        return json.load(response)


def clean_label(value: Any) -> str:
    if value is None:
        return "Unlabeled"
    text = normalize_ws(str(value))
    return text if text else "Unlabeled"


def normalize_row(item: dict[str, Any]) -> dict[str, Any]:
    row = item["row"]
    paper_content = normalize_ws(row.get("paper_content", ""))
    review_item = normalize_ws(row.get("review_item", ""))
    return {
        "dataset": DATASET_ID,
        "config": CONFIG,
        "split": SPLIT,
        "row_index": item["row_idx"],
        "paper_id": row["paper_id"],
        "paper_title": normalize_ws(row["paper_title"]),
        "paper_excerpt": paper_content[:1600],
        "annotator_source": row.get("annotator_source", ""),
        "reviewer_id": row.get("reviewer_id", ""),
        "reviewer_type": row.get("reviewer_type", ""),
        "review_item_number": row.get("review_item_number"),
        "review_item": review_item,
        "correctness_label": clean_label(row.get("correctness")),
        "significance_label": clean_label(row.get("significance")),
        "evidence_label": clean_label(row.get("evidence")),
        "annotator_comments": normalize_ws(row.get("annotator_comments", "")),
    }


def main() -> None:
    ensure_dirs()
    limit = int(os.getenv("PEERREVIEW_BENCH_LIMIT", str(DEFAULT_LIMIT)))
    rows = []
    offset = 0
    total_available = None
    while len(rows) < limit:
        payload = fetch_rows(offset, min(PAGE_SIZE, limit - len(rows)))
        total_available = payload.get("num_rows_total")
        batch = payload.get("rows") or []
        if not batch:
            break
        rows.extend(normalize_row(item) for item in batch)
        offset += len(batch)

    write_jsonl(DATA_DIR / OUT_FILE, rows)
    summary = {
        "status": "ready" if rows else "empty",
        "dataset_id": DATASET_ID,
        "config": CONFIG,
        "split": SPLIT,
        "source_url": f"https://huggingface.co/datasets/{DATASET_ID}",
        "license": "cc-by-4.0",
        "total_available_rows": total_available,
        "downloaded_rows": len(rows),
        "limit": limit,
        "label_counts": {
            "correctness": dict(Counter(row["correctness_label"] for row in rows)),
            "significance": dict(Counter(row["significance_label"] for row in rows)),
            "evidence": dict(Counter(row["evidence_label"] for row in rows)),
        },
        "note": "Stored rows drop full paper_content and keep a short paper excerpt to keep the repository lightweight.",
    }
    write_json(DATA_DIR / SUMMARY_FILE, summary)
    print(f"Wrote {DATA_DIR / OUT_FILE}")
    print(f"Wrote {DATA_DIR / SUMMARY_FILE}")
    print(f"peerreview_bench rows={len(rows)} total_available={total_available}")


if __name__ == "__main__":
    main()
