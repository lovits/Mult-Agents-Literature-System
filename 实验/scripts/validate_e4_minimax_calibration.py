import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    result = json.loads(
        (EXPERIMENT_ROOT / "outputs/metrics/e4_minimax_calibration.json").read_text(
            encoding="utf-8"
        )
    )
    systems = result["systems"]
    integrity = result["integrity"]
    quota_blocked = (
        result["evaluated"] > 0
        and integrity["failures"] > 0
        and integrity.get("failure_reasons") == {"http_429": integrity["failures"]}
    )
    checks = {
        "provider": {
            "passed": (
                result["protocol"]["provider_backed"] is True
                and result["protocol"]["model"] == "MiniMax-M2.7"
            ),
            "model": result["protocol"]["model"],
            "provider_backed": result["protocol"]["provider_backed"],
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
            "passed": all(systems[name]["tokens_per_candidate"] > 0 for name in ["A1", "A2", "A3", "A4"]),
            "tokens_per_candidate": {
                name: systems[name]["tokens_per_candidate"] for name in systems
            },
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "pending_quota" if quota_blocked else "failed",
        "passed": passed,
        "summary": (
            "MiniMax-M2.7 E4 provider calibration is validated."
            if passed
            else "MiniMax-M2.7 is reachable, but Token Plan quota blocks calibration."
            if quota_blocked
            else "MiniMax-M2.7 E4 provider calibration failed."
        ),
        "checks": checks,
        "metrics": systems,
        "next_experiment": "Scale provider-backed E4 A0-A4 after calibration diagnosis",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-minimax-calibration/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
