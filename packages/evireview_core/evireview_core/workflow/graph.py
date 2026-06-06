from __future__ import annotations

from collections.abc import Callable
from typing import Any

from evireview_core.workflow.registry import DEFAULT_GRAPH_REGISTRY, GraphRegistry
from evireview_core.workflow.state import ReviewAuditState


class AgentNodeError(RuntimeError):
    def __init__(self, node: str, cause: Exception) -> None:
        super().__init__(f"agent node failed: {node}")
        self.node = node
        self.cause = cause


class ReviewAuditGraph:
    def __init__(self, profile: str = "full", registry: GraphRegistry = DEFAULT_GRAPH_REGISTRY) -> None:
        self.profile = profile
        self.nodes: tuple[tuple[str, Callable[[ReviewAuditState], dict[str, Any] | None]], ...] = registry.get(profile).nodes

    def run(self, state: ReviewAuditState) -> ReviewAuditState:
        for node_name, node in self.nodes:
            try:
                details = node(state)
            except Exception as exc:
                state.record(node_name, "failed", error_type=type(exc).__name__)
                raise AgentNodeError(node_name, exc) from exc
            state.record(node_name, "succeeded", **(details or {}))
        return state
