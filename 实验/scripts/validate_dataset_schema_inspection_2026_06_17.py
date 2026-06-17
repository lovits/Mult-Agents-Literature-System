import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "dataset/raw"
REPORT = ROOT / "reports/dataset_schema_inspection_2026-06-17.md"


EXPECTED_SIZES = {
    RAW_ROOT / "evaluation/peerqa_xt/data/test-00000-of-00001.parquet": 31_160_942,
    RAW_ROOT / "evaluation/peerqa_xt/data/validation-00000-of-00001.parquet": 33_141_812,
    RAW_ROOT / "evaluation/peerqa_xt/data/train-00000-of-00002.parquet": 150_099_121,
    RAW_ROOT / "evaluation/peerqa_xt/data/train-00001-of-00002.parquet": 106_039_698,
    RAW_ROOT
    / "primary/researcharcade_openreview_papers_reviews/converted/default/train/0000.parquet": 17_307_887,
}


def parquet_like(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000:
        return False
    with path.open("rb") as handle:
        head = handle.read(4)
        handle.seek(-4, 2)
        tail = handle.read(4)
    return head == b"PAR1" and tail == b"PAR1"


def validate() -> dict:
    parquet_checks = {
        str(path.relative_to(ROOT)): {
            "passed": parquet_like(path) and path.stat().st_size == expected_size,
            "size": path.stat().st_size if path.exists() else 0,
            "expected_size": expected_size,
        }
        for path, expected_size in EXPECTED_SIZES.items()
    }
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    required_claims = [
        "12,628",
        "10,128",
        "1,248",
        "1,252",
        "737,577",
        "`pid`, `qid`, `question`, `answer`, `paper`, `domain`",
        "`venue`, `paper_openreview_id`, `review_openreview_id`, `title`, `time`",
        "不能直接替代完整 review text",
        "不能声称模型性能提升",
    ]
    report_checks = {claim: claim in report_text for claim in required_claims}
    passed = all(check["passed"] for check in parquet_checks.values()) and all(
        report_checks.values()
    )
    result = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "PeerQA-XT and ResearchArcade schema inspection is documented and locally gated.",
        "checks": {
            "parquet_files": parquet_checks,
            "report_claims": report_checks,
        },
    }
    return result


def main() -> None:
    result = validate()
    output = ROOT.parent / ".omx/specs/autoresearch-dataset-schema-inspection-2026-06-17/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
