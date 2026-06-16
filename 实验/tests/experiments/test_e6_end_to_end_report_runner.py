from evireview.evaluation.end_to_end_report_runner import (
    run_end_to_end_report_baseline,
)


def test_e6_builds_traceable_topk_reports_without_accept_reject_decisions():
    submissions = [
        {
            "paper_id": "paper-1",
            "content": {
                "title": "A Test Paper",
                "abstract": "This paper proposes a retrieval augmented method.",
            },
            "local_pdf": "pdfs/paper-1.pdf",
            "reviews": [
                {
                    "id": "review-1",
                    "content": {
                        "weaknesses": "- The paper lacks ablation experiments.\n- Baselines are limited.",
                        "rating": 6,
                        "confidence": 4,
                    },
                },
                {
                    "id": "review-2",
                    "content": {
                        "weaknesses": "The paper should clarify implementation details.",
                        "rating": 5,
                        "confidence": 3,
                    },
                },
            ],
        }
    ]
    arxiv = [
        {
            "arxiv_id": "2606.00001v1",
            "title": "Unseen Agent Paper",
            "local_pdf": "pdfs/2606.00001v1.pdf",
            "published": "2026-06-01T00:00:00Z",
        }
    ]
    component_metrics = {
        "e2": {"status": "passed"},
        "e3": {"status": "passed"},
        "e4": {"status": "passed"},
        "e5": {"status": "passed"},
    }

    result = run_end_to_end_report_baseline(
        submissions,
        arxiv,
        component_metrics,
        top_k=2,
    )

    report = result["openreview_reports"][0]
    assert report["paper_id"] == "paper-1"
    assert len(report["top_weaknesses"]) == 2
    assert all(item["evidence_ids"] for item in report["top_weaknesses"])
    assert report["decision"] == "not_applicable"
    assert result["systems"]["B1_structured_evidence_report"]["trace_coverage"] == 1.0
    assert result["unseen_demo"]["papers"] == 1
    assert result["unseen_demo"]["gold_metrics_reported"] is False


def test_e6_structured_report_improves_traceability_over_unstructured_baseline():
    submissions = [
        {
            "paper_id": "paper-1",
            "content": {"title": "Paper", "abstract": "Abstract"},
            "reviews": [
                {
                    "id": "review-1",
                    "content": {"weaknesses": "Missing baseline comparison."},
                }
            ],
        }
    ]

    result = run_end_to_end_report_baseline(
        submissions,
        [],
        {"e2": {}, "e3": {}, "e4": {}, "e5": {}},
        top_k=1,
    )

    baseline = result["systems"]["B0_unstructured_review_dump"]
    structured = result["systems"]["B1_structured_evidence_report"]
    assert structured["trace_coverage"] > baseline["trace_coverage"]
    assert structured["top_k_compliance"] == 1.0
