import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_SYSTEMS = {
    "R0_input_order",
    "R1_text_severity",
    "R2_text_dedup",
    "R3_evidence_aware",
}


def validate(metrics_path: Path | None = None) -> dict:
    result = json.loads(
        (metrics_path or EXPERIMENT_ROOT / "outputs/metrics/e5_meta_reviewer.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = result["protocol"]
    dataset = result["dataset"]
    systems = result["systems"]
    baseline = systems["R0_input_order"]
    text = systems["R1_text_severity"]
    dedup = systems["R2_text_dedup"]
    evidence = systems["R3_evidence_aware"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "e5-meta-reviewer-ranker-v1"
                and protocol["gold_used_only_for_metrics"] is True
                and protocol["covered_refuted_gold"] is False
                and protocol["uses_e4_audit_trace"] is True
                and protocol["uses_substanreview_auxiliary"] is True
                and protocol["uses_literature_rag_boundary"] is True
            ),
            "protocol": protocol["name"],
        },
        "dataset": {
            "passed": dataset["evaluated_candidates"] >= 150 and dataset["paper_groups"] >= 50,
            "evaluated_candidates": dataset["evaluated_candidates"],
            "paper_groups": dataset["paper_groups"],
        },
        "systems": {
            "passed": set(systems) == EXPECTED_SYSTEMS,
            "systems": sorted(systems),
        },
        "baseline_improvement": {
            "passed": evidence["top_k_agreement_precision"] >= baseline["top_k_agreement_precision"],
            "baseline_top_k_precision": baseline["top_k_agreement_precision"],
            "evidence_top_k_precision": evidence["top_k_agreement_precision"],
        },
        "dedup_redundancy": {
            "passed": dedup["redundancy_rate"] <= text["redundancy_rate"],
            "text_redundancy_rate": text["redundancy_rate"],
            "dedup_redundancy_rate": dedup["redundancy_rate"],
        },
        "evidence_boundary": {
            "passed": evidence["confidence_brier"] <= 1.0,
            "confidence_brier": evidence["confidence_brier"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "E5 Meta-Reviewer ranking baselines validate evidence-aware Top-K selection without covered/refuted Gold claims.",
        "checks": checks,
        "metrics": {
            "baseline_top_k_agreement_precision": baseline["top_k_agreement_precision"],
            "text_top_k_agreement_precision": text["top_k_agreement_precision"],
            "dedup_top_k_agreement_precision": dedup["top_k_agreement_precision"],
            "evidence_top_k_agreement_precision": evidence["top_k_agreement_precision"],
            "evidence_keep_coverage@k": evidence["keep_coverage@k"],
            "evidence_redundancy_rate": evidence["redundancy_rate"],
            "evidence_confidence_brier": evidence["confidence_brier"],
        },
        "next_experiment": "Connect E5 ranking output to the end-to-end E6 review report pipeline.",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e5-meta-reviewer/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
