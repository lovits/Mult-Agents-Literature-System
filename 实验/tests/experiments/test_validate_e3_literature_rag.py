import json

from scripts.validate_e3_literature_rag import validate


def test_validate_e3_literature_rag_accepts_controlled_baselines(tmp_path):
    metrics = {
        "protocol": {
            "name": "controlled-literature-rag-v1",
            "frozen_local_corpus": True,
            "online_retrieval": False,
            "metadata_year_filter": True,
        },
        "dataset": {
            "markdown_docs": 30,
            "metadata_complete_docs": 30,
            "source_path": str(tmp_path),
            "source_exists": True,
        },
        "queries": {"count": 6},
        "systems": {
            "L0_no_literature": {
                "recall@10": 0.0,
                "mrr": 0.0,
                "literature_relevance@10": 0.0,
                "citation_validity_rate": 0.0,
                "future_leakage_count": 0,
            },
            "L1_keyword": {
                "recall@10": 0.8,
                "mrr": 0.6,
                "literature_relevance@10": 0.5,
                "citation_validity_rate": 1.0,
                "future_leakage_count": 2,
            },
            "L2_hybrid": {
                "recall@10": 0.9,
                "mrr": 0.7,
                "literature_relevance@10": 0.6,
                "citation_validity_rate": 1.0,
                "future_leakage_count": 2,
            },
            "L3_hybrid_metadata_filter": {
                "recall@10": 0.9,
                "mrr": 0.7,
                "literature_relevance@10": 0.6,
                "citation_validity_rate": 1.0,
                "future_leakage_count": 0,
            },
        },
    }
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    result = validate(metrics_path)

    assert result["status"] == "passed"
    assert result["passed"] is True
    assert result["checks"]["baseline_improvement"]["passed"] is True
