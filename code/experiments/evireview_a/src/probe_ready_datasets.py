from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, write_json


CANDIDATES = [
    {
        "dataset_id": "prometheus-eval/peerreview-bench",
        "name": "PeerReview Bench",
        "config": "expert_annotation",
        "split": "eval",
        "best_use": "verifier/ranker/review-quality labels: correctness, significance, evidence",
        "decision": "A-tier add now",
    },
    {
        "dataset_id": "UKPLab/PeerQA-XT",
        "name": "PeerQA-XT",
        "config": "default",
        "split": "test",
        "best_use": "Paper-RAG retrieval QA over full scientific papers with peer-review-derived questions",
        "decision": "A-tier add next",
    },
    {
        "dataset_id": "Reviewerly/RottenReviews",
        "name": "RottenReviews",
        "config": "human_annotated_data",
        "split": "data",
        "best_use": "review quality dimensions and human quality annotations",
        "decision": "B-tier quality/ranker supplement",
    },
    {
        "dataset_id": "Samarth0710/reviewbench",
        "name": "ReviewBench",
        "config": "default",
        "split": "iclr",
        "best_use": "multi-conference OpenReview papers, reviews, rebuttals, decisions, markdown",
        "decision": "B-tier scaling/generalization",
    },
    {
        "dataset_id": "anoyresearcher/prism_paper_data",
        "name": "PRISM paper data",
        "config": None,
        "split": None,
        "best_use": "large OpenReview-derived paper/review corpus and PRISM-style review-quality framing",
        "decision": "B-tier with license caution",
    },
    {
        "dataset_id": "ut-amrl/SPECS-Review-Benchmark",
        "name": "SPECS Review Benchmark",
        "config": None,
        "split": None,
        "best_use": "controlled injected-flaw detection for reviewer robustness",
        "decision": "B-tier robustness experiment",
    },
    {
        "dataset_id": "TrustAIRLab/PeerCheck",
        "name": "PeerCheck",
        "config": None,
        "split": None,
        "best_use": "human vs LLM review quality and alignment",
        "decision": "B-tier reviewer generation comparison",
    },
    {
        "dataset_id": "priorcomputers/openreview_raw",
        "name": "OpenReview Raw",
        "config": "default",
        "split": "train",
        "best_use": "large-scale OpenReview review mining and auxiliary classification",
        "decision": "C-tier scaling only; very large",
    },
]


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def dataset_meta(dataset_id: str) -> dict[str, Any]:
    return fetch_json(f"https://huggingface.co/api/datasets/{dataset_id}")


def sample_rows(dataset_id: str, config: str, split: str, length: int = 1) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "dataset": dataset_id,
            "config": config,
            "split": split,
            "offset": 0,
            "length": length,
        }
    )
    return fetch_json(f"https://datasets-server.huggingface.co/rows?{params}")


def short_schema(rows_payload: dict[str, Any]) -> dict[str, Any]:
    rows = rows_payload.get("rows") or []
    if not rows:
        return {"num_rows_total": rows_payload.get("num_rows_total"), "columns": [], "sample": {}}
    row = rows[0].get("row", {})
    sample = {}
    for key, value in row.items():
        text = str(value).replace("\n", " ")
        sample[key] = text[:220]
    return {
        "num_rows_total": rows_payload.get("num_rows_total"),
        "columns": list(row.keys()),
        "sample": sample,
    }


def main() -> None:
    ensure_dirs()
    results = []
    for candidate in CANDIDATES:
        dataset_id = candidate["dataset_id"]
        row = dict(candidate)
        try:
            meta = dataset_meta(dataset_id)
            card = meta.get("cardData") or {}
            row.update(
                {
                    "status": "reachable",
                    "private": meta.get("private"),
                    "gated": meta.get("gated"),
                    "downloads": meta.get("downloads"),
                    "likes": meta.get("likes"),
                    "license": card.get("license") or card.get("license_name"),
                    "task_categories": card.get("task_categories"),
                    "language": card.get("language"),
                    "files": [item.get("rfilename") for item in (meta.get("siblings") or [])[:12]],
                }
            )
            if candidate.get("config") and candidate.get("split"):
                row["row_probe"] = short_schema(sample_rows(dataset_id, candidate["config"], candidate["split"]))
        except Exception as exc:
            row.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
        results.append(row)

    payload = {
        "status": "ok",
        "selection_rule": "Datasets must already contain labels or structured supervision usable for EviReview-Lite experiments without new manual annotation.",
        "candidates": results,
    }
    write_json(DATA_DIR / "ready_dataset_candidates.json", payload)

    lines = [
        "# Ready-to-use Dataset Candidates",
        "",
        "This report lists external datasets that can support the thesis experiments without creating new manual labels first.",
        "",
        "| Dataset | License | Rows / Probe | Best use | Decision |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in results:
        row_probe = item.get("row_probe") or {}
        rows = row_probe.get("num_rows_total", "-")
        lines.append(
            f"| [{item['name']}](https://huggingface.co/datasets/{item['dataset_id']}) | "
            f"{item.get('license', '-')} | {rows} | {item['best_use']} | {item['decision']} |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "1. Add PeerReview Bench first because it directly labels review items for correctness, significance, and evidence.",
            "2. Add PeerQA-XT next for Paper-RAG retrieval QA over full scientific papers.",
            "3. Use RottenReviews and ReviewBench as B-version quality/generalization datasets.",
            "4. Keep PRISM/OpenReview Raw as scaling corpora with license and size safeguards.",
        ]
    )
    (REPORT_DIR / "ready_dataset_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {DATA_DIR / 'ready_dataset_candidates.json'}")
    print(f"Wrote {REPORT_DIR / 'ready_dataset_candidates.md'}")


if __name__ == "__main__":
    main()
