import json

from evireview.dao.claimcheck import ClaimCheckDataset


def test_claimcheck_adapter_preserves_ordinal_and_multilabel_annotations(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    payload = {
        "paper-review-1": {
            "response": {
                "Weakness associated with claims": [
                    {
                        "Weakness span": "The evidence is insufficient.",
                        "Weakness confidence score": 4,
                        "Target claims": ["Claim1: The method is superior."],
                        "Weakness Annotation": {
                            "subjectivity": 2,
                            "agreement": 5,
                            "weakness_type": {
                                "insufficient": True,
                                "contradictory": True,
                                "novelty": False,
                                "clarity": False,
                                "related_work": False,
                                "other": False,
                            },
                        },
                    }
                ]
            },
            "meta": {"title": "Paper", "claims": ["Claim1: The method is superior."]},
        }
    }
    (source / "main.json").write_text(json.dumps(payload), encoding="utf-8")
    (source / "pilot.json").write_text("{}", encoding="utf-8")

    dataset = ClaimCheckDataset.from_source_dir(source)
    example = dataset.examples[0]

    assert example.split == "main"
    assert example.groundedness_confidence == 4
    assert example.agreement == 5
    assert example.subjectivity == 2
    assert example.weakness_types == {"insufficient", "contradictory"}
    assert example.target_claims == ["Claim1: The method is superior."]


def test_claimcheck_real_data_exposes_supported_tasks_and_missing_gold_boundary():
    dataset = ClaimCheckDataset.from_source_dir(
        "dataset/raw/evaluation/claimcheck/texts/source"
    )
    summary = dataset.audit_summary()

    assert summary["paper_review_pairs"] == 60
    assert summary["weaknesses"] == 168
    assert summary["main_weaknesses"] == 155
    assert summary["pilot_weaknesses"] == 13
    assert summary["target_claim_grounded_weaknesses"] == 120
    assert summary["supports"]["claim_association"] is True
    assert summary["supports"]["weakness_labeling"] is True
    assert summary["supports"]["covered_refuted_gold"] is False
