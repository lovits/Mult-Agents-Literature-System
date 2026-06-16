from evireview.dao.literature import LiteratureCorpus
from evireview.evaluation.literature_rag_runner import (
    LiteratureQuery,
    run_literature_rag_baselines,
)


def _write_doc(source, name, title, body):
    path = source / name
    path.write_text(f"# {title}\n\n{body}", encoding="utf-8")
    return path


def test_literature_rag_baselines_compare_against_no_retrieval(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    _write_doc(
        source,
        "01_MARG_Multi_Agent_Review_Generation_2024.md",
        "MARG: Multi-Agent Review Generation for Scientific Papers",
        "Multi-agent review generation improves feedback specificity.",
    )
    _write_doc(
        source,
        "14_RAGChecker_Fine_grained_RAG_Evaluation_2024.md",
        "RAGChecker: A Fine-grained Framework for Diagnosing RAG",
        "RAGChecker diagnoses retrieval and generation in RAG systems.",
    )

    corpus = LiteratureCorpus.from_source_dir(source)
    result = run_literature_rag_baselines(
        corpus,
        queries=[
            LiteratureQuery(
                query_id="q_marg",
                query="multi agent review generation scientific papers",
                aspect="review_generation",
                as_of_year=2024,
                gold_doc_ids=[corpus.find_by_title_keyword("MARG").doc_id],
            )
        ],
        top_k=2,
    )

    assert result["systems"]["L0_no_literature"]["recall@10"] == 0.0
    assert result["systems"]["L1_keyword"]["recall@10"] == 1.0
    assert result["systems"]["L2_hybrid"]["citation_validity_rate"] == 1.0
    assert result["systems"]["L3_hybrid_metadata_filter"]["recall@10"] == 1.0


def test_metadata_filter_removes_future_literature_leakage(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    _write_doc(
        source,
        "09_Can_LLMs_Provide_Useful_Feedback_2024.md",
        "Can LLMs Provide Useful Feedback on Research Papers?",
        "This work evaluates useful feedback for research papers.",
    )
    _write_doc(
        source,
        "17_ReviewGrounder_arXiv_2026.md",
        "ReviewGrounder: Rubric-Guided Tool-Integrated Agents",
        "ReviewGrounder provides grounded evidence for useful feedback.",
    )

    corpus = LiteratureCorpus.from_source_dir(source)
    result = run_literature_rag_baselines(
        corpus,
        queries=[
            LiteratureQuery(
                query_id="q_feedback",
                query="useful feedback research papers grounded review",
                aspect="feedback_quality",
                as_of_year=2024,
                gold_doc_ids=[
                    corpus.find_by_title_keyword("Useful Feedback").doc_id
                ],
            )
        ],
        top_k=2,
    )

    hybrid_leakage = result["systems"]["L2_hybrid"]["future_leakage_count"]
    filtered_leakage = result["systems"]["L3_hybrid_metadata_filter"][
        "future_leakage_count"
    ]
    assert hybrid_leakage > filtered_leakage
    assert filtered_leakage == 0
