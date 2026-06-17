from evireview.evaluation.e6_b5_diagnostics import run_b5_diagnostics


def test_e6_b5_diagnostics_reports_balanced_agent_rag_bottlenecks():
    submissions = [
        {
            "paper_id": "p1",
            "content": {"title": "Paper 1"},
            "reviews": [
                {
                    "id": "r1",
                    "content": {
                        "weaknesses": "The baseline comparison is weak."
                    },
                }
            ],
        },
        {
            "paper_id": "p2",
            "content": {"title": "Paper 2"},
            "reviews": [
                {
                    "id": "r2",
                    "content": {"weaknesses": "The ablation study is missing."},
                }
            ],
        },
    ]
    e6_result = {
        "protocol": {"name": "e6-end-to-end-structured-report-v1"},
        "cue_aware_reports": [
            {
                "paper_id": "p1",
                "title": "Paper 1",
                "top_weaknesses": [
                    {
                        "aspect": "missing_baseline",
                        "weakness": "The baseline comparison is weak.",
                    }
                ],
            },
            {
                "paper_id": "p2",
                "title": "Paper 2",
                "top_weaknesses": [
                    {
                        "aspect": "method",
                        "weakness": "The method assumptions need clearer justification.",
                    }
                ],
            },
        ],
        "agent_rag_reports": [
            {
                "paper_id": "p1",
                "title": "Paper 1",
                "top_weaknesses": [
                    {
                        "aspect": "method",
                        "weakness": "The method assumptions need clearer justification.",
                        "audit_decision": "keep",
                        "support_strength": 0.6,
                        "refutation_strength": 0.1,
                    }
                ],
            },
            {
                "paper_id": "p2",
                "title": "Paper 2",
                "top_weaknesses": [
                    {
                        "aspect": "experiment",
                        "weakness": "The ablation study is missing.",
                        "audit_decision": "keep",
                        "support_strength": 0.8,
                        "refutation_strength": 0.0,
                    }
                ],
            },
        ],
        "balanced_agent_rag_reports": [
            {
                "paper_id": "p1",
                "title": "Paper 1",
                "top_weaknesses": [
                    {
                        "aspect": "missing_baseline",
                        "weakness": "The baseline comparison is weak.",
                        "audit_decision": "keep",
                        "support_strength": 0.7,
                        "refutation_strength": 0.0,
                    }
                ],
            },
            {
                "paper_id": "p2",
                "title": "Paper 2",
                "top_weaknesses": [
                    {
                        "aspect": "novelty",
                        "weakness": "The novelty claim needs stronger related-work positioning.",
                        "audit_decision": "rewrite",
                        "support_strength": 0.5,
                        "refutation_strength": 0.2,
                    }
                ],
            },
        ],
    }

    result = run_b5_diagnostics(e6_result, submissions, top_failure_count=2)

    assert result["protocol"]["name"] == "e6-b5-balanced-agent-rag-diagnostics-v1"
    assert result["comparison"]["b5_improved_vs_b4_papers"] == 1
    assert result["comparison"]["b5_regressed_vs_b4_papers"] == 1
    assert result["systems"]["B5_balanced_agent_rag_pipeline_report"][
        "aspect_distribution"
    ] == {"missing_baseline": 1, "novelty": 1}
    assert result["low_overlap_cases"][0]["paper_id"] == "p2"
    assert result["aspect_bottlenecks"][0]["aspect"] == "novelty"
    assert result["next_optimization_hints"]
