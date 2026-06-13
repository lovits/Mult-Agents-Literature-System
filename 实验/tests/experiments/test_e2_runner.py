import json

import pytest

from evireview.dao.peerqa import PeerQADataset
from evireview.dao.peerqa import PeerQAExample
from evireview.evaluation.e2_runner import _plan_question, run_e2


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


def test_e2_runner_records_formal_embedding_metadata():
    dataset = PeerQADataset(blocks_by_paper={}, examples=[])

    result = run_e2(
        dataset,
        limit=0,
        top_k=5,
        embedding_name="BAAI/bge-base-en-v1.5",
        embedding_metadata={"revision": "fixed-revision", "device": "cpu"},
        embed=lambda text: [1.0],
    )

    assert result["protocol"]["formal_result"] is True
    assert result["protocol"]["embedding_metadata"] == {
        "revision": "fixed-revision",
        "device": "cpu",
    }


def test_query_planner_only_applies_structure_priors_with_explicit_cues():
    generic = PeerQAExample(
        question_id="q1",
        paper_id="p1",
        question="What is the main contribution?",
        relevant_evidence_ids={"p1:1"},
    )
    ablation = generic.model_copy(
        update={"question": "What does Table 3 show in the ablation?"}
    )

    generic_plan = _plan_question(generic)
    ablation_plan = _plan_question(ablation)

    assert generic_plan.expected_sections == []
    assert generic_plan.expected_evidence_types == []
    assert ablation_plan.expected_sections == [
        "Experiments",
        "Results",
        "Ablation",
        "Appendix",
    ]
    assert ablation_plan.expected_evidence_types == ["table_caption"]


def test_formal_runner_warms_query_embedding_before_timing(tmp_path):
    papers = tmp_path / "papers.jsonl"
    qa = tmp_path / "qa.jsonl"
    papers.write_text(
        json.dumps(
            {
                "idx": 1,
                "type": "paragraph",
                "content": "Evidence",
                "last_heading": "Results",
                "paper_id": "p1",
            }
        ),
        encoding="utf-8",
    )
    qa.write_text(
        json.dumps(
            {
                "paper_id": "p1",
                "question_id": "q1",
                "question": "What is the result?",
                "answer_evidence_mapped": [{"idx": [1]}],
                "answerable_mapped": True,
            }
        ),
        encoding="utf-8",
    )
    dataset = PeerQADataset.from_jsonl(papers, qa)
    query_calls = []

    run_e2(
        dataset,
        limit=1,
        top_k=1,
        embedding_name="formal-test",
        embed=lambda text: [1.0],
        query_embed=lambda text: query_calls.append(text) or [1.0],
        embed_many=lambda texts: [[1.0] for _ in texts],
    )

    assert query_calls == ["What is the result?"] * 5
