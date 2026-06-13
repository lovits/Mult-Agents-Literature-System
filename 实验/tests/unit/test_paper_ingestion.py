from evireview.service.paper_ingestion_service import PaperIngestionService


def test_markdown_ingestion_preserves_structure_and_evidence_types():
    paper = PaperIngestionService().from_markdown("tests/fixtures/paper_sample.md", "p1")

    kinds = {block.evidence_type for block in paper.blocks}
    assert {"paragraph", "algorithm", "table_caption", "appendix"} <= kinds
    assert {"introduction", "method", "experiments", "appendix"} <= set(paper.sections)
    assert all(block.section for block in paper.blocks)


def test_markdown_ingestion_produces_stable_block_ids():
    service = PaperIngestionService()

    first = service.from_markdown("tests/fixtures/paper_sample.md", "p1")
    second = service.from_markdown("tests/fixtures/paper_sample.md", "p1")

    assert [block.block_id for block in first.blocks] == [block.block_id for block in second.blocks]
