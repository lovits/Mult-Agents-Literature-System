import yaml

from scripts.run_e3_literature_rag import run


def test_run_e3_literature_rag_writes_metrics_and_report(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "14_RAGChecker_Fine_grained_RAG_Evaluation_2024.md").write_text(
        "# RAGChecker: A Fine-grained Framework for Diagnosing RAG\n\n"
        "RAGChecker evaluates retrieval and generation in RAG systems.",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    output = tmp_path / "metrics.json"
    report = tmp_path / "report.md"
    config.write_text(
        yaml.safe_dump(
            {
                "dataset": {"path": str(source)},
                "queries": [
                    {
                        "query_id": "q_ragchecker",
                        "query": "fine grained rag evaluation ragchecker",
                        "aspect": "rag_evaluation",
                        "as_of_year": 2024,
                        "gold_title_keywords": ["RAGChecker"],
                    }
                ],
                "top_k": 3,
                "output": str(output),
                "report": str(report),
            }
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert report.exists()
    assert result["systems"]["L3_hybrid_metadata_filter"]["recall@10"] == 1.0
    assert "Controlled Literature-RAG" in report.read_text(encoding="utf-8")
