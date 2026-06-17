import json

from scripts.run_e6_b5_diagnostics import run


def test_run_e6_b5_diagnostics_writes_metrics_and_report(tmp_path):
    openreview = tmp_path / "openreview"
    openreview.mkdir()
    submissions = [
        {
            "paper_id": "p1",
            "content": {"title": "Paper 1"},
            "reviews": [
                {
                    "id": "r1",
                    "content": {"weaknesses": "The ablation study is missing."},
                }
            ],
        }
    ]
    (openreview / "submissions_with_reviews.json").write_text(
        json.dumps(submissions),
        encoding="utf-8",
    )
    e6_metrics = tmp_path / "e6.json"
    report = {
        "paper_id": "p1",
        "title": "Paper 1",
        "top_weaknesses": [
            {
                "aspect": "experiment",
                "weakness": "The ablation study is missing.",
                "audit_decision": "keep",
                "support_strength": 0.8,
                "refutation_strength": 0.0,
            }
        ],
    }
    e6_metrics.write_text(
        json.dumps(
            {
                "protocol": {"name": "e6-end-to-end-structured-report-v1"},
                "cue_aware_reports": [report],
                "agent_rag_reports": [report],
                "balanced_agent_rag_reports": [report],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "b5.json"
    report_path = tmp_path / "b5.md"
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                f"e6_metrics: {e6_metrics}",
                f"openreview_path: {openreview}",
                "top_failure_count: 3",
                f"output: {output}",
                f"report: {report_path}",
            ]
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert report_path.exists()
    assert result["comparison"]["b5_tied_vs_b4_papers"] == 1
    assert "E6 B5 Balanced Agent-RAG Diagnostics" in report_path.read_text(
        encoding="utf-8"
    )
