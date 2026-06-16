import json

from scripts.run_e6_end_to_end_report import run


def test_run_e6_end_to_end_report_writes_metrics_and_report(tmp_path):
    openreview = tmp_path / "openreview"
    openreview.mkdir()
    (openreview / "submissions_with_reviews.json").write_text(
        json.dumps(
            [
                {
                    "paper_id": "paper-1",
                    "content": {"title": "Paper", "abstract": "Abstract"},
                    "reviews": [
                        {
                            "id": "review-1",
                            "content": {"weaknesses": "Missing ablation study."},
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    unseen = tmp_path / "unseen"
    unseen.mkdir()
    (unseen / "papers.json").write_text(
        json.dumps(
            [
                {
                    "arxiv_id": "2606.00001v1",
                    "title": "Unseen Paper",
                    "local_pdf": "pdfs/2606.00001v1.pdf",
                    "published": "2026-06-01T00:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )
    for name in ["e2", "e3", "e4", "e5"]:
        (tmp_path / f"{name}.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    output = tmp_path / "metrics.json"
    report = tmp_path / "report.md"
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                f"openreview_path: {openreview}",
                f"unseen_path: {unseen}",
                "component_metrics:",
                f"  e2: {tmp_path / 'e2.json'}",
                f"  e3: {tmp_path / 'e3.json'}",
                f"  e4: {tmp_path / 'e4.json'}",
                f"  e5: {tmp_path / 'e5.json'}",
                "top_k: 1",
                f"output: {output}",
                f"report: {report}",
            ]
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert report.exists()
    assert result["systems"]["B1_structured_evidence_report"]["paper_report_coverage"] == 1.0
    assert "E6 End-to-End Structured Review Report" in report.read_text(encoding="utf-8")
