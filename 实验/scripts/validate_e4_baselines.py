import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_ASSOCIATION_SYSTEMS = {
    "C0_position",
    "C1_bm25",
    "C2_dense",
    "C3_hybrid",
}


def validate() -> dict:
    result = _read_result()
    protocol = result["protocol"]
    association = result["association"]
    labeling = result["labeling"]
    systems = association["systems"]
    strongest_system = max(systems, key=lambda name: systems[name]["recall@5"])
    excluded = sum(association["excluded_with_reason"].values())
    w0 = labeling["W0_pilot_prior"]

    checks = {
        "protocol": {
            "passed": (
                protocol["development_split"] == "pilot"
                and protocol["evaluation_split"] == "main"
                and protocol["gold_used_only_for_evaluation"] is True
                and protocol["covered_refuted_gold"] is False
            ),
            "development_split": protocol["development_split"],
            "evaluation_split": protocol["evaluation_split"],
            "gold_used_only_for_evaluation": protocol["gold_used_only_for_evaluation"],
            "covered_refuted_gold": protocol["covered_refuted_gold"],
        },
        "association": {
            "passed": (
                association["evaluated"] == 91
                and excluded == 64
                and len(association["sample_results"]) == 91
                and set(systems) == EXPECTED_ASSOCIATION_SYSTEMS
                and strongest_system == "C1_bm25"
                and systems["C1_bm25"]["recall@5"] > 0.75
            ),
            "evaluated": association["evaluated"],
            "excluded": excluded,
            "sample_results": len(association["sample_results"]),
            "systems": sorted(systems),
        },
        "labeling": {
            "passed": (
                labeling["evaluated"] == 155
                and w0["available"] is True
                and w0["cost_per_candidate"] == 0.0
            ),
            "evaluated": labeling["evaluated"],
            "W0_available": w0["available"],
            "W0_cost_per_candidate": w0["cost_per_candidate"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": (
            "E4 leakage-free association and labeling baselines are validated."
        ),
        "checks": checks,
        "metrics": {
            "strongest_association_system": strongest_system,
            "C1_bm25_recall@5": systems["C1_bm25"]["recall@5"],
            "C3_hybrid_recall@5": systems["C3_hybrid"]["recall@5"],
            "W0_weakness_type_macro_f1": w0["weakness_type_macro_f1"],
        },
        "next_experiment": "E4 A1-A4 evidence audit systems",
    }


def _read_result() -> dict:
    path = EXPERIMENT_ROOT / "outputs/metrics/e4_claimcheck_baselines.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e4-baselines/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
