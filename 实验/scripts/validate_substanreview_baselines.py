import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_SYSTEMS = {"S0_proximity", "S1_lexical", "S2_hybrid"}


def validate(metrics_path: Path | None = None) -> dict:
    result = json.loads(
        (metrics_path or EXPERIMENT_ROOT / "outputs/metrics/substanreview_baselines.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = result["protocol"]
    dataset = result["dataset"]
    evaluation = result["evaluation"]
    systems = result["systems"]
    best_system = max(systems, key=lambda name: systems[name]["supported_f1"])
    checks = {
        "protocol": {
            "passed": (
                protocol["development_split"] == "train"
                and protocol["evaluation_split"] == "test"
                and protocol["gold_claim_spans"] is True
                and protocol["development_gold_used_for_threshold_tuning"] is True
                and protocol["evaluation_gold_used_only_for_metrics"] is True
            ),
            "development_split": protocol["development_split"],
            "evaluation_split": protocol["evaluation_split"],
        },
        "evaluation_boundary": {
            "passed": (
                protocol["weakness_validity_gold"] is False
                and protocol["covered_refuted_gold"] is False
                and dataset["supports"]["claim_evidence_substantiation"] is True
                and dataset["supports"]["weakness_validity"] is False
                and dataset["supports"]["covered_refuted_gold"] is False
            ),
            "weakness_validity_gold": protocol["weakness_validity_gold"],
            "covered_refuted_gold": protocol["covered_refuted_gold"],
        },
        "dataset": {
            "passed": (
                dataset["reviews"] == 550
                and dataset["train_reviews"] == 440
                and dataset["test_reviews"] == 110
                and dataset["claims"] == 2940
            ),
            "reviews": dataset["reviews"],
            "claims": dataset["claims"],
        },
        "evaluation_split": {
            "passed": (
                dataset["test_reviews"] == 110
                and evaluation["reviews"] >= 100
                and evaluation["claims"] == 580
                and len(result["sample_results"]) == 580
            ),
            "test_reviews": dataset["test_reviews"],
            "claim_bearing_reviews": evaluation["reviews"],
            "claims": evaluation["claims"],
            "sample_results": len(result["sample_results"]),
        },
        "systems": {
            "passed": (
                set(systems) == EXPECTED_SYSTEMS
                and all(0 <= values["supported_f1"] <= 1 for values in systems.values())
                and all(0 <= values["evidence_hit@1"] <= 1 for values in systems.values())
            ),
            "systems": sorted(systems),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "SubstanReview gold-claim evidence-linkage baselines are validated as auxiliary substantiation evidence.",
        "checks": checks,
        "best_system": best_system,
        "metrics": {
            "test_claim_evidence_coverage": evaluation["claim_evidence_coverage"],
            "test_substantiated_claim_rate": evaluation[
                "substantiated_claim_rate"
            ],
            "best_supported_f1": systems[best_system]["supported_f1"],
            "best_evidence_hit@1": systems[best_system]["evidence_hit@1"],
            "best_evidence_token_f1": systems[best_system]["evidence_token_f1"],
        },
        "next_experiment": "Use SubstanReview metrics as E4/E6 auxiliary evidence and proceed to Literature-RAG E3.",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-substanreview-baselines/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
