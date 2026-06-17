import json

from scripts.validate_e6_b5_diagnostics import validate


def test_validate_e6_b5_diagnostics_accepts_actionable_result(tmp_path):
    metrics = {
        "protocol": {
            "name": "e6-b5-balanced-agent-rag-diagnostics-v1",
            "source_experiment": "e6-end-to-end-structured-report-v1",
            "gold_usage": "diagnostic_only_official_review_weakness_proxy",
            "accept_reject_decision": False,
        },
        "dataset": {"openreview_papers": 30, "openreview_reviews": 122},
        "systems": {
            "B3_cue_aware_structured_report": {
                "overall_proxy_overlap@k": 0.054,
                "aspect_distribution": {"experiment": 30},
                "aspect_proxy_overlap@k": {"experiment": 0.054},
                "zero_overlap_rate": 0.02,
                "paper_score_mean": 0.054,
                "paper_score_median": 0.054,
            },
            "B4_agent_rag_pipeline_report": {
                "overall_proxy_overlap@k": 0.055,
                "aspect_distribution": {"experiment": 25, "method": 5},
                "aspect_proxy_overlap@k": {"experiment": 0.05, "method": 0.08},
                "zero_overlap_rate": 0.02,
                "paper_score_mean": 0.055,
                "paper_score_median": 0.055,
                "audit_decision_distribution": {"keep": 30},
                "support_strength_mean": 0.7,
                "refutation_strength_mean": 0.1,
            },
            "B5_balanced_agent_rag_pipeline_report": {
                "overall_proxy_overlap@k": 0.057,
                "aspect_distribution": {"experiment": 20, "method": 10},
                "aspect_proxy_overlap@k": {"experiment": 0.052, "method": 0.087},
                "zero_overlap_rate": 0.01,
                "paper_score_mean": 0.057,
                "paper_score_median": 0.057,
                "audit_decision_distribution": {"keep": 28, "rewrite": 2},
                "support_strength_mean": 0.72,
                "refutation_strength_mean": 0.08,
            },
        },
        "comparison": {
            "b5_minus_b4_mean_delta": 0.002,
            "b5_improved_vs_b4_papers": 14,
            "b5_tied_vs_b4_papers": 8,
            "b5_regressed_vs_b4_papers": 8,
            "b5_minus_b3_mean_delta": 0.003,
            "b5_improved_vs_b3_papers": 15,
            "b5_tied_vs_b3_papers": 7,
            "b5_regressed_vs_b3_papers": 8,
        },
        "aspect_bottlenecks": [{"aspect": "experiment", "proxy_overlap@k": 0.052}],
        "low_overlap_cases": [{"paper_id": "p1", "b5_proxy_overlap@k": 0.0}],
        "regression_vs_b4_cases": [{"paper_id": "p2"}],
        "next_optimization_hints": ["inspect experiment cases"],
    }
    path = tmp_path / "b5.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["metrics"]["b5_minus_b4_mean_delta"] == 0.002
    assert result["checks"]["diagnostic_actionability"]["passed"] is True
