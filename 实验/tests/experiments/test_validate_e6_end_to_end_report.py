import json

from scripts.validate_e6_end_to_end_report import validate


def test_validate_e6_end_to_end_report_accepts_traceable_report_result(tmp_path):
    metrics = {
        "protocol": {
            "name": "e6-end-to-end-structured-report-v1",
            "accept_reject_decision": False,
            "arxiv_unseen_gold_metrics": False,
            "uses_component_outputs": ["E2", "E3", "E4", "E5"],
        },
        "dataset": {
            "openreview_papers": 10,
            "openreview_reviews": 41,
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
        },
        "unseen_demo": {"papers": 5, "gold_metrics_reported": False},
    }
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(path)

    assert result["status"] == "passed"
    assert result["checks"]["traceability_improvement"]["passed"] is True
    assert result["checks"]["unseen_boundary"]["passed"] is True
