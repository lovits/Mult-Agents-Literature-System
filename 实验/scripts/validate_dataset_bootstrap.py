import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "dataset/raw"


def jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def json_object_size(path: Path) -> int:
    return len(json.loads(path.read_text(encoding="utf-8")))


def jsonl_rows_with_fields(path: Path, required_fields: set[str]) -> int:
    count = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if not required_fields <= set(row):
                raise ValueError(f"{path} is missing required fields")
            count += 1
    return count


def valid_pdfs(path: Path) -> list[Path]:
    return [
        pdf
        for pdf in path.glob("*.pdf")
        if pdf.stat().st_size > 1_000 and pdf.read_bytes()[:5] == b"%PDF-"
    ]


def validate() -> dict:
    openreview_manifest = json.loads(
        (RAW_ROOT / "primary/openreview_iclr2025_seed/manifest.json").read_text(encoding="utf-8")
    )
    arxiv_snapshot_root = RAW_ROOT / "demo/arxiv_unseen_2026-06-17"
    arxiv_manifest = json.loads((arxiv_snapshot_root / "manifest.json").read_text(encoding="utf-8"))
    literature_files = [
        path
        for path in (RAW_ROOT / "literature/local_corpus/source").rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".pdf"}
    ]
    peerqa_root = RAW_ROOT / "evaluation/peerqa"
    claimcheck_root = RAW_ROOT / "evaluation/claimcheck/texts"
    reviewcritique_root = RAW_ROOT / "evaluation/reviewcritique"
    substanreview_root = RAW_ROOT / "evaluation/substanreview"
    substanreview_train = jsonl_rows_with_fields(
        substanreview_root / "train.jsonl",
        {"id", "review", "label"},
    )
    substanreview_test = jsonl_rows_with_fields(
        substanreview_root / "test.jsonl",
        {"id", "review", "label"},
    )
    forbidden_candidates = [
        ROOT / "dataset/legacy_sources",
        *RAW_ROOT.rglob(".git"),
        *RAW_ROOT.rglob("*.zip"),
    ]
    forbidden_paths = [path for path in forbidden_candidates if path.exists()]

    checks = {
        "raw_primary": {
            "passed": (
                openreview_manifest["papers"] >= 30
                and openreview_manifest["official_reviews"] >= 120
                and len(valid_pdfs(RAW_ROOT / "primary/openreview_iclr2025_seed/pdfs"))
                >= openreview_manifest["papers"]
                and (RAW_ROOT / "restricted/nlpeer").exists()
            ),
            "openreview_papers": openreview_manifest["papers"],
            "openreview_reviews": openreview_manifest["official_reviews"],
            "openreview_valid_pdfs": len(
                valid_pdfs(RAW_ROOT / "primary/openreview_iclr2025_seed/pdfs")
            ),
            "nlpeer_status": "requires_application",
        },
        "strict_evaluation": {
            "passed": (
                jsonl_rows_with_fields(
                    peerqa_root / "qa.jsonl",
                    {"question_id", "paper_id", "answer_evidence_mapped"},
                )
                == 579
                and jsonl_rows_with_fields(
                    peerqa_root / "papers.jsonl",
                    {"idx", "paper_id", "content"},
                )
                == 24_265
                and json_object_size(claimcheck_root / "source/main.json") == 55
                and json_object_size(claimcheck_root / "related_work/main.json") == 43
                and jsonl_rows_with_fields(
                    reviewcritique_root / "ReviewCritique.jsonl",
                    {"body_text", "decision", "review#1"},
                )
                == 100
                and substanreview_train == 440
                and substanreview_test == 110
            ),
            "peerqa_qa": jsonl_rows(peerqa_root / "qa.jsonl"),
            "peerqa_paper_rows": jsonl_rows(peerqa_root / "papers.jsonl"),
            "claimcheck_source_pairs": json_object_size(claimcheck_root / "source/main.json"),
            "claimcheck_related_work_pairs": json_object_size(
                claimcheck_root / "related_work/main.json"
            ),
            "reviewcritique_human_papers": jsonl_rows(
                reviewcritique_root / "ReviewCritique.jsonl"
            ),
            "reviewcritique_llm_papers": jsonl_rows(
                reviewcritique_root / "ReviewCritique_LLM.jsonl"
            ),
            "substanreview_reviews": substanreview_train + substanreview_test,
        },
        "literature_corpus": {
            "passed": len(literature_files) >= 60,
            "paired_library_files": len(literature_files),
        },
        "unseen_demo": {
            "passed": (
                arxiv_manifest["papers"] >= 20
                and len(valid_pdfs(arxiv_snapshot_root / "pdfs")) >= 20
            ),
            "arxiv_papers": arxiv_manifest["papers"],
            "arxiv_valid_pdfs": len(valid_pdfs(arxiv_snapshot_root / "pdfs")),
            "snapshot": str(arxiv_snapshot_root.relative_to(ROOT)),
        },
        "clean_dataset_layout": {
            "passed": not forbidden_paths,
            "forbidden_paths": [str(path) for path in forbidden_paths],
            "roles": ["primary", "evaluation", "literature", "demo", "restricted"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "All four required data layers are available or explicitly gated.",
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = ROOT.parent / ".omx/specs/autoresearch-evireview-dataset-bootstrap/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
