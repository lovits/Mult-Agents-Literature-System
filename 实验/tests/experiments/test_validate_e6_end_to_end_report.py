import json

from scripts.validate_e6_end_to_end_report import validate


def test_validate_e6_end_to_end_report_accepts_traceable_report_result(tmp_path):
    metrics = {
        "protocol": {
            "name": "e6-end-to-end-structured-report-v1",
            "accept_reject_decision": False,
            "arxiv_unseen_gold_metrics": False,
            "system_candidate_generation": "system_deterministic_baseline_v1",
            "cue_aware_candidate_generation": "system_cue_aware_baseline_v2",
            "uses_component_outputs": ["E2", "E3", "E4", "E5"],
        },
        "dataset": {
            "openreview_papers": 30,
            "openreview_reviews": 122,
            "arxiv_unseen_papers": 5,
        },
        "systems": {
            "B0_unstructured_review_dump": {
                "paper_report_coverage": 1.0,
                "trace_coverage": 0.0,
                "top_k_compliance": 0.0,
                "accept_reject_decisions": 0,
            },
            "B1_structured_evidence_report": {
                "paper_report_coverage": 1.0,
                "trace_coverage": 1.0,
                "top_k_compliance": 1.0,
                "accept_reject_decisions": 0,
            },
            "B2_system_generated_structured_report": {
                "paper_report_coverage": 1.0,
                "trace_coverage": 1.0,
                "top_k_compliance": 1.0,
                "accept_reject_decisions": 0,
                "review_leakage_free": True,
                "official_weakness_proxy_overlap@k": 0.25,
                "aspect_diversity@k": 1.0,
                "redundancy_rate@k": 0.0,
            },
            "B3_cue_aware_structured_report": {
                "paper_report_coverage": 1.0,
                "trace_coverage": 1.0,
                "top_k_compliance": 1.0,
                "accept_reject_decisions": 0,
                "review_leakage_free": True,
                "official_weakness_proxy_overlap@k": 0.32,
                "official_weakness_proxy_overlap_delta_vs_b2": 0.07,
                "aspect_diversity@k": 1.0,
                "redundancy_rate@k": 0.0,
            },
        },
        "unseen_demo": {"papers": 5, "gold_metrics_reported": False},
    }
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["checks"]["traceability_improvement"]["passed"] is True
    assert result["checks"]["system_generated_candidates"]["passed"] is True
    assert result["checks"]["cue_aware_optimization"]["passed"] is True
    assert result["checks"]["unseen_boundary"]["passed"] is True
