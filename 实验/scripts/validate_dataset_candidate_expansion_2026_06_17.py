import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "dataset/raw"
REPORT = ROOT / "reports/dataset_candidate_expansion_2026-06-17.md"


def parquet_like(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000:
        return False
    with path.open("rb") as handle:
        head = handle.read(4)
        handle.seek(-4, 2)
        tail = handle.read(4)
    return head == b"PAR1" and tail == b"PAR1"


def jsonl_summary(path: Path) -> dict:
    count = 0
    first = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            count += 1
            if first is None:
                first = json.loads(line)
    return {"rows": count, "keys": sorted(first.keys()) if isinstance(first, dict) else []}


def json_summary(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        first = payload[0] if payload else {}
        return {
            "container": "list",
            "rows": len(payload),
            "keys": sorted(first.keys()) if isinstance(first, dict) else [],
        }
    if isinstance(payload, dict):
        first = next(iter(payload.values())) if payload else {}
        return {
            "container": "dict",
            "rows": len(payload),
            "keys": sorted(first.keys()) if isinstance(first, dict) else [],
        }
    return {"container": type(payload).__name__, "rows": 0, "keys": []}


def no_hf_cache_dirs() -> bool:
    return not any(RAW_ROOT.glob("**/.cache"))


def validate() -> dict:
    openreview_parquet = (
        RAW_ROOT
        / "primary/openreview_raw_hf_shard0/data/train-00000-of-00006.parquet"
    )
    neurips_jsonl = (
        RAW_ROOT / "primary/neurips_2023_2025_2023_only/data/2023.jsonl"
    )
    peercheck_jsonl = RAW_ROOT / "evaluation/peercheck/train.jsonl"
    reviewrebuttal_json = RAW_ROOT / "evaluation/reviewrebuttal_test/REVIEWS_test.json"
    reviewrebuttal_parquet = (
        RAW_ROOT / "evaluation/reviewrebuttal_test/reviews_parquet/test/test.parquet"
    )

    neurips = jsonl_summary(neurips_jsonl)
    peercheck = jsonl_summary(peercheck_jsonl)
    reviewrebuttal = json_summary(reviewrebuttal_json)
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""

    required_report_claims = [
        "`Jasonpicky/openreview_raw`",
        "`djroytburg/NeurIPS-2023-2025`",
        "`TrustAIRLab/PeerCheck`",
        "`xxxxxsss/ReviewRebuttal`",
        "WestlakeNLP/Review-5K",
        "DeepReview-13K",
        "不能声称模型指标相对 baseline 提升",
        "不把 token 写入仓库",
        "下一步可以先把 `NeurIPS 2023` 和 `ReviewRebuttal test` 接入 E0 registry",
    ]

    checks = {
        "openreview_raw_hf_shard0": {
            "passed": parquet_like(openreview_parquet)
            and openreview_parquet.stat().st_size > 100_000_000,
            "path": str(openreview_parquet.relative_to(ROOT)),
            "size": openreview_parquet.stat().st_size if openreview_parquet.exists() else 0,
            "role": "primary review text expansion candidate",
        },
        "neurips_2023_jsonl": {
            "passed": neurips["rows"] >= 3_000
            and {
                "paper_id",
                "year",
                "conference",
                "accepted",
                "title",
                "abstract",
                "paper_text",
                "reviews",
            }.issubset(neurips["keys"]),
            "rows": neurips["rows"],
            "keys": neurips["keys"],
            "role": "primary full paper plus reviews expansion candidate",
        },
        "peercheck_jsonl": {
            "passed": peercheck["rows"] == 100
            and {"file", "answer"}.issubset(peercheck["keys"]),
            "rows": peercheck["rows"],
            "keys": peercheck["keys"],
            "role": "evidence-style review formatting diagnostic",
        },
        "reviewrebuttal_test": {
            "passed": reviewrebuttal["rows"] >= 1_000
            and {
                "paper_id",
                "reviews",
                "metareview",
                "decision",
            }.issubset(reviewrebuttal["keys"])
            and parquet_like(reviewrebuttal_parquet),
            "rows": reviewrebuttal["rows"],
            "keys": reviewrebuttal["keys"],
            "parquet_size": (
                reviewrebuttal_parquet.stat().st_size
                if reviewrebuttal_parquet.exists()
                else 0
            ),
            "role": "full-stage peer review diagnostic candidate",
        },
        "download_hygiene": {
            "passed": no_hf_cache_dirs(),
            "role": "only experiment data files are kept under raw dataset directories",
        },
        "report_claims": {
            "passed": all(claim in report_text for claim in required_report_claims),
            "missing": [
                claim for claim in required_report_claims if claim not in report_text
            ],
            "report": str(REPORT.relative_to(ROOT)),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "Candidate peer-review datasets are downloaded or authorization-gated with "
            "clear task roles and no metric-improvement claim."
        ),
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = (
        ROOT.parent
        / ".omx/specs/autoresearch-dataset-candidate-expansion-2026-06-17/result.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
