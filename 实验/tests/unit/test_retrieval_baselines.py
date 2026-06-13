from evireview.models.evidence import EvidenceBlock
from evireview.rag.bm25 import BM25Retriever
from evireview.rag.dense import DenseRetriever
from evireview.rag.fusion import reciprocal_rank_fusion
from evireview.rag.index_store import IndexIdentity


BLOCKS = [
    EvidenceBlock(
        block_id="b1",
        paper_id="p1",
        section="method",
        evidence_type="paragraph",
        text="The retriever combines sparse and dense scores.",
        ordinal=0,
    ),
    EvidenceBlock(
        block_id="b2",
        paper_id="p1",
        section="experiments",
        evidence_type="paragraph",
        text="We report an ablation of the retrieval module.",
        ordinal=1,
    ),
    EvidenceBlock(
        block_id="b3",
        paper_id="p1",
        section="introduction",
        evidence_type="paragraph",
        text="Large language models review scientific papers.",
        ordinal=2,
    ),
]


def test_bm25_retrieves_exact_ablation_evidence():
    results = BM25Retriever(BLOCKS).retrieve("retrieval ablation", top_k=2)

    assert results[0].evidence_id == "b2"
    assert results[0].source == "paper"


def test_dense_retriever_uses_injected_embeddings():
    vectors = {
        BLOCKS[0].text: [1.0, 0.0],
        BLOCKS[1].text: [0.8, 0.2],
        BLOCKS[2].text: [0.0, 1.0],
        "method retrieval": [1.0, 0.0],
    }
    results = DenseRetriever(BLOCKS, embed=lambda text: vectors[text]).retrieve(
        "method retrieval",
        top_k=2,
    )

    assert [result.evidence_id for result in results] == ["b1", "b2"]


def test_rrf_rewards_items_retrieved_by_both_methods():
    fused = reciprocal_rank_fusion([["b1", "b2"], ["b2", "b3"]], k=60)

    assert fused[0].item_id == "b2"


def test_index_identity_changes_when_blocks_change():
    original = IndexIdentity.from_blocks("p1", "markdown-v1", "embed-v1", BLOCKS)
    changed = IndexIdentity.from_blocks("p1", "markdown-v1", "embed-v1", BLOCKS[:2])

    assert original.cache_key != changed.cache_key
