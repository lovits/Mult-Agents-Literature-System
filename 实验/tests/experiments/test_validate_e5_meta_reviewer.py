import json

from scripts.validate_e5_meta_reviewer import validate


def test_validate_e5_meta_reviewer_accepts_ranker_result(tmp_path):
    metrics = {
        "protocol": {
            "name": "e5-meta-reviewer-ranker-v1",
            "gold_used_only_for_metrics": True,
            "covered_refuted_gold": False,
            "uses_e4_audit_trace": True,
            "uses_substanreview_auxiliary": True,
            "uses_literature_rag_boundary": True,
        },
        "dataset": {"evaluated_candidates": 155, "paper_groups": 55},
        "systems": {
            "R0_input_order": {
                "top_k_agreement_precision": 0.4,
                "keep_coverage@k": 0.3,
                "redundancy_rate": 0.2,
                "confidence_brier": 0.3,
            },
            "R1_text_severity": {
                "top_k_agreement_precision": 0.45,
                "keep_coverage@k": 0.35,
                "redundancy_rate": 0.2,
                "confidence_brier": 0.25,
            },
            "R2_text_dedup": {
                "top_k_agreement_precision": 0.45,
                "keep_coverage@k": 0.35,
                "redundancy_rate": 0.1,
                "confidence_brier": 0.25,
            },
            "R3_evidence_aware": {
                "top_k_agreement_precision": 0.5,
                "keep_coverage@k": 0.4,
                "redundancy_rate": 0.1,
                "confidence_brier": 0.22,
            },
        },
    }
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["checks"]["baseline_improvement"]["passed"] is True
    assert result["checks"]["dedup_redundancy"]["passed"] is True
