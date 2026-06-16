from evireview.dao.substanreview import (
    SubstanClaim,
    SubstanEvidenceSpan,
    SubstanReviewDataset,
)
from evireview.evaluation.substanreview_baseline_runner import (
    run_substanreview_baselines,
)


def _claim(
    claim_id,
    split,
    review,
    claim_text,
    evidence_text=None,
):
    claim_start = review.index(claim_text)
    evidence = []
    if evidence_text:
        evidence_start = review.index(evidence_text)
        evidence = [
            SubstanEvidenceSpan(
                start=evidence_start,
                end=evidence_start + len(evidence_text),
                text=evidence_text,
            )
        ]
    return SubstanClaim(
        claim_id=claim_id,
        review_id=claim_id.split(":")[0],
        split=split,
        review=review,
        polarity="negative",
        claim_start=claim_start,
        claim_end=claim_start + len(claim_text),
        claim_text=claim_text,
        evidence_spans=evidence,
    )


def test_substanreview_baselines_tune_on_train_and_evaluate_test_only():
    supported_review = (
        "The experiment is weak because it has no baseline. More results are needed."
    )
    unsupported_review = "The writing is unclear. The paper studies retrieval."
    dataset = SubstanReviewDataset(
        review_counts={"train": 2, "test": 2},
        claims=[
            _claim(
                "train-1:0",
                "train",
                supported_review,
                "The experiment is weak",
                "because it has no baseline",
            ),
            _claim(
                "train-2:0",
                "train",
                unsupported_review,
                "The writing is unclear",
            ),
            _claim(
                "test-1:0",
                "test",
                supported_review,
                "The experiment is weak",
                "because it has no baseline",
            ),
            _claim(
                "test-2:0",
                "test",
                unsupported_review,
                "The writing is unclear",
            ),
        ],
    )

    result = run_substanreview_baselines(dataset)

    assert result["protocol"]["development_split"] == "train"
    assert result["protocol"]["evaluation_split"] == "test"
    assert result["protocol"]["gold_claim_spans"] is True
    assert result["protocol"]["weakness_validity_gold"] is False
    assert result["evaluation"]["claims"] == 2
    assert set(result["systems"]) == {
        "S0_proximity",
        "S1_lexical",
        "S2_hybrid",
    }
    assert result["systems"]["S2_hybrid"]["supported_f1"] > 0
    assert len(result["sample_results"]) == 2


def test_substanreview_baselines_report_gold_auxiliary_metrics():
    review = "The method is weak because no ablation is reported."
    dataset = SubstanReviewDataset(
        review_counts={"train": 1, "test": 1},
        claims=[
            _claim(
                "train-1:0",
                "train",
                review,
                "The method is weak",
                "because no ablation is reported",
            ),
            _claim(
                "test-1:0",
                "test",
                review,
                "The method is weak",
                "because no ablation is reported",
            ),
        ],
    )

    result = run_substanreview_baselines(dataset)

    assert result["evaluation"]["claim_evidence_coverage"] == 1.0
    assert result["evaluation"]["substantiated_claim_rate"] == 1.0
    assert result["evaluation"]["mean_substan_score"] > 0
    assert result["systems"]["S0_proximity"]["evidence_hit@1"] == 1.0
