import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def json_object_size(path: Path) -> int:
    return len(json.loads(path.read_text(encoding="utf-8")))


def validate() -> dict:
    openreview_manifest = json.loads(
        (ROOT / "dataset/raw/openreview/iclr2025_seed/manifest.json").read_text(encoding="utf-8")
    )
    arxiv_manifest = json.loads(
        (ROOT / "dataset/raw/arxiv_unseen/2026-06-13/manifest.json").read_text(encoding="utf-8")
    )
    literature_files = [
        path
        for path in (ROOT / "dataset/raw/local_literature/source").rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".pdf"}
    ]

    checks = {
        "raw_primary": {
            "passed": (
                openreview_manifest["papers"] == 10
                and openreview_manifest["official_reviews"] >= 40
                and len(list((ROOT / "dataset/raw/openreview/iclr2025_seed/pdfs").glob("*.pdf"))) == 10
                and (ROOT / "dataset/raw/nlpeer/loader").exists()
            ),
            "openreview_papers": openreview_manifest["papers"],
            "openreview_reviews": openreview_manifest["official_reviews"],
            "nlpeer_status": "requires_application",
        },
        "strict_evaluation": {
            "passed": (
                jsonl_rows(ROOT / "dataset/raw/peerqa/data/qa.jsonl") == 579
                and jsonl_rows(ROOT / "dataset/raw/peerqa/data/papers.jsonl") == 24_265
                and json_object_size(
                    ROOT / "dataset/raw/claimcheck/repository/data/texts/source/main.json"
                )
                == 55
                and jsonl_rows(
                    ROOT / "dataset/raw/reviewcritique/repository/data/ReviewCritique.jsonl"
                )
                == 100
            ),
            "peerqa_qa": jsonl_rows(ROOT / "dataset/raw/peerqa/data/qa.jsonl"),
            "peerqa_paper_rows": jsonl_rows(ROOT / "dataset/raw/peerqa/data/papers.jsonl"),
            "claimcheck_source_pairs": json_object_size(
                ROOT / "dataset/raw/claimcheck/repository/data/texts/source/main.json"
            ),
            "reviewcritique_human_papers": jsonl_rows(
                ROOT / "dataset/raw/reviewcritique/repository/data/ReviewCritique.jsonl"
            ),
            "reviewcritique_llm_papers": jsonl_rows(
                ROOT / "dataset/raw/reviewcritique/repository/data/ReviewCritique_LLM.jsonl"
            ),
        },
        "literature_corpus": {
            "passed": len(literature_files) >= 60,
            "paired_library_files": len(literature_files),
        },
        "unseen_demo": {
            "passed": (
                arxiv_manifest["papers"] == 5
                and len(list((ROOT / "dataset/raw/arxiv_unseen/2026-06-13/pdfs").glob("*.pdf"))) == 5
            ),
            "arxiv_papers": arxiv_manifest["papers"],
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
