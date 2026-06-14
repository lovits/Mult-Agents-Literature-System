import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    result = json.loads(
        (EXPERIMENT_ROOT / "outputs/metrics/e4_agnes_calibration.json").read_text(
            encoding="utf-8"
        )
    )
    systems = result["systems"]
    integrity = result["integrity"]
    checks = {
        "provider": {
            "passed": (
                result["protocol"]["provider_backed"] is True
                and result["protocol"]["model"] == "agnes-2.0-flash"
            ),
            "model": result["protocol"]["model"],
        },
        "coverage": {
            "passed": result["evaluated"] == 5 and len(result["traces"]) == 5,
            "evaluated": result["evaluated"],
            "traces": len(result["traces"]),
        },
        "systems": {
            "passed": set(systems) == {"A0", "A1", "A2", "A3", "A4"},
            "systems": sorted(systems),
        },
        "integrity": {
            "passed": integrity["failures"] == 0,
            **integrity,
        },
        "usage": {
            "passed": all(
                systems[name]["tokens_per_candidate"] > 0
                for name in ["A1", "A2", "A3", "A4"]
            ),
            "tokens_per_candidate": {
                name: systems[name]["tokens_per_candidate"] for name in systems
            },
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Agnes-2.0-Flash E4 five-sample provider calibration is validated.",
        "checks": checks,
        "metrics": systems,
        "next_experiment": "Scale Agnes provider-backed E4 A0-A4",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-agnes-calibration/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
