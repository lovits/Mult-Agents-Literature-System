from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.runs import ReviewAuditRequest
from evireview_core.domain.models import EvidenceBlock, Weakness


class WeaknessInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weakness_id: str
    paper_id: str
    weakness_text: str
    category: str
    severity: str = "unknown"
    source: str = "human_review"


class EvidenceBlockInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_id: str
    paper_id: str
    section_path: str
    section_type: str
    text: str
    score: float = 0.0


class ReviewAuditInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_id: str
    weaknesses: list[WeaknessInput] = Field(default_factory=list)
    evidence_blocks: list[EvidenceBlockInput] = Field(default_factory=list)
    top_k: int = Field(default=5, gt=0)
    finding_top_k: int = Field(default=3, gt=0)

    def to_request(self) -> ReviewAuditRequest:
        return ReviewAuditRequest(
            paper_id=self.paper_id,
            weaknesses=[Weakness.from_dict(item.model_dump()) for item in self.weaknesses],
            evidence_blocks=[EvidenceBlock.from_dict(item.model_dump()) for item in self.evidence_blocks],
            top_k=self.top_k,
            finding_top_k=self.finding_top_k,
        )


class CreatedRunResponse(BaseModel):
    run: dict[str, Any]
    job: dict[str, Any]
    delivery_id: str


class PaperImportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    markdown: str = Field(min_length=1)


class PersistedPaperReviewAuditInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weaknesses: list[WeaknessInput] = Field(default_factory=list)
    top_k: int = Field(default=5, gt=0)
    finding_top_k: int = Field(default=3, gt=0)

    def to_weaknesses(self) -> list[Weakness]:
        return [Weakness.from_dict(item.model_dump()) for item in self.weaknesses]
