import hashlib
import math
from collections.abc import Sequence

from evireview.agent.candidate_generator import (
    generate_candidate_weaknesses,
    generate_cue_aware_candidate_weaknesses,
)
from evireview.agent.evidence_adjudicator import EvidenceAdjudicator
from evireview.agent.refutation_agent import RefutationAgent
from evireview.agent.support_agent import SupportAgent
from evireview.models.evidence import EvidenceBundle, EvidenceItem
from evireview.models.paper import PaperDocument
from evireview.models.review import ReviewReport
from evireview.models.weakness import CandidateWeakness
from evireview.rag.paper_rag import PaperRAG
from evireview.system.config import AgentRAGSystemConfig
from evireview.system.paper_adapter import paper_from_submission
from evireview.system.planner import QueryPlanner
from evireview.system.ranker import EvidenceAwareMetaRanker
from evireview.system.schemas import (
    AgentRAGReviewResult,
    CandidateAuditTrace,
    ReviewPipelineRequest,
)


PIPELINE_STAGES = [
    "paper_parse_index",
    "candidate_generation",
    "query_planning",
    "paper_rag",
    "literature_rag_boundary",
    "support_refutation_audit",
    "adjudication",
    "meta_reviewer_ranking",
    "report_assembly",
]


class AgentRAGReviewPipeline:
    """Composable backend pipeline for automatic paper-review weakness auditing."""

    def __init__(self, config: AgentRAGSystemConfig | None = None):
        self.config = config or AgentRAGSystemConfig()
        self.planner = QueryPlanner()
        self.support_agent = SupportAgent()
        self.refutation_agent = RefutationAgent()
        self.adjudicator = EvidenceAdjudicator()
        self.ranker = EvidenceAwareMetaRanker(dedup_threshold=self.config.dedup_threshold)

    def run(self, request: ReviewPipelineRequest) -> AgentRAGReviewResult:
        paper = self._resolve_paper(request)
        submission = self._submission_for_generation(request, paper)
        rag = PaperRAG(
            paper.blocks,
            embed=_hash_embed,
            query_embed=_hash_embed,
            embed_many=_hash_embed_many,
        )
        candidate_dicts = self._generate_candidates(submission)
        traces: list[CandidateAuditTrace] = []
        ranker_input = []
        for candidate_dict in candidate_dicts:
            candidate = _candidate_from_dict(candidate_dict)
            query_plan = self.planner.plan(candidate)
            rag_result = rag.retrieve(query_plan, self.config.paper_rag)
            literature_evidence = self._literature_evidence(candidate, query_plan)
            bundle = EvidenceBundle(
                candidate_id=candidate.candidate_id,
                paper_evidence=rag_result.items,
                literature_evidence=literature_evidence,
            )
            support = self.support_agent.run(candidate, bundle)
            refutation = self.refutation_agent.run(candidate, bundle)
            adjudication = self.adjudicator.decide(candidate, support, refutation)
            trace = CandidateAuditTrace(
                candidate=candidate,
                query_plan=query_plan,
                evidence_bundle=bundle,
                support=support,
                refutation=refutation,
                adjudication=adjudication,
                rag_trace=rag_result.trace,
                metadata={
                    "candidate_rank_score": candidate_dict.get("rank_score"),
                    "candidate_confidence": candidate_dict.get("confidence"),
                },
            )
            traces.append(trace)
            ranker_input.append(
                {
                    "candidate": candidate,
                    "support": support,
                    "refutation": refutation,
                    "adjudication": adjudication,
                }
            )
        top_weaknesses = self.ranker.rank(ranker_input, top_k=self.config.top_k_weaknesses)
        report = ReviewReport(
            paper_id=paper.paper_id,
            summary=(
                f"Generated {len(candidate_dicts)} candidate weaknesses, audited "
                f"{len(traces)} candidates, and selected {len(top_weaknesses)} "
                "evidence-grounded issues. No paper-level decision recommendation is produced."
            ),
            top_weaknesses=top_weaknesses,
            trace_path="in_memory",
        )
        return AgentRAGReviewResult(
            paper_id=paper.paper_id,
            report=report,
            traces=traces,
            stages=PIPELINE_STAGES,
            system_trace={
                "frontend_included": False,
                "paper_decision_produced": False,
                "human_check_route": False,
                "literature_rag_enabled": self.config.literature_rag_enabled,
                "paper_rag_mode": self.config.paper_rag.mode,
                "top_k_weaknesses": self.config.top_k_weaknesses,
            },
        )

    def _resolve_paper(self, request: ReviewPipelineRequest) -> PaperDocument:
        if request.paper:
            return request.paper
        if request.submission:
            return paper_from_submission(request.submission)
        raise ValueError("request requires either paper or submission")

    def _submission_for_generation(
        self,
        request: ReviewPipelineRequest,
        paper: PaperDocument,
    ) -> dict:
        if request.submission:
            return request.submission
        text_by_section = {
            block.section.replace(" ", "_"): block.text
            for block in paper.blocks
        }
        return {
            "paper_id": paper.paper_id,
            "content": {
                "title": paper.title,
                "abstract": text_by_section.get("abstract", ""),
                **text_by_section,
            },
            "metadata": paper.metadata,
        }

    def _generate_candidates(self, submission: dict) -> list[dict]:
        generator = (
            generate_cue_aware_candidate_weaknesses
            if self.config.candidate_generator == "cue_aware"
            else generate_candidate_weaknesses
        )
        return generator(submission, max_candidates=self.config.max_candidates)

    def _literature_evidence(self, candidate, query_plan) -> list[EvidenceItem]:
        if not self.config.literature_rag_enabled or not query_plan.literature_required:
            return []
        return [
            EvidenceItem(
                evidence_id=f"literature:boundary:{candidate.aspect}",
                source="literature",
                text=(
                    "Literature-RAG evidence is reserved for novelty, related-work, "
                    "missing-baseline, and external-comparison aspects."
                ),
                score=0.01,
                section="literature_boundary",
                document_id="fixed_literature_corpus",
            )
        ]


def _candidate_from_dict(item: dict) -> CandidateWeakness:
    return CandidateWeakness(
        candidate_id=item["candidate_id"],
        paper_id=item["paper_id"],
        aspect=item["aspect"],
        target=item["target"],
        weakness=item["weakness"],
        severity=item["severity"],
        suggestion=item["suggestion"],
        source_agent=item["source_agent"],
    )


def _hash_embed_many(texts: Sequence[str]) -> list[list[float]]:
    return [_hash_embed(text) for text in texts]


def _hash_embed(text: str, dimensions: int = 64) -> list[float]:
    vector = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % dimensions
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
