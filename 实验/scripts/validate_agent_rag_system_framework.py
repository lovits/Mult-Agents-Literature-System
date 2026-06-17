#!/usr/bin/env python
import json
from pathlib import Path

from evireview.system import AgentRAGReviewPipeline, ReviewPipelineRequest
from evireview.system.config import AgentRAGSystemConfig


RESULT_PATH = Path("../.omx/specs/autoresearch-agent-rag-system-framework/result.json")


def main() -> int:
    result = validate()
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


def validate() -> dict:
    pipeline = AgentRAGReviewPipeline(
        AgentRAGSystemConfig(max_candidates=6, top_k_weaknesses=3)
    )
    result = pipeline.run(ReviewPipelineRequest(submission=_sample_submission()))
    required_stages = {
        "paper_parse_index",
        "candidate_generation",
        "query_planning",
        "paper_rag",
        "literature_rag_boundary",
        "support_refutation_audit",
        "adjudication",
        "meta_reviewer_ranking",
        "report_assembly",
    }
    trace_checks = [
        bool(trace.evidence_bundle.paper_evidence)
        and trace.support.stance == "support"
        and trace.refutation.stance == "refutation"
        and trace.adjudication.decision in {"keep", "rewrite", "reject", "uncertain"}
        for trace in result.traces
    ]
    top_evidence_attached = all(item.evidence_ids for item in result.top_weaknesses)
    no_forbidden_routes = (
        not result.system_trace["frontend_included"]
        and not result.system_trace["paper_decision_produced"]
        and not result.system_trace["human_check_route"]
        and "accept" not in result.report.summary.lower()
    )
    passed = (
        required_stages.issubset(set(result.stages))
        and len(result.traces) >= 4
        and all(trace_checks)
        and len(result.top_weaknesses) == 3
        and top_evidence_attached
        and no_forbidden_routes
    )
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "backend Agent-RAG framework validates full non-frontend review chain",
        "artifact": {
            "paper_id": result.paper_id,
            "stage_count": len(result.stages),
            "candidate_traces": len(result.traces),
            "top_weaknesses": len(result.top_weaknesses),
            "paper_decision_produced": result.system_trace["paper_decision_produced"],
            "human_check_route": result.system_trace["human_check_route"],
        },
        "stages": result.stages,
    }


def _sample_submission() -> dict:
    return {
        "paper_id": "framework-paper-001",
        "content": {
            "title": "Agentic Retrieval for Evidence-Grounded Review Generation",
            "abstract": (
                "We propose an agentic retrieval system for paper review. The method "
                "uses retrieval, evidence audit, and ranking but reports limited "
                "ablation results."
            ),
            "keywords": ["agent", "retrieval", "paper review"],
            "primary_area": "natural language processing",
            "method": (
                "The system contains candidate generation, Paper-RAG, support and "
                "refutation agents, and an adjudicator. Algorithm 1 describes the "
                "review pipeline."
            ),
            "experiments": (
                "Table 2 reports the main comparison. The ablation removes the "
                "retriever component and shows a smaller score drop than expected."
            ),
            "ablation": (
                "Table 3: Retrieval module ablation across reviewer aspects. The "
                "paper does not include a separate literature retrieval ablation."
            ),
            "related_work": (
                "Prior work includes multi-agent review systems, retrieval-augmented "
                "generation, and evidence-based scientific claim verification."
            ),
            "appendix": (
                "Implementation details include a fixed random seed, prompt template, "
                "and deterministic lexical fallback."
            ),
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
