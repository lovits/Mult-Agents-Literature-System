import json

from scripts.validate_e6_candidate_diagnostics import validate


def test_validate_e6_candidate_diagnostics_accepts_actionable_diagnostics(tmp_path):
    metrics = {
        "protocol": {
            "name": "e6-candidate-diagnostics-v1",
            "gold_usage": "diagnostic_only_official_review_weakness_proxy",
            "accept_reject_decision": False,
        },
        "dataset": {"openreview_papers": 30, "openreview_reviews": 122},
        "systems": {
            "B2_system_generated_structured_report": {
                "overall_proxy_overlap@k": 0.05,
                "aspect_distribution": {"experiment": 30},
                "aspect_proxy_overlap@k": {"experiment": 0.05},
                "zero_overlap_rate": 0.1,
                "paper_score_mean": 0.05,
                "paper_score_median": 0.05,
            },
            "B3_cue_aware_structured_report": {
                "overall_proxy_overlap@k": 0.06,
                "aspect_distribution": {"experiment": 20, "missing_baseline": 10},
                "aspect_proxy_overlap@k": {"experiment": 0.06, "missing_baseline": 0.07},
                "zero_overlap_rate": 0.05,
                "paper_score_mean": 0.06,
                "paper_score_median": 0.06,
            },
        },
        "comparison": {
            "b3_minus_b2_mean_delta": 0.01,
            "b3_improved_papers": 12,
            "b3_tied_papers": 10,
            "b3_regressed_papers": 8,
            "failure_or_tie_rate": 0.6,
        },
        "failure_cases": [{"paper_id": "p1"}],
        "next_optimization_hints": ["inspect failures"],
    }
    path = tmp_path / "diagnostics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["checks"]["comparison"]["passed"] is True
    assert result["metrics"]["b3_minus_b2_mean_delta"] == 0.01
