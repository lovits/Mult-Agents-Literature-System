from __future__ import annotations

import unittest
from pathlib import Path

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.generation.structured_reviewer import StructuredReviewerGenerator
from evireview_core.io.jsonl import read_jsonl
from evireview_core.providers.base import ProviderGeneration
from evireview_core.workflow.deterministic import run_deterministic_review_audit
from evireview_core.workflow.graph import ReviewAuditGraph
from evireview_core.workflow.components import DEFAULT_COMPONENT_REGISTRY
from evireview_core.workflow.registry import DEFAULT_GRAPH_REGISTRY
from evireview_core.workflow.state import ReviewAuditState, WeaknessGenerationResult


class DeterministicWorkflowTest(unittest.TestCase):
    def test_graph_executes_explicit_retrieval_verification_and_ranking_nodes(self) -> None:
        state = ReviewAuditState(
            weaknesses=[Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")],
            evidence_blocks=[
                EvidenceBlock("b1", "p1", "Experiments", "experiment", "The ablation baseline removes the reranker.")
            ],
            top_k=1,
            finding_top_k=1,
        )

        result = ReviewAuditGraph().run(state)

        self.assertEqual(
            [item["node"] for item in result.agent_trace],
            ["generate_or_import_weaknesses", "plan_weakness_queries", "retrieve_evidence", "verify_weaknesses", "rank_findings"],
        )
        self.assertTrue(all(item["status"] == "succeeded" for item in result.agent_trace))
        self.assertEqual(result.agent_trace[0]["mode"], "imported")
        self.assertEqual(len(result.ranked_findings), 1)

    def test_graph_generates_weaknesses_when_none_are_imported(self) -> None:
        def generator(_state: ReviewAuditState) -> WeaknessGenerationResult:
            return WeaknessGenerationResult(
                weaknesses=[Weakness("w-generated", "p1", "The evaluation omits ablations.", "experiment", "major", "minimax_reviewer")],
                metadata={"provider_name": "minimax", "model_name": "MiniMax-M2.7", "is_silver": True},
            )

        state = ReviewAuditState(
            weaknesses=[],
            evidence_blocks=[EvidenceBlock("b1", "p1", "Experiments", "experiment", "The evaluation reports no ablations.")],
            weakness_generator=generator,
        )

        result = ReviewAuditGraph().run(state)

        self.assertEqual(result.weaknesses[0].source, "minimax_reviewer")
        self.assertEqual(result.generation_metadata["provider_name"], "minimax")
        self.assertEqual(result.agent_trace[0], {"node": "generate_or_import_weaknesses", "status": "succeeded", "mode": "generated", "weakness_count": 1})

    def test_structured_reviewer_connects_provider_generation_to_graph(self) -> None:
        class FakeProvider:
            def generate_json(self, _system: str, user: str, **_kwargs: object) -> ProviderGeneration:
                self.user_prompt = user
                return ProviderGeneration(
                    payload={
                        "weaknesses": [
                            {
                                "weakness_text": "The evaluation does not isolate the reranker contribution.",
                                "category": "experiment",
                                "severity": "major",
                            }
                        ]
                    },
                    metadata={"provider_name": "minimax", "model_name": "MiniMax-M2.7", "is_silver": True},
                )

        provider = FakeProvider()
        state = ReviewAuditState(
            weaknesses=[],
            evidence_blocks=[EvidenceBlock("b1", "p1", "Experiments", "experiment", "The full system is compared against BM25.")],
            weakness_generator=StructuredReviewerGenerator(provider, source="minimax_reviewer"),
        )

        result = ReviewAuditGraph().run(state)

        self.assertIn("The full system is compared against BM25.", provider.user_prompt)
        self.assertEqual(result.weaknesses[0].paper_id, "p1")
        self.assertEqual(result.weaknesses[0].source, "minimax_reviewer")
        self.assertEqual(result.generation_metadata["provider_name"], "minimax")

    def test_graph_records_failed_node_without_recording_private_error_text(self) -> None:
        def fail_node(_state: ReviewAuditState) -> None:
            raise RuntimeError("private provider response")

        graph = ReviewAuditGraph()
        graph.nodes = (("provider_generation", fail_node),)
        state = ReviewAuditState(weaknesses=[], evidence_blocks=[])

        with self.assertRaisesRegex(RuntimeError, "agent node failed"):
            graph.run(state)

        self.assertEqual(state.agent_trace, [{"node": "provider_generation", "status": "failed", "error_type": "RuntimeError"}])
        self.assertNotIn("private provider response", str(state.agent_trace))

    def test_workflow_returns_retrieval_verification_and_ranking(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major"),
            Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        blocks = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The ablation baseline removes the reranker."),
            EvidenceBlock("b2", "p1", "Introduction", "introduction", "The paper motivates agent retrieval."),
        ]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(len(result["retrieval"]), 2)
        self.assertEqual(len(result["verification"]), 2)
        self.assertGreaterEqual(len(result["ranked_findings"]), 1)
        self.assertEqual(
            [item["node"] for item in result["agent_trace"]],
            ["generate_or_import_weaknesses", "plan_weakness_queries", "retrieve_evidence", "verify_weaknesses", "rank_findings"],
        )

    def test_component_registry_exposes_planners_and_retrievers(self) -> None:
        self.assertEqual(DEFAULT_COMPONENT_REGISTRY.query_planner_names(), ("category_expansion", "direct"))
        self.assertEqual(DEFAULT_COMPONENT_REGISTRY.retriever_names(), ("bm25", "hierarchical"))
        with self.assertRaisesRegex(KeyError, "query planner"):
            DEFAULT_COMPONENT_REGISTRY.query_planner("missing")
        with self.assertRaisesRegex(KeyError, "retriever"):
            DEFAULT_COMPONENT_REGISTRY.retriever("missing")

    def test_graph_executes_selected_query_planner_and_retriever(self) -> None:
        state = ReviewAuditState(
            weaknesses=[Weakness("w1", "p1", "The evaluation is incomplete.", "experiment", "major")],
            evidence_blocks=[
                EvidenceBlock("b1", "p1", "Experiments", "experiment", "Ablation baseline evaluation results.")
            ],
            query_planner_name="category_expansion",
            retriever_name="bm25",
        )

        result = ReviewAuditGraph().run(state)

        self.assertIn("ablation", result.query_plan["w1"])
        self.assertEqual(result.retrieval["w1"][0].retriever, "bm25")
        self.assertEqual(result.agent_trace[1]["query_planner"], "category_expansion")
        self.assertEqual(result.agent_trace[2]["retriever"], "bm25")

    def test_workflow_runs_on_committed_jsonl_fixtures(self) -> None:
        fixture_dir = Path(__file__).resolve().parent / "fixtures"
        weaknesses = [Weakness.from_dict(row) for row in read_jsonl(fixture_dir / "sample_weaknesses.jsonl")]
        blocks = [EvidenceBlock.from_dict(row) for row in read_jsonl(fixture_dir / "sample_blocks.jsonl")]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["workflow"], "deterministic_review_audit_v1")
        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(result["metric_boundary"], "silver diagnostic")

    def test_workflow_controls_final_finding_count_separately(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper has limited ablation baselines.", "experiment", "major"),
            Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        blocks = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper has limited ablation baselines."),
            EvidenceBlock("b2", "p1", "Introduction", "introduction", "The motivation is unclear."),
        ]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=1, finding_top_k=1)

        self.assertEqual(len(result["ranked_findings"]), 1)

    def test_graph_registry_exposes_full_no_verifier_and_no_ranker_profiles(self) -> None:
        self.assertEqual(DEFAULT_GRAPH_REGISTRY.names(), ("full", "no_ranker", "no_verifier"))
        with self.assertRaisesRegex(KeyError, "graph profile"):
            DEFAULT_GRAPH_REGISTRY.get("missing")

    def test_no_verifier_and_no_ranker_profiles_remain_executable(self) -> None:
        state = ReviewAuditState(
            weaknesses=[
                Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major"),
                Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
            ],
            evidence_blocks=[EvidenceBlock("b1", "p1", "Experiments", "experiment", "The paper reports results.")],
            finding_top_k=1,
        )

        no_verifier = ReviewAuditGraph(profile="no_verifier").run(state)
        no_ranker = ReviewAuditGraph(profile="no_ranker").run(
            ReviewAuditState(weaknesses=state.weaknesses, evidence_blocks=state.evidence_blocks, finding_top_k=1)
        )

        self.assertTrue(all(item.label == "Supported" for item in no_verifier.verification.values()))
        self.assertEqual(no_ranker.ranked_findings[0].weakness_id, "w1")
        self.assertEqual(no_ranker.agent_trace[-1]["node"], "preserve_candidate_order")


if __name__ == "__main__":
    unittest.main()
