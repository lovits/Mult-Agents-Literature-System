from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.runs import PersistedPaperReviewAuditRequest, ReviewAuditRequest
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
    graph_profile: str = "full"
    query_planner: str = "direct"
    retriever: str = "hierarchical"
    weakness_generator: str = "imported"
    verifier: str = "heuristic"

    def to_request(self) -> ReviewAuditRequest:
        return ReviewAuditRequest(
            paper_id=self.paper_id,
            weaknesses=[Weakness.from_dict(item.model_dump()) for item in self.weaknesses],
            evidence_blocks=[EvidenceBlock.from_dict(item.model_dump()) for item in self.evidence_blocks],
            top_k=self.top_k,
            finding_top_k=self.finding_top_k,
            graph_profile=self.graph_profile,
            query_planner=self.query_planner,
            retriever=self.retriever,
            weakness_generator=self.weakness_generator,
            verifier=self.verifier,
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
    graph_profile: str = "full"
    query_planner: str = "direct"
    retriever: str = "hierarchical"
    weakness_generator: str = "imported"
    verifier: str = "heuristic"

    def to_weaknesses(self) -> list[Weakness]:
        return [Weakness.from_dict(item.model_dump()) for item in self.weaknesses]


class ExperimentPaperAuditInput(PersistedPaperReviewAuditInput):
    paper_id: str = Field(min_length=1)

    def to_request(self) -> PersistedPaperReviewAuditRequest:
        return PersistedPaperReviewAuditRequest(
            paper_id=self.paper_id,
            weaknesses=self.to_weaknesses(),
            top_k=self.top_k,
            finding_top_k=self.finding_top_k,
            graph_profile=self.graph_profile,
            query_planner=self.query_planner,
            retriever=self.retriever,
            weakness_generator=self.weakness_generator,
            verifier=self.verifier,
        )


class ExperimentPaperAuditBatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ExperimentPaperAuditInput] = Field(min_length=1, max_length=100)


class ExperimentManifestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("config")
    @classmethod
    def reject_secret_config_keys(cls, config: dict[str, Any]) -> dict[str, Any]:
        secret_keys = {"api_key", "apikey", "access_token", "secret", "password"}

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if str(key).lower() in secret_keys:
                        raise ValueError("experiment config must not contain secret-like keys")
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(config)
        return config
