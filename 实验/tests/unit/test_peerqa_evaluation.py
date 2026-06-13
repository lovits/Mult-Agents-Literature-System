import json

from evireview.dao.peerqa import PeerQADataset
from evireview.evaluation.retrieval_metrics import evaluate_ranking


def test_peerqa_adapter_maps_gold_sentence_indexes_to_evidence_ids(tmp_path):
    papers = tmp_path / "papers.jsonl"
    qa = tmp_path / "qa.jsonl"
    papers.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "idx": 10,
                        "type": "heading",
                        "content": "Experiments",
                        "last_heading": None,
                        "paper_id": "paper-1",
                    }
                ),
                json.dumps(
                    {
                        "idx": 11,
                        "type": "paragraph",
                        "content": "The ablation removes retrieval.",
                        "last_heading": "Experiments",
                        "paper_id": "paper-1",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    qa.write_text(
        json.dumps(
            {
                "paper_id": "paper-1",
                "question_id": "q-1",
                "question": "Was retrieval ablated?",
                "answer_evidence_mapped": [{"sentence": "yes", "idx": [11]}],
                "answerable": True,
                "answerable_mapped": True,
            }
        ),
        encoding="utf-8",
    )

    dataset = PeerQADataset.from_jsonl(papers, qa)
    example = dataset.examples[0]

    assert example.relevant_evidence_ids == {"paper-1:11"}
    assert dataset.blocks_by_paper["paper-1"][1].section == "Experiments"


def test_retrieval_metrics_match_hand_calculation():
    metrics = evaluate_ranking(
        ranked_ids=["d1", "d2", "d3", "d4"],
        relevant_ids={"d2", "d4"},
        cutoffs=(1, 3, 5),
    )

    assert metrics["recall@1"] == 0.0
    assert metrics["recall@3"] == 0.5
    assert metrics["recall@5"] == 1.0
    assert metrics["mrr"] == 0.5
    assert round(metrics["ndcg@3"], 6) == 0.386853
