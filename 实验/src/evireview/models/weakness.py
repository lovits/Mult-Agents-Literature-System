from typing import Literal

from pydantic import BaseModel, model_validator

from evireview.models.evidence import EvidenceType


Aspect = Literal[
    "method",
    "experiment",
    "reproducibility",
    "novelty",
    "related_work",
    "missing_baseline",
    "external_comparison",
]

EXTERNAL_ASPECTS = {
    "novelty",
    "related_work",
    "missing_baseline",
    "external_comparison",
}


class CandidateWeakness(BaseModel):
    candidate_id: str
    paper_id: str
    aspect: Aspect
    target: str
    weakness: str
    severity: Literal["minor", "major"]
    suggestion: str
    source_agent: str


class QueryPlan(BaseModel):
    candidate_id: str
    aspect: Aspect
    keyword_queries: list[str]
    semantic_query: str
    expected_sections: list[str]
    expected_evidence_types: list[EvidenceType]
    literature_required: bool

    @model_validator(mode="after")
    def validate_literature_route(self) -> "QueryPlan":
        expected = self.aspect in EXTERNAL_ASPECTS
        if self.literature_required != expected:
            raise ValueError("literature_required must match the fixed external-aspect route")
        return self
