from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.e4_baseline_runner import run_e4_baselines


def _example(
    example_id,
    split,
    weakness,
    relevant,
    *,
    groundedness=3,
    agreement=4,
    subjectivity=2,
    weakness_types=None,
):
    return ClaimCheckWeakness(
        example_id=example_id,
        paper_review_id="paper-1",
        split=split,
        weakness=weakness,
        groundedness_confidence=groundedness,
        target_claims=["gold"] if relevant else [],
        paper_texts=["irrelevant", "retrieval improves recall"],
        relevant_text_ids=relevant,
        exclusion_reason=None if relevant else "no_target_claim",
        subjectivity=subjectivity,
        agreement=agreement,
        weakness_types=weakness_types or {"insufficient"},
    )


def test_e4_baselines_fit_label_prior_on_pilot_and_evaluate_main_only():
    dataset = ClaimCheckDataset(
        paper_review_pairs=2,
        examples=[
            _example("pilot:1", "pilot", "pilot weakness", {"paper-1:1"}, agreement=5),
            _example("main:1", "main", "retrieval recall issue", {"paper-1:1"}, agreement=2),
        ],
    )

    result = run_e4_baselines(
        dataset,
        embed_document=lambda text: [1.0, 0.0] if "retrieval" in text else [0.0, 1.0],
        embed_query=lambda text: [1.0, 0.0],
    )

    assert result["protocol"]["development_split"] == "pilot"
    assert result["protocol"]["evaluation_split"] == "main"
    assert result["association"]["evaluated"] == 1
    assert result["association"]["systems"]["C1_bm25"]["recall@1"] == 1.0
    assert result["association"]["systems"]["C2_dense"]["recall@1"] == 1.0
    assert result["association"]["systems"]["C3_hybrid"]["recall@1"] == 1.0
    assert result["association"]["sample_results"][0]["example_id"] == "main:1"
    assert result["association"]["sample_results"][0]["gold_ids"] == ["paper-1:1"]
    assert result["labeling"]["W0_pilot_prior"]["agreement_mae"] == 3.0
    assert result["labeling"]["W0_pilot_prior"]["cost_per_candidate"] == 0.0


def test_e4_baselines_report_excluded_unmapped_examples():
    dataset = ClaimCheckDataset(
        paper_review_pairs=1,
        examples=[_example("main:1", "main", "no claim", set())],
    )

    result = run_e4_baselines(dataset)

    assert result["association"]["evaluated"] == 0
    assert result["association"]["excluded_with_reason"] == {"no_target_claim": 1}
    assert result["association"]["excluded_examples"] == [
        {"example_id": "main:1", "reason": "no_target_claim"}
    ]
