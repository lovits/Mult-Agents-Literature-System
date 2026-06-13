import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_REVISION = "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a"


def validate() -> dict:
    formal = _read_result("e2_paper_rag_formal.json")
    ungated = _read_result("e2_paper_rag_formal_ungated.json")
    baseline_name = max(
        ("P0", "P1", "P2"),
        key=lambda name: formal["systems"][name]["recall@5"],
    )
    baseline = formal["systems"][baseline_name]
    p4 = formal["systems"]["P4"]
    ungated_p4 = ungated["systems"]["P4"]
    recall_delta = p4["recall@5"] - baseline["recall@5"]
    evidence_type_delta = (
        p4["evidence_type_match@5"] - baseline["evidence_type_match@5"]
    )
    latency_ratio = p4["latency_ms"] / formal["systems"]["P2"]["latency_ms"]
    success_criteria = {
        "recall_gain_passed": recall_delta >= 0.05,
        "evidence_type_gain_passed": evidence_type_delta >= 0.10,
        "latency_passed": latency_ratio <= 2.0,
    }
    checks = {
        "formal_run": {
            "passed": (
                formal["protocol"]["formal_result"] is True
                and formal["samples"] == 136
                and not formal["failures"]
                and formal["protocol"]["embedding_metadata"]["revision"]
                == EXPECTED_REVISION
            ),
            "samples": formal["samples"],
            "failures": len(formal["failures"]),
            "revision": formal["protocol"]["embedding_metadata"]["revision"],
        },
        "ungated_run_preserved": {
            "passed": (
                ungated["protocol"]["formal_result"] is True
                and ungated["samples"] == 136
                and not ungated["failures"]
            ),
        },
    }
    completed = all(check["passed"] for check in checks.values())
    experiment_success = all(success_criteria.values())
    return {
        "status": "passed" if completed else "failed",
        "passed": completed,
        "summary": "Formal E2 completed with an honest success-criteria verdict.",
        "experiment_verdict": (
            "passed_success_criteria" if experiment_success else "failed_with_metrics"
        ),
        "checks": checks,
        "metrics": {
            "strongest_baseline": baseline_name,
            "baseline_recall@5": baseline["recall@5"],
            "p4_recall@5": p4["recall@5"],
            "recall_delta": recall_delta,
            "baseline_evidence_type_match@5": baseline["evidence_type_match@5"],
            "p4_evidence_type_match@5": p4["evidence_type_match@5"],
            "evidence_type_delta": evidence_type_delta,
            "latency_ratio_vs_p2": latency_ratio,
            "gating_p4_recall_delta": p4["recall@5"] - ungated_p4["recall@5"],
        },
        "success_criteria": success_criteria,
    }


def _read_result(name: str) -> dict:
    path = EXPERIMENT_ROOT / "outputs/metrics" / name
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e2-formal/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
