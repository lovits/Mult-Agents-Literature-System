import json

from evireview.dao.substanreview import SubstanReviewDataset


def test_substanreview_adapter_links_claims_to_matching_evidence_spans(tmp_path):
    review = "The method is strong because accuracy improves. The writing is clear."
    claim_start = review.index("The method is strong")
    evidence_start = review.index("because accuracy improves")
    major_start = review.index("The writing is clear")
    row = {
        "id": 7,
        "review": review,
        "label": [
            [claim_start, claim_start + len("The method is strong"), "Eval_pos_1"],
            [
                evidence_start,
                evidence_start + len("because accuracy improves"),
                "Jus_pos_1",
            ],
            [major_start, major_start + len("The writing is clear"), "Major_claim"],
        ],
    }
    (tmp_path / "train.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (tmp_path / "test.jsonl").write_text("", encoding="utf-8")

    dataset = SubstanReviewDataset.from_source_dir(tmp_path)

    assert len(dataset.claims) == 2
    linked = dataset.claims[0]
    assert linked.split == "train"
    assert linked.polarity == "positive"
    assert linked.claim_text == "The method is strong"
    assert [span.text for span in linked.evidence_spans] == [
        "because accuracy improves"
    ]
    assert dataset.claims[1].polarity == "major"
    assert dataset.claims[1].evidence_spans == []


def test_substanreview_real_data_preserves_auxiliary_evaluation_boundary():
    dataset = SubstanReviewDataset.from_source_dir(
        "dataset/raw/evaluation/substanreview"
    )
    summary = dataset.audit_summary()

    assert summary["reviews"] == 550
    assert summary["train_reviews"] == 440
    assert summary["test_reviews"] == 110
    assert summary["claims"] == 2940
    assert summary["supports"]["claim_evidence_substantiation"] is True
    assert summary["supports"]["weakness_validity"] is False
    assert summary["supports"]["covered_refuted_gold"] is False
