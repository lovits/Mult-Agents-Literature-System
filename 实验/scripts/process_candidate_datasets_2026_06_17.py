import json
from pathlib import Path

from evireview.dao.candidate_datasets import (
    coerce_review_list,
    paper_from_neurips_record,
    peercheck_summary,
    read_jsonl,
    reviewrebuttal_summary,
)


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "dataset/raw"
OUTPUT_ROOT = ROOT / "dataset/processed/candidate_expansion_2026_06_17"


def run(sample_size: int = 50) -> dict:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    _write_processed_gitignore()

    neurips_result = process_neurips(sample_size=sample_size)
    reviewrebuttal_result = process_reviewrebuttal()
    peercheck_result = process_peercheck()
    openreview_result = inspect_openreview_raw_status()

    manifest = {
        "status": "processed",
        "sample_size": sample_size,
        "artifacts_are_local": True,
        "raw_data_committed": False,
        "token_persisted": False,
        "datasets": {
            "neurips_2023": neurips_result,
            "reviewrebuttal_test": reviewrebuttal_result,
            "peercheck": peercheck_result,
            "openreview_raw_hf_shard0": openreview_result,
        },
    }
    (OUTPUT_ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def process_neurips(sample_size: int) -> dict:
    raw_path = RAW_ROOT / "primary/neurips_2023_2025_2023_only/data/2023.jsonl"
    papers_path = OUTPUT_ROOT / "neurips_2023_sample_papers.jsonl"
    reviews_path = OUTPUT_ROOT / "neurips_2023_review_pool.jsonl"

    selected = []
    review_rows = []
    section_counts: dict[str, int] = {}
    evidence_type_counts: dict[str, int] = {}
    for row in read_jsonl(raw_path):
        reviews = coerce_review_list(row.get("reviews"))
        if not reviews or len(str(row.get("paper_text") or "")) < 1_000:
            continue
        paper = paper_from_neurips_record(row, max_blocks=120)
        selected.append(paper)
        for block in paper.blocks:
            section_counts[block.section] = section_counts.get(block.section, 0) + 1
            evidence_type_counts[block.evidence_type] = (
                evidence_type_counts.get(block.evidence_type, 0) + 1
            )
        for index, review in enumerate(reviews):
            review_rows.append(
                {
                    "paper_id": paper.paper_id,
                    "review_index": index,
                    "source": "NeurIPS 2023 OpenReview public review",
                    "text": review,
                }
            )
        if len(selected) >= sample_size:
            break

    with papers_path.open("w", encoding="utf-8") as handle:
        for paper in selected:
            handle.write(json.dumps(paper.model_dump(), ensure_ascii=False) + "\n")
    with reviews_path.open("w", encoding="utf-8") as handle:
        for review in review_rows:
            handle.write(json.dumps(review, ensure_ascii=False) + "\n")

    return {
        "papers": len(selected),
        "evidence_blocks": sum(len(paper.blocks) for paper in selected),
        "reviews": len(review_rows),
        "sections": dict(sorted(section_counts.items())),
        "evidence_types": dict(sorted(evidence_type_counts.items())),
        "artifacts": [
            str(papers_path.relative_to(ROOT)),
            str(reviews_path.relative_to(ROOT)),
        ],
        "role": "sampled primary paper/review pool for later E6 stability runs",
    }


def process_reviewrebuttal() -> dict:
    raw_path = RAW_ROOT / "evaluation/reviewrebuttal_test/REVIEWS_test.json"
    summary = reviewrebuttal_summary(raw_path)
    summary["artifact"] = str(
        (OUTPUT_ROOT / "reviewrebuttal_test_summary.json").relative_to(ROOT)
    )
    (OUTPUT_ROOT / "reviewrebuttal_test_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary | {
        "role": "full-stage review/metareview/decision diagnostic candidate"
    }


def process_peercheck() -> dict:
    raw_path = RAW_ROOT / "evaluation/peercheck/train.jsonl"
    summary = peercheck_summary(raw_path)
    summary["artifact"] = str((OUTPUT_ROOT / "peercheck_summary.json").relative_to(ROOT))
    (OUTPUT_ROOT / "peercheck_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary | {"role": "evidence-citation format diagnostic candidate"}


def inspect_openreview_raw_status() -> dict:
    parquet_path = (
        RAW_ROOT / "primary/openreview_raw_hf_shard0/data/train-00000-of-00006.parquet"
    )
    parquet_ready = _parquet_like(parquet_path)
    return {
        "downloaded": parquet_path.exists(),
        "parquet_like": parquet_ready,
        "size": parquet_path.stat().st_size if parquet_path.exists() else 0,
        "event_filter_status": "pending_parquet_reader",
        "pending_reason": (
            "Current committed dependencies intentionally avoid pyarrow/pandas; "
            "event filtering will be added after a parquet reader is approved or provided."
        ),
        "role": "primary OpenReview event pool candidate",
    }


def _parquet_like(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000:
        return False
    with path.open("rb") as handle:
        head = handle.read(4)
        handle.seek(-4, 2)
        tail = handle.read(4)
    return head == b"PAR1" and tail == b"PAR1"


def _write_processed_gitignore() -> None:
    (OUTPUT_ROOT / ".gitignore").write_text(
        "\n".join(
            [
                "# Generated from third-party raw datasets; keep local.",
                "*.jsonl",
                "manifest.json",
                "peercheck_summary.json",
                "reviewrebuttal_test_summary.json",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
