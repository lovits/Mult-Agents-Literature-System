from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.workflow.registry import DEFAULT_GRAPH_REGISTRY
from evireview_core.workflow.components import DEFAULT_COMPONENT_REGISTRY


RUN_STATUSES = {"created", "queued", "running", "succeeded", "failed", "cancelled"}
JOB_STATUSES = {"queued", "running", "succeeded", "failed", "cancelled"}


@dataclass(frozen=True)
class ReviewAuditRequest:
    paper_id: str
    weaknesses: list[Weakness]
    evidence_blocks: list[EvidenceBlock]
    top_k: int = 5
    finding_top_k: int = 3
    graph_profile: str = "full"
    query_planner: str = "direct"
    retriever: str = "hierarchical"
    weakness_generator: str = "imported"
    verifier: str = "heuristic"

    def __post_init__(self) -> None:
        if not self.paper_id.strip():
            raise ValueError("paper_id must not be empty")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.finding_top_k <= 0:
            raise ValueError("finding_top_k must be positive")
        if self.graph_profile not in DEFAULT_GRAPH_REGISTRY.names():
            raise ValueError(f"unknown graph_profile: {self.graph_profile}")
        if self.query_planner not in DEFAULT_COMPONENT_REGISTRY.query_planner_names():
            raise ValueError(f"unknown query_planner: {self.query_planner}")
        if self.retriever not in DEFAULT_COMPONENT_REGISTRY.retriever_names():
            raise ValueError(f"unknown retriever: {self.retriever}")
        if self.weakness_generator not in DEFAULT_COMPONENT_REGISTRY.weakness_generator_names():
            raise ValueError(f"unknown weakness_generator: {self.weakness_generator}")
        if self.verifier not in DEFAULT_COMPONENT_REGISTRY.verifier_names():
            raise ValueError(f"unknown verifier: {self.verifier}")
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
            "graph_profile": self.graph_profile,
            "query_planner": self.query_planner,
            "retriever": self.retriever,
            "weakness_generator": self.weakness_generator,
            "verifier": self.verifier,
        }


@dataclass(frozen=True)
class PersistedPaperReviewAuditRequest:
    paper_id: str
    weaknesses: list[Weakness]
    top_k: int = 5
    finding_top_k: int = 3
    graph_profile: str = "full"
    query_planner: str = "direct"
    retriever: str = "hierarchical"
    weakness_generator: str = "imported"
    verifier: str = "heuristic"


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
