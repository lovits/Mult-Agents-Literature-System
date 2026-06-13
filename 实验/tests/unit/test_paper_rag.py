from evireview.models.evidence import EvidenceBlock
from evireview.models.weakness import QueryPlan
from evireview.rag.paper_rag import PaperRAG, PaperRAGConfig
from evireview.rag.priors import apply_structure_priors, expand_neighbors


BLOCKS = [
    EvidenceBlock(
        block_id="intro",
        paper_id="p1",
        section="introduction",
        evidence_type="paragraph",
        text="We introduce a retrieval module.",
        ordinal=0,
    ),
    EvidenceBlock(
        block_id="experiment",
        paper_id="p1",
        section="experiments",
        evidence_type="paragraph",
        text="We compare retrieval results.",
        ordinal=1,
    ),
    EvidenceBlock(
        block_id="ablation",
        paper_id="p1",
        section="ablation",
        evidence_type="table_caption",
        text="Table 3: Retrieval module ablation.",
        ordinal=2,
    ),
    EvidenceBlock(
        block_id="appendix",
        paper_id="p1",
        section="appendix",
        evidence_type="appendix",
        text="Additional implementation details.",
        ordinal=3,
    ),
]


PLAN = QueryPlan(
    candidate_id="w1",
    aspect="experiment",
    keyword_queries=["retrieval module ablation"],
    semantic_query="retrieval module ablation",
    expected_sections=["experiments", "ablation"],
    expected_evidence_types=["table_caption"],
    literature_required=False,
)


def test_experiment_query_promotes_ablation_table():
    ranked = apply_structure_priors(
        expected_sections=PLAN.expected_sections,
        expected_types=PLAN.expected_evidence_types,
        candidates=[
            {"id": "intro", "section": "introduction", "type": "paragraph", "score": 0.8},
            {"id": "ablation", "section": "ablation", "type": "table_caption", "score": 0.7},
        ],
        section_weight=0.1,
        evidence_type_weight=0.1,
    )

    assert ranked[0]["id"] == "ablation"


def test_neighbor_expansion_never_crosses_section_boundaries():
    expanded = expand_neighbors(BLOCKS, seed_ids=["ablation"], radius=1)

    assert [block.block_id for block in expanded] == ["ablation"]


def test_paper_rag_modes_are_component_ablatable():
    vectors = {
        block.text: [1.0, float(block.ordinal)] for block in BLOCKS
    } | {PLAN.semantic_query: [1.0, 0.0]}
    rag = PaperRAG(BLOCKS, embed=lambda text: vectors[text])

    p2 = rag.retrieve(PLAN, PaperRAGConfig(mode="P2", top_k=3))
    p3 = rag.retrieve(PLAN, PaperRAGConfig(mode="P3", top_k=3))
    p4 = rag.retrieve(PLAN, PaperRAGConfig(mode="P4", top_k=3))

    assert p2.trace["section_prior"] is False
    assert p3.trace["section_prior"] is True
    assert p3.trace["evidence_type_prior"] is False
    assert p4.trace["evidence_type_prior"] is True
    assert p4.trace["neighbor_expansion"] is True
    assert p4.items[0].evidence_id == "ablation"
