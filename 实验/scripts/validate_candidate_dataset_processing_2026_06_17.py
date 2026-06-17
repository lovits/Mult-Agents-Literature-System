import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_ROOT = ROOT / "dataset/processed/candidate_expansion_2026_06_17"
REPORT = ROOT / "reports/candidate_dataset_processing_2026-06-17.md"


def validate() -> dict:
    manifest_path = PROCESSED_ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    datasets = manifest.get("datasets", {})
    neurips = datasets.get("neurips_2023", {})
    reviewrebuttal = datasets.get("reviewrebuttal_test", {})
    peercheck = datasets.get("peercheck", {})
    openreview = datasets.get("openreview_raw_hf_shard0", {})
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""

    required_report_claims = [
        "NeurIPS 2023",
        "ReviewRebuttal test",
        "PeerCheck",
        "OpenReview Raw shard0",
        "没有复跑 E2/E4/E5/E6",
        "不能声称相对 baseline 的模型性能提升",
        "下一步",
    ]
    checks = {
        "manifest_exists": {
            "passed": manifest_path.exists() and manifest.get("status") == "processed",
            "path": str(manifest_path.relative_to(ROOT)),
        },
        "token_not_persisted": {
            "passed": manifest.get("token_persisted") is False,
            "raw_data_committed": manifest.get("raw_data_committed"),
        },
        "neurips_processed_sample": {
            "passed": neurips.get("papers", 0) >= 50
            and neurips.get("evidence_blocks", 0) >= 500
            and neurips.get("reviews", 0) >= 100
            and "abstract" in neurips.get("sections", {}),
            "summary": neurips,
        },
        "reviewrebuttal_diagnostics": {
            "passed": reviewrebuttal.get("papers", 0) >= 1_000
            and reviewrebuttal.get("reviews", 0) >= 1_000
            and reviewrebuttal.get("metareview_present", 0) >= 1,
            "summary": reviewrebuttal,
        },
        "peercheck_diagnostics": {
            "passed": peercheck.get("rows") == 100
            and peercheck.get("citation_markers", 0) >= 100
            and peercheck.get("weakness_sections", 0) >= 50,
            "summary": peercheck,
        },
        "openreview_raw_boundary": {
            "passed": openreview.get("downloaded") is True
            and openreview.get("parquet_like") is True
            and openreview.get("event_filter_status") == "pending_parquet_reader",
            "summary": openreview,
        },
        "report_claims": {
            "passed": all(claim in report_text for claim in required_report_claims),
            "missing": [
                claim for claim in required_report_claims if claim not in report_text
            ],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "Candidate datasets are processed into local experimental snapshots with "
            "clear boundaries and no baseline metric claim."
        ),
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = (
        ROOT.parent
        / ".omx/specs/autoresearch-candidate-dataset-processing-2026-06-17/result.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
