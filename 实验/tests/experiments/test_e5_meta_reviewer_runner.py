from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.meta_reviewer_runner import run_meta_reviewer_baselines


def _example(example_id, paper_id, weakness, agreement=5):
    return ClaimCheckWeakness(
        example_id=example_id,
        paper_review_id=paper_id,
        split="main",
        weakness=weakness,
        groundedness_confidence=agreement,
        target_claims=[],
        paper_texts=["paper text"],
        relevant_text_ids=set(),
        subjectivity=2,
        agreement=agreement,
        weakness_types=set(),
    )


def test_meta_reviewer_prefers_evidence_backed_keep_items_and_deduplicates():
    dataset = ClaimCheckDataset(
        paper_review_pairs=1,
        examples=[
            _example(
                "main:p1:0",
                "p1",
                "The paper lacks ablation experiments for the retrieval module.",
                agreement=5,
            ),
            _example(
                "main:p1:1",
                "p1",
                "The paper lacks ablation experiments for the retriever component.",
                agreement=5,
            ),
            _example(
                "main:p1:2",
                "p1",
                "The presentation is somewhat verbose.",
                agreement=2,
            ),
        ],
    )
    audit = {
        "protocol": {"name": "e4-audit-protocol-smoke-v1"},
        "traces": [
            {
                "example_id": "main:p1:0",
                "support": {"strength": 0.9},
                "refutation": {"strength": 0.1},
                "A4_heuristic_smoke": {
                    "decision": "keep",
                    "confidence": 0.8,
                    "evidence_ids": ["p1:1", "p1:2"],
                },
            },
            {
                "example_id": "main:p1:1",
                "support": {"strength": 0.7},
                "refutation": {"strength": 0.2},
                "A4_heuristic_smoke": {
                    "decision": "keep",
                    "confidence": 0.7,
                    "evidence_ids": ["p1:1"],
                },
            },
            {
                "example_id": "main:p1:2",
                "support": {"strength": 0.1},
                "refutation": {"strength": 0.7},
                "A4_heuristic_smoke": {
                    "decision": "reject",
                    "confidence": 0.8,
                    "evidence_ids": ["p1:3"],
                },
            },
        ],
    }
    substanreview = {
        "evaluation": {"substantiated_claim_rate": 0.42},
        "protocol": {"covered_refuted_gold": False},
    }
    literature = {
        "systems": {
            "L3_hybrid_metadata_filter": {
                "citation_validity_rate": 1.0,
                "future_leakage_count": 0,
            }
        }
    }

    result = run_meta_reviewer_baselines(
        dataset,
        audit,
        substanreview,
        literature,
        top_k=2,
    )

    systems = result["systems"]
    assert systems["R3_evidence_aware"]["top_k_agreement_precision"] == 1.0
    assert (
        systems["R2_text_dedup"]["redundancy_rate"]
        <= systems["R1_text_severity"]["redundancy_rate"]
    )
    selected = result["sample_rankings"]["R3_evidence_aware"]["p1"][:2]
    assert selected[0]["candidate_id"] == "main:p1:0"


def test_meta_reviewer_reports_boundary_metadata():
    dataset = ClaimCheckDataset(
        paper_review_pairs=1,
        examples=[_example("main:p1:0", "p1", "Missing baseline comparison.", 5)],
    )
    result = run_meta_reviewer_baselines(
        dataset,
        {"traces": []},
        {"evaluation": {"substantiated_claim_rate": 0.4}, "protocol": {"covered_refuted_gold": False}},
        {
            "systems": {
                "L3_hybrid_metadata_filter": {
                    "citation_validity_rate": 1.0,
                    "future_leakage_count": 0,
                }
            }
        },
    )

    assert result["protocol"]["covered_refuted_gold"] is False
    assert result["protocol"]["gold_used_only_for_metrics"] is True
    assert result["dataset"]["evaluated_candidates"] == 1
