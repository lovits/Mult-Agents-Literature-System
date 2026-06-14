from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.e4_audit_smoke_runner import run_e4_audit_protocol_smoke


def _example(example_id: str, agreement: int) -> ClaimCheckWeakness:
    return ClaimCheckWeakness(
        example_id=example_id,
        split="main",
        paper_review_id="paper-1",
        weakness="The retrieval component lacks an ablation.",
        groundedness_confidence=4,
        target_claims=["We report an ablation."],
        paper_texts=[
            "We report an ablation of the retrieval component.",
            "The model uses a retriever.",
        ],
        relevant_text_ids={"paper-1:0"},
        subjectivity=2,
        agreement=agreement,
        weakness_types={"insufficient"},
    )


def test_audit_protocol_smoke_preserves_every_candidate_and_trace():
    dataset = ClaimCheckDataset(
        examples=[_example("main:1", 5), _example("main:2", 2)],
        paper_review_pairs=1,
    )

    result = run_e4_audit_protocol_smoke(dataset)

    assert result["protocol"]["formal_a0_a4_result"] is False
    assert result["evaluated"] == 2
    assert len(result["traces"]) == 2
    assert result["integrity"]["invalid_citations"] == 0
    assert result["integrity"]["missing_bidirectional_cases"] == 0
    assert result["integrity"]["human_check_decisions"] == 0
    assert set(result["systems"]) == {"A3_heuristic_smoke", "A4_heuristic_smoke"}
