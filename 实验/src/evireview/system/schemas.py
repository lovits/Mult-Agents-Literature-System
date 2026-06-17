from typing import Any

from pydantic import BaseModel, Field

from evireview.models.audit import AdjudicationResult, AuditCase
from evireview.models.evidence import EvidenceBundle
from evireview.models.paper import PaperDocument
from evireview.models.review import RankedWeakness, ReviewReport
from evireview.models.weakness import CandidateWeakness, QueryPlan


class ReviewPipelineRequest(BaseModel):
    submission: dict[str, Any] | None = None
    paper: PaperDocument | None = None

    @property
    def paper_id(self) -> str:
        if self.paper:
            return self.paper.paper_id
        if self.submission:
            return str(self.submission["paper_id"])
        raise ValueError("request requires either paper or submission")


class CandidateAuditTrace(BaseModel):
    candidate: CandidateWeakness
    query_plan: QueryPlan
    evidence_bundle: EvidenceBundle
    support: AuditCase
    refutation: AuditCase
    adjudication: AdjudicationResult
    rag_trace: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRAGReviewResult(BaseModel):
    paper_id: str
    report: ReviewReport
    traces: list[CandidateAuditTrace]
    stages: list[str]
    system_trace: dict[str, Any] = Field(default_factory=dict)

    @property
    def top_weaknesses(self) -> list[RankedWeakness]:
        return self.report.top_weaknesses
