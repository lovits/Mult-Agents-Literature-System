from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evireview_core.domain.models import EvidenceBlock, Weakness


RUN_STATUSES = {"created", "queued", "running", "succeeded", "failed", "cancelled"}
JOB_STATUSES = {"queued", "running", "succeeded", "failed", "cancelled"}


@dataclass(frozen=True)
class ReviewAuditRequest:
    paper_id: str
    weaknesses: list[Weakness]
    evidence_blocks: list[EvidenceBlock]
    top_k: int = 5
    finding_top_k: int = 3

    def __post_init__(self) -> None:
        if not self.paper_id.strip():
            raise ValueError("paper_id must not be empty")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.finding_top_k <= 0:
            raise ValueError("finding_top_k must be positive")
        paper_ids = {item.paper_id for item in [*self.weaknesses, *self.evidence_blocks]}
        if paper_ids - {self.paper_id}:
            raise ValueError("weaknesses and evidence blocks must belong to the same paper")

    def to_payload(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "weaknesses": [item.to_dict() for item in self.weaknesses],
            "evidence_blocks": [item.to_dict() for item in self.evidence_blocks],
            "top_k": self.top_k,
            "finding_top_k": self.finding_top_k,
        }


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    paper_id: str
    status: str
    error: str | None = None


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    run_id: str
    status: str
    progress: float
    error: str | None = None
