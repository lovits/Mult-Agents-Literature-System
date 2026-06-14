import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    result = json.loads(
        (EXPERIMENT_ROOT / "outputs/metrics/e4_audit_protocol_smoke.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = result["protocol"]
    integrity = result["integrity"]
    systems = result["systems"]
    checks = {
        "protocol": {
            "passed": (
                protocol["formal_a0_a4_result"] is False
                and protocol["provider_backed"] is False
                and protocol["fixed_bidirectional_execution"] is True
                and protocol["label_mapping_is_proxy"] is True
                and protocol["covered_refuted_gold"] is False
            ),
            **protocol,
        },
        "coverage": {
            "passed": result["evaluated"] == 155 and len(result["traces"]) == 155,
            "evaluated": result["evaluated"],
            "traces": len(result["traces"]),
        },
        "integrity": {
            "passed": all(value == 0 for value in integrity.values()),
            **integrity,
        },
        "smoke_systems": {
            "passed": set(systems) == {"A3_heuristic_smoke", "A4_heuristic_smoke"},
            "systems": sorted(systems),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "E4 fixed bidirectional audit protocol smoke is validated without "
            "misreporting heuristic results as formal A0-A4."
        ),
        "checks": checks,
        "metrics": systems,
        "next_experiment": "Formal provider-backed E4 A0-A4",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-audit-protocol/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
