from evireview.dao.literature import LiteratureCorpus


def test_literature_corpus_loads_markdown_metadata(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "01_MARG_Multi_Agent_Review_Generation_2024.md").write_text(
        "# MARG: Multi-Agent Review Generation for Scientific Papers\n\n"
        "This paper studies multi-agent review generation.",
        encoding="utf-8",
    )
    nested = source / "ReviewAgents_Bridging_the_Gap_Between_Human_and_AI_2503.08506"
    nested.mkdir()
    (nested / "ReviewAgents_Bridging_the_Gap_Between_Human_and_AI_2503.08506.md").write_text(
        "# ReviewAgents: Bridging the Gap Between Human and AI Paper Review\n\n"
        "The work introduces review chain-of-thought.",
        encoding="utf-8",
    )

    corpus = LiteratureCorpus.from_source_dir(source)

    assert corpus.audit_summary()["markdown_docs"] == 2
    assert corpus.documents[0].year == 2024
    assert corpus.documents[1].year == 2025
    assert all(document.title for document in corpus.documents)
    assert all(document.source_path.endswith(".md") for document in corpus.documents)


def test_literature_corpus_exports_blocks_for_retrieval(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "14_RAGChecker_Fine_grained_RAG_Evaluation_2024.md").write_text(
        "# RAGChecker: A Fine-grained Framework for Diagnosing RAG\n\n"
        "RAGChecker evaluates retrieval and generation for RAG systems.",
        encoding="utf-8",
    )

    corpus = LiteratureCorpus.from_source_dir(source)
    blocks = corpus.to_evidence_blocks()

    assert len(blocks) == 1
    assert blocks[0].paper_id.startswith("lit:")
    assert blocks[0].section == "literature"
    assert "RAGChecker" in blocks[0].text


def test_literature_corpus_uses_curated_year_hints_for_local_snapshot(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    nested = source / "14_SubstanReview_Automatic_Analysis_of_Substantiation"
    nested.mkdir()
    (nested / "14_SubstanReview_Automatic_Analysis_of_Substantiation.md").write_text(
        "# SubstanReview: Automatic Analysis of Substantiation in Peer Reviews\n\n"
        "This dataset studies substantiation in review comments.",
        encoding="utf-8",
    )

    corpus = LiteratureCorpus.from_source_dir(source)

    assert corpus.documents[0].year == 2023
    assert corpus.audit_summary()["metadata_complete_docs"] == 1
