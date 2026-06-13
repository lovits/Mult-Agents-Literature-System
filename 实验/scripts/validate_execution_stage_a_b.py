import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def validate() -> dict:
    substanreview = EXPERIMENT_ROOT / "dataset/raw/evaluation/substanreview"
    smoke_path = EXPERIMENT_ROOT / "outputs/metrics/e2_paper_rag_smoke.json"
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    reviews = jsonl_rows(substanreview / "train.jsonl") + jsonl_rows(
        substanreview / "test.jsonl"
    )
    systems = sorted(smoke["systems"])
    checks = {
        "execution_plan": {
            "passed": (EXPERIMENT_ROOT / "EXECUTION_PLAN.md").exists(),
        },
        "substanreview": {
            "passed": reviews == 550,
            "reviews": reviews,
        },
        "e2_smoke": {
            "passed": (
                systems == ["P0", "P1", "P2", "P3", "P4"]
                and smoke["samples"] == 136
                and not smoke["failures"]
                and smoke["protocol"]["formal_result"] is False
                and all("precision@5" in metrics for metrics in smoke["systems"].values())
            ),
            "systems": systems,
            "samples": smoke["samples"],
            "formal_result": smoke["protocol"]["formal_result"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Dataset stage A and E2 smoke stage B are validated.",
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-execution-stage-a-b/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
