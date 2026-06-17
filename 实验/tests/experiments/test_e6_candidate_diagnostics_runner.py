from evireview.evaluation.e6_candidate_diagnostics import run_candidate_diagnostics


def test_e6_candidate_diagnostics_reports_paper_deltas_and_failure_cases():
    submissions = [
        {
            "paper_id": "p1",
            "content": {"title": "Paper 1"},
            "reviews": [
                {
                    "id": "r1",
                    "content": {
                        "weaknesses": "The benchmark needs stronger human annotation details."
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
                    "content": {"weaknesses": "The method assumptions are unclear."},
                }
            ],
        },
    ]
    e6_result = {
        "protocol": {"name": "e6-end-to-end-structured-report-v1"},
        "system_generated_reports": [
            {
                "paper_id": "p1",
                "title": "Paper 1",
                "top_weaknesses": [
                    {"aspect": "experiment", "weakness": "The evaluation needs ablation."}
                ],
            },
            {
                "paper_id": "p2",
                "title": "Paper 2",
                "top_weaknesses": [
                    {"aspect": "method", "weakness": "The method assumptions are unclear."}
                ],
            },
        ],
        "cue_aware_reports": [
            {
                "paper_id": "p1",
                "title": "Paper 1",
                "top_weaknesses": [
                    {
                        "aspect": "experiment",
                        "weakness": "The benchmark needs stronger human annotation details.",
                    }
                ],
            },
            {
                "paper_id": "p2",
                "title": "Paper 2",
                "top_weaknesses": [
                    {"aspect": "novelty", "weakness": "The novelty claim needs positioning."}
                ],
            },
        ],
    }

    result = run_candidate_diagnostics(e6_result, submissions)

    assert result["comparison"]["b3_improved_papers"] == 1
    assert result["comparison"]["b3_regressed_papers"] == 1
    assert result["failure_cases"][0]["paper_id"] == "p2"
    assert result["systems"]["B3_cue_aware_structured_report"]["aspect_distribution"][
        "experiment"
    ] == 1
    assert result["next_optimization_hints"]
