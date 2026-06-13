from typing import Literal

from pydantic import BaseModel, Field


Decision = Literal["keep", "rewrite", "reject", "uncertain"]


class AuditCase(BaseModel):
    candidate_id: str
    stance: Literal["support", "refutation"]
    claim: str
    evidence_ids: list[str]
    strength: float = Field(ge=0, le=1)
    rationale: str


class AdjudicationResult(BaseModel):
    candidate_id: str
    decision: Decision
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str]
    reason: str
    rewritten_weakness: str | None = None
