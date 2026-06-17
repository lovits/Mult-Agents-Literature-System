import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "dataset/raw"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_pdf_count(path: Path) -> int:
    count = 0
    for pdf in path.glob("*.pdf"):
        if pdf.stat().st_size > 1_000 and pdf.read_bytes()[:5] == b"%PDF-":
            count += 1
    return count


def parquet_like(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000:
        return False
    with path.open("rb") as handle:
        head = handle.read(4)
        handle.seek(-4, 2)
        tail = handle.read(4)
    return head == b"PAR1" and tail == b"PAR1"


def validate() -> dict:
    openreview_expanded = load_json(
        RAW_ROOT / "primary/openreview_iclr2025_expanded_100/manifest.json"
    )
    arxiv_expanded = load_json(RAW_ROOT / "demo/arxiv_unseen_2026-06-17/manifest.json")
    peerqa_xt_root = RAW_ROOT / "evaluation/peerqa_xt"
    peerqa_xt_files = {
        "readme": peerqa_xt_root / "README.md",
        "test": peerqa_xt_root / "data/test-00000-of-00001.parquet",
        "validation": peerqa_xt_root / "data/validation-00000-of-00001.parquet",
        "train_00000": peerqa_xt_root / "data/train-00000-of-00002.parquet",
        "train_00001": peerqa_xt_root / "data/train-00001-of-00002.parquet",
    }
    researcharcade_root = RAW_ROOT / "primary/researcharcade_openreview_papers_reviews"
    researcharcade_files = {
        "readme": researcharcade_root / "README.md",
        "converted_train": researcharcade_root / "converted/default/train/0000.parquet",
    }
    report_path = ROOT / "reports/data_expansion_2026-06-17.md"

    checks = {
        "openreview_expanded_100_snapshot": {
            "passed": (
                openreview_expanded["papers"] >= 100
                and openreview_expanded["official_reviews"] >= 200
                and openreview_expanded["valid_pdfs"] >= 30
                and openreview_expanded["pdf_failures"] > 0
                and openreview_expanded["review_fetch_failures"] > 0
            ),
            "papers": openreview_expanded["papers"],
            "official_reviews": openreview_expanded["official_reviews"],
            "valid_pdfs": openreview_expanded["valid_pdfs"],
            "pdf_failures": openreview_expanded["pdf_failures"],
            "review_fetch_failures": openreview_expanded["review_fetch_failures"],
            "role": "partial expansion; not a replacement for the complete 30-paper seed",
        },
        "arxiv_unseen_20_snapshot": {
            "passed": (
                arxiv_expanded["papers"] >= 20
                and arxiv_expanded["valid_pdfs"] >= 20
                and valid_pdf_count(RAW_ROOT / "demo/arxiv_unseen_2026-06-17/pdfs") >= 20
                and "unseen" in arxiv_expanded["supervision"]
            ),
            "papers": arxiv_expanded["papers"],
            "valid_pdfs": arxiv_expanded["valid_pdfs"],
            "role": "unseen demonstration only",
        },
        "peerqa_xt_complete_snapshot": {
            "passed": (
                peerqa_xt_files["readme"].exists()
                and parquet_like(peerqa_xt_files["test"])
                and parquet_like(peerqa_xt_files["validation"])
                and parquet_like(peerqa_xt_files["train_00000"])
                and parquet_like(peerqa_xt_files["train_00001"])
            ),
            "downloaded_files": [
                name for name, path in peerqa_xt_files.items() if path.exists()
            ],
            "missing_files": [
                name for name, path in peerqa_xt_files.items() if not path.exists()
            ],
            "role": "complete auxiliary synthetic QA expansion; not a strict human-gold set",
        },
        "researcharcade_converted_snapshot": {
            "passed": (
                researcharcade_files["readme"].exists()
                and parquet_like(researcharcade_files["converted_train"])
            ),
            "downloaded_files": [
                name for name, path in researcharcade_files.items() if path.exists()
            ],
            "role": (
                "OpenReview paper-review metadata expansion candidate from HF converted parquet; "
                "requires schema inspection before main metrics"
            ),
        },
        "authorization_and_limitations_documented": {
            "passed": (
                report_path.exists()
                and "NLPEERv2" in report_path.read_text(encoding="utf-8")
                and "Review-5K" in report_path.read_text(encoding="utf-8")
                and "HF_TOKEN" in report_path.read_text(encoding="utf-8")
                and "ResearchArcade" in report_path.read_text(encoding="utf-8")
            ),
            "report": str(report_path),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "Data expansion artifacts are locally verifiable with documented authorization "
            "and download limitations."
        ),
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = ROOT.parent / ".omx/specs/autoresearch-data-expansion-2026-06-17/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
