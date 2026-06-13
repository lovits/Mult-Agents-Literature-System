import json

import pytest

from evireview.dao.peerqa import PeerQADataset
from evireview.evaluation.e2_runner import run_e2


def test_e2_runner_reports_all_systems_and_marks_hashing_as_smoke(tmp_path):
    papers = tmp_path / "papers.jsonl"
    qa = tmp_path / "qa.jsonl"
    papers.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "idx": 0,
                        "type": "heading",
                        "content": "Experiments",
                        "last_heading": None,
                        "paper_id": "p1",
                    }
                ),
                json.dumps(
                    {
                        "idx": 1,
                        "type": "paragraph",
                        "content": "The retrieval ablation improves recall.",
                        "last_heading": "Experiments",
                        "paper_id": "p1",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    qa.write_text(
        json.dumps(
            {
                "paper_id": "p1",
                "question_id": "q1",
                "question": "What does the retrieval ablation improve?",
                "answer_evidence_mapped": [{"sentence": "answer", "idx": [1]}],
                "answerable_mapped": True,
            }
        ),
        encoding="utf-8",
    )
    dataset = PeerQADataset.from_jsonl(papers, qa)

    result = run_e2(dataset, limit=1, top_k=2, embedding_name="hashing-smoke")

    assert set(result["systems"]) == {"P0", "P1", "P2", "P3", "P4"}
    assert result["protocol"]["formal_result"] is False
    assert result["protocol"]["embedding"] == "hashing-smoke"
    assert result["samples"] == 1
    assert result["systems"]["P0"]["recall@5"] == 1.0


def test_e2_runner_never_labels_hashing_vectors_as_a_formal_embedding(tmp_path):
    dataset = PeerQADataset(blocks_by_paper={}, examples=[])

    with pytest.raises(ValueError, match="explicit embed callable"):
        run_e2(dataset, limit=0, top_k=5, embedding_name="BAAI/bge-base-en-v1.5")
