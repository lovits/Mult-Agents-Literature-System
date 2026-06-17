import json

from scripts.run_e6_candidate_diagnostics import run


def test_run_e6_candidate_diagnostics_writes_metrics_and_report(tmp_path):
    openreview = tmp_path / "openreview"
    openreview.mkdir()
    submissions = [
        {
            "paper_id": "p1",
            "content": {"title": "Paper 1"},
            "reviews": [
                {
                    "id": "r1",
                    "content": {"weaknesses": "The baseline comparison is weak."},
                }
            ],
        }
    ]
    (openreview / "submissions_with_reviews.json").write_text(
        json.dumps(submissions),
        encoding="utf-8",
    )
    e6_metrics = tmp_path / "e6.json"
    e6_metrics.write_text(
        json.dumps(
            {
                "protocol": {"name": "e6-end-to-end-structured-report-v1"},
                "system_generated_reports": [
                    {
                        "paper_id": "p1",
                        "title": "Paper 1",
                        "top_weaknesses": [
                            {
                                "aspect": "experiment",
                                "weakness": "The empirical evaluation needs ablation.",
                            }
                        ],
                    }
                ],
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
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "diagnostics.json"
    report = tmp_path / "diagnostics.md"
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                f"e6_metrics: {e6_metrics}",
                f"openreview_path: {openreview}",
                "top_failure_count: 3",
                f"output: {output}",
                f"report: {report}",
            ]
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert report.exists()
    assert result["comparison"]["b3_improved_papers"] == 1
    assert "E6 Candidate Generation Diagnostics" in report.read_text(encoding="utf-8")
