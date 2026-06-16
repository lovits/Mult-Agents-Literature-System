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


def test_e6_system_generated_candidates_are_leakage_free_and_traceable():
    submissions = [
        {
            "paper_id": "paper-1",
            "content": {
                "title": "Paper",
                "abstract": (
                    "We propose a retrieval augmented review system for scientific papers. "
                    "The method compares against baselines and includes an ablation study."
                ),
                "keywords": ["retrieval", "review", "agent"],
                "primary_area": "natural language processing",
            },
            "reviews": [
                {
                    "id": "review-1",
                    "content": {
                        "weaknesses": (
                            "The ablation study is limited. "
                            "The baseline comparison should be clearer."
                        )
                    },
                }
            ],
        }
    ]

    result = run_end_to_end_report_baseline(
        submissions,
        [],
        {"e2": {}, "e3": {}, "e4": {}, "e5": {}},
        top_k=3,
    )

    generated = result["systems"]["B2_system_generated_structured_report"]
    report = result["system_generated_reports"][0]
    assert generated["trace_coverage"] == 1.0
    assert generated["review_leakage_free"] is True
    assert generated["official_weakness_proxy_overlap@k"] > 0.0
    assert report["trace_policy"] == "paper_content_to_system_generated_topk"
    assert report["candidate_source"] == "system_deterministic_baseline_v1"
    assert all(item["source_review_id"] is None for item in report["top_weaknesses"])
    assert all(item["evidence_ids"] for item in report["top_weaknesses"])


def test_e6_cue_aware_candidates_improve_proxy_overlap_without_review_leakage():
    submissions = [
        {
            "paper_id": "paper-1",
            "content": {
                "title": "A Benchmark for LLM Judge Evaluation",
                "abstract": (
                    "We introduce a benchmark for evaluating large language models with automatic judges. "
                    "The benchmark includes prompts, model comparisons, and annotations."
                ),
                "keywords": ["benchmark", "LLM judge", "annotation"],
                "primary_area": "natural language processing",
            },
            "reviews": [
                {
                    "id": "review-1",
                    "content": {
                        "weaknesses": (
                            "The benchmark needs stronger human annotation details. "
                            "The LLM-as-a-judge evaluation should be validated against human judgment."
                        )
                    },
                }
            ],
        }
    ]

    result = run_end_to_end_report_baseline(
        submissions,
        [],
        {"e2": {}, "e3": {}, "e4": {}, "e5": {}},
        top_k=3,
    )

    b2 = result["systems"]["B2_system_generated_structured_report"]
    b3 = result["systems"]["B3_cue_aware_structured_report"]
    report = result["cue_aware_reports"][0]
    assert b3["trace_coverage"] == 1.0
    assert b3["review_leakage_free"] is True
    assert b3["official_weakness_proxy_overlap@k"] > b2["official_weakness_proxy_overlap@k"]
    assert report["candidate_source"] == "system_cue_aware_baseline_v2"
    assert any("human annotation" in item["weakness"].lower() for item in report["top_weaknesses"])
    assert all(item["source_review_id"] is None for item in report["top_weaknesses"])
