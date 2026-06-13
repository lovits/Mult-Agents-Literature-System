import json
from pathlib import Path

from evireview.dao.claimcheck import ClaimCheckDataset


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    dataset = ClaimCheckDataset.from_source_dir(
        EXPERIMENT_ROOT / "dataset/raw/evaluation/claimcheck/texts/source"
    )
    summary = dataset.audit_summary()
    checks = {
        "claimcheck": {
            "passed": (
                summary["paper_review_pairs"] == 60
                and summary["weaknesses"] == 168
                and summary["target_claim_grounded_weaknesses"] == 120
            ),
            "paper_review_pairs": summary["paper_review_pairs"],
            "weaknesses": summary["weaknesses"],
            "grounded_weaknesses": summary["target_claim_grounded_weaknesses"],
        },
        "evaluation_boundary": {
            "passed": (
                summary["supports"]["claim_association"]
                and summary["supports"]["weakness_labeling"]
                and not summary["supports"]["covered_refuted_gold"]
            ),
            **summary["supports"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "CLAIMCHECK E4 foundation and label boundaries are validated.",
        "checks": checks,
        "next_experiment": "E4 claim association and weakness labeling baselines",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-claimcheck-foundation/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
