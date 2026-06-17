import json

from evireview.evaluation.end_to_end_report_runner import _balanced_agent_rag_top_items
from evireview.evaluation.e6_neurips_stability import (
    extract_weakness_proxy,
    load_neurips_submissions,
    run_neurips_stability_experiment,
)
from evireview.models.audit import AdjudicationResult, AuditCase
from evireview.models.evidence import EvidenceBlock
from evireview.models.paper import PaperDocument
from evireview.models.weakness import CandidateWeakness


def test_extract_weakness_proxy_prefers_weakness_sentences():
    text = (
        "The paper is well written. "
        "However, the ablation study is limited. "
        "The authors should compare against stronger baselines."
    )

    proxy = extract_weakness_proxy(text)

    assert "ablation" in proxy.lower()
    assert "baselines" in proxy.lower()
    assert "well written" not in proxy.lower()


def test_load_neurips_submissions_from_processed_snapshot(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    paper = PaperDocument(
        paper_id="p1",
        title="Paper One",
        source_path="https://openreview.net/pdf?id=p1",
        sections=["abstract", "experiments"],
        blocks=[
            EvidenceBlock(
                block_id="p1:b0",
                paper_id="p1",
                section="abstract",
                evidence_type="paragraph",
                text="We study an agent RAG benchmark.",
                ordinal=0,
            ),
            EvidenceBlock(
                block_id="p1:b1",
                paper_id="p1",
                section="experiments",
                evidence_type="paragraph",
                text="Experiments compare baselines.",
                ordinal=1,
            ),
        ],
        metadata={"conference": "NeurIPS 2023", "keywords": ["agent", "rag"]},
    )
    (processed / "neurips_2023_sample_papers.jsonl").write_text(
        json.dumps(paper.model_dump(), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (processed / "neurips_2023_review_pool.jsonl").write_text(
        json.dumps(
            {
                "paper_id": "p1",
                "review_index": 0,
                "text": "The paper should include stronger ablations.",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    submissions = load_neurips_submissions(processed)

    assert submissions[0]["paper_id"] == "p1"
    assert submissions[0]["content"]["abstract"]
    assert submissions[0]["reviews"][0]["content"]["weaknesses"]


def test_run_neurips_stability_experiment_with_small_snapshot(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    for index in range(2):
        paper = PaperDocument(
            paper_id=f"p{index}",
            title=f"Paper {index}",
            source_path="",
            sections=["abstract", "method", "experiments", "related_work"],
            blocks=[
                EvidenceBlock(
                    block_id=f"p{index}:b0",
                    paper_id=f"p{index}",
                    section="abstract",
                    evidence_type="paragraph",
                    text="We propose an agentic retrieval benchmark with baselines and ablations.",
                    ordinal=0,
                ),
                EvidenceBlock(
                    block_id=f"p{index}:b1",
                    paper_id=f"p{index}",
                    section="method",
                    evidence_type="paragraph",
                    text="The method uses retrieval planning and adjudication.",
                    ordinal=1,
                ),
                EvidenceBlock(
                    block_id=f"p{index}:b2",
                    paper_id=f"p{index}",
                    section="experiments",
                    evidence_type="paragraph",
                    text="Experiments compare baselines and ablations.",
                    ordinal=2,
                ),
                EvidenceBlock(
                    block_id=f"p{index}:b3",
                    paper_id=f"p{index}",
                    section="related_work",
                    evidence_type="paragraph",
                    text="Related work includes RAG and automatic review.",
                    ordinal=3,
                ),
            ],
            metadata={"conference": "NeurIPS 2023", "keywords": ["agent", "retrieval"]},
        )
        with (processed / "neurips_2023_sample_papers.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(paper.model_dump(), ensure_ascii=False) + "\n")
        with (processed / "neurips_2023_review_pool.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "paper_id": f"p{index}",
                        "review_index": 0,
                        "text": "The ablation is limited and the baseline comparison should be stronger.",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    result = run_neurips_stability_experiment(processed, sample_size=2, top_k=2)

    assert result["protocol"]["name"] == "e6-neurips-2023-stability-v1"
    assert result["dataset"]["papers"] == 2
    assert result["systems"]["B5_balanced_agent_rag_pipeline_report"]["trace_coverage"] == 1.0


def test_balanced_selector_skips_ranker_filtered_rejects():
    traces = [
        _trace("p1:c0", "method", "reject"),
        _trace("p1:c1", "experiment", "keep"),
    ]

    items = _balanced_agent_rag_top_items(traces, top_k=2)

    assert len(items) == 1
    assert items[0]["candidate_id"] == "p1:c1"
    assert items[0]["audit_decision"] == "keep"


def _trace(candidate_id: str, aspect: str, decision: str):
    candidate = CandidateWeakness(
        candidate_id=candidate_id,
        paper_id="p1",
        aspect=aspect,
        target="experiments",
        weakness="The experiment lacks a clear ablation for retrieval components.",
        severity="major",
        suggestion="Add an ablation that removes the retrieval planner.",
        source_agent="test-agent",
    )
    return type(
        "Trace",
        (),
        {
            "candidate": candidate,
            "support": AuditCase(
                candidate_id=candidate_id,
                stance="support",
                claim=candidate.weakness,
                evidence_ids=["p1:b1"],
                strength=0.8,
                rationale="The evidence mentions no ablation.",
            ),
            "refutation": AuditCase(
                candidate_id=candidate_id,
                stance="refutation",
                claim=candidate.weakness,
                evidence_ids=[],
                strength=0.1,
                rationale="No refuting evidence.",
            ),
            "adjudication": AdjudicationResult(
                candidate_id=candidate_id,
                decision=decision,
                confidence=0.8,
                evidence_ids=["p1:b1"] if decision != "reject" else [],
                reason="Synthetic regression trace.",
            ),
            "metadata": {"candidate_rank_score": 0.5},
        },
    )()
