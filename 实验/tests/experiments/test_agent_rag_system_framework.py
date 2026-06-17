import json

from scripts.validate_agent_rag_system_framework import validate
from evireview.system import AgentRAGReviewPipeline, ReviewPipelineRequest
from evireview.system.config import AgentRAGSystemConfig


def _submission():
    return {
        "paper_id": "p-framework",
        "content": {
            "title": "A Multi-Agent RAG Review System",
            "abstract": "We evaluate retrieval agents, evidence audit, and ranking.",
            "keywords": ["agent", "rag", "review"],
            "method": "The method uses a planner, retriever, support agent, refutation agent, and adjudicator.",
            "experiments": "Table 1 reports main results with baseline comparison.",
            "ablation": "Table 2 reports retriever and ranker ablation.",
            "related_work": "Related work discusses automatic review and evidence-grounded RAG.",
            "appendix": "Implementation details list seed, prompt, and hyperparameters.",
        },
    }


def test_agent_rag_pipeline_runs_full_backend_chain():
    pipeline = AgentRAGReviewPipeline(
        AgentRAGSystemConfig(max_candidates=6, top_k_weaknesses=3)
    )

    result = pipeline.run(ReviewPipelineRequest(submission=_submission()))

    assert "candidate_generation" in result.stages
    assert "paper_rag" in result.stages
    assert "support_refutation_audit" in result.stages
    assert "meta_reviewer_ranking" in result.stages
    assert len(result.traces) == 6
    assert len(result.top_weaknesses) == 3
    assert all(trace.evidence_bundle.paper_evidence for trace in result.traces)
    assert all(item.evidence_ids for item in result.top_weaknesses)
    assert result.system_trace["paper_decision_produced"] is False
    assert result.system_trace["human_check_route"] is False


def test_pipeline_result_is_json_serializable():
    pipeline = AgentRAGReviewPipeline(AgentRAGSystemConfig(max_candidates=4))
    result = pipeline.run(ReviewPipelineRequest(submission=_submission()))

    payload = json.loads(result.model_dump_json())

    assert payload["paper_id"] == "p-framework"
    assert payload["report"]["top_weaknesses"]


def test_system_framework_autoresearch_validator_passes():
    result = validate()

    assert result["passed"] is True
    assert result["artifact"]["paper_decision_produced"] is False
    assert result["artifact"]["human_check_route"] is False
