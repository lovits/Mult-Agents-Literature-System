from __future__ import annotations

import re
from collections import Counter
from typing import Any

from common import DATA_DIR, ensure_dirs, normalize_ws, read_jsonl, write_json, write_jsonl


RAW_DIR = DATA_DIR / "substanreview_raw"
LABEL_RE = re.compile(r"^(Eval|Jus)_(pos|neg)_(\d+)$")


def parse_label_key(label: str) -> tuple[str, str, str] | None:
    match = LABEL_RE.match(label)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def span_payload(review: str, start: int, end: int, label: str) -> dict[str, Any]:
    return {
        "span_start": start,
        "span_end": end,
        "span_label": label,
        "text": normalize_ws(review[start:end]),
    }


def process_record(record: dict[str, Any], split: str) -> list[dict[str, Any]]:
    review = record["review"]
    evidence_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    eval_spans: list[tuple[tuple[str, str], dict[str, Any]]] = []

    for start, end, label in record["label"]:
        parsed = parse_label_key(label)
        if parsed is None:
            continue
        role, polarity, index = parsed
        item = span_payload(review, int(start), int(end), label)
        key = (polarity, index)
        if role == "Jus":
            evidence_by_key.setdefault(key, []).append(item)
        elif role == "Eval":
            eval_spans.append((key, item))

    rows = []
    for local_index, (key, eval_item) in enumerate(eval_spans, start=1):
        evidence_items = evidence_by_key.get(key, [])
        substantiation_label = "Supported" if evidence_items else "Unsupported"
        rows.append(
            {
                "dataset": "SubstanReview",
                "split": split,
                "review_id": record["id"],
                "claim_id": f"{split}_{record['id']}_eval_{local_index:03d}",
                "polarity": key[0],
                "pair_index": key[1],
                "claim_label": eval_item["span_label"],
                "claim_start": eval_item["span_start"],
                "claim_end": eval_item["span_end"],
                "claim_text": eval_item["text"],
                "substantiation_label": substantiation_label,
                "evidence_count": len(evidence_items),
                "evidence_texts": [item["text"] for item in evidence_items],
                "evidence_spans": evidence_items,
                "review_text": review,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], review_count: int, split: str) -> dict[str, Any]:
    label_counts = Counter(row["substantiation_label"] for row in rows)
    polarity_counts = Counter(row["polarity"] for row in rows)
    evidence_counts = Counter(str(row["evidence_count"]) for row in rows)
    return {
        "split": split,
        "review_count": review_count,
        "claim_count": len(rows),
        "substantiation_label_counts": dict(label_counts),
        "polarity_counts": dict(polarity_counts),
        "evidence_count_distribution": dict(evidence_counts),
    }


def main() -> None:
    ensure_dirs()
    all_rows: list[dict[str, Any]] = []
    summaries = {}

    for split in ("train", "test"):
        raw_path = RAW_DIR / f"{split}.jsonl"
        if not raw_path.exists():
            raise SystemExit(f"{raw_path} missing; run fetch_substanreview.py first")
        records = read_jsonl(raw_path)
        rows = [row for record in records for row in process_record(record, split)]
        write_jsonl(DATA_DIR / f"substanreview_{split}_claims.jsonl", rows)
        summaries[split] = summarize(rows, len(records), split)
        all_rows.extend(rows)
        print(f"{split}: reviews={len(records)} claims={len(rows)} labels={summaries[split]['substantiation_label_counts']}")

    write_jsonl(DATA_DIR / "substanreview_claims_all.jsonl", all_rows)
    summary = {
        "dataset": "SubstanReview",
        "task": "Claim-level substantiation detection from human annotated Eval/Jus span pairs",
        "gold_definition": "Eval spans with a same-index Jus span are Supported; Eval spans without a paired Jus span are Unsupported.",
        "source_repository": "https://github.com/YanzhuGuo/SubstanReview",
        "paper": "https://aclanthology.org/2023.findings-emnlp.684/",
        "splits": summaries,
        "all": summarize(all_rows, summaries["train"]["review_count"] + summaries["test"]["review_count"], "all"),
    }
    write_json(DATA_DIR / "substanreview_summary.json", summary)
    print(f"all: claims={len(all_rows)} labels={summary['all']['substantiation_label_counts']}")


if __name__ == "__main__":
    main()
