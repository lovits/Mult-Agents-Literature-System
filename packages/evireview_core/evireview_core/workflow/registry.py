from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from evireview_core.workflow.nodes import (
    assume_supported,
    deduplicate_weaknesses,
    generate_or_import_weaknesses,
    preserve_candidate_order,
    plan_weakness_queries,
    rank_findings,
    retrieve_evidence,
    skip_deduplication,
    verify_weaknesses,
)
from evireview_core.workflow.state import ReviewAuditState


AgentNode = Callable[[ReviewAuditState], dict[str, Any] | None]


@dataclass(frozen=True)
class GraphProfile:
    name: str
    nodes: tuple[tuple[str, AgentNode], ...]


class GraphRegistry:
    def __init__(self, profiles: tuple[GraphProfile, ...]) -> None:
        self._profiles = {profile.name: profile for profile in profiles}

    def get(self, name: str) -> GraphProfile:
        if name not in self._profiles:
            raise KeyError(f"graph profile not found: {name}")
        return self._profiles[name]

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))


BASE = (
    ("generate_or_import_weaknesses", generate_or_import_weaknesses),
    ("plan_weakness_queries", plan_weakness_queries),
    ("retrieve_evidence", retrieve_evidence),
)

DEFAULT_GRAPH_REGISTRY = GraphRegistry(
    (
        GraphProfile(
            "full",
            (*BASE, ("verify_weaknesses", verify_weaknesses), ("deduplicate_weaknesses", deduplicate_weaknesses), ("rank_findings", rank_findings)),
        ),
        GraphProfile(
            "no_dedup",
            (*BASE, ("verify_weaknesses", verify_weaknesses), ("skip_deduplication", skip_deduplication), ("rank_findings", rank_findings)),
        ),
        GraphProfile(
            "no_verifier",
            (*BASE, ("assume_supported", assume_supported), ("deduplicate_weaknesses", deduplicate_weaknesses), ("rank_findings", rank_findings)),
        ),
        GraphProfile(
            "no_ranker",
            (
                *BASE,
                ("verify_weaknesses", verify_weaknesses),
                ("deduplicate_weaknesses", deduplicate_weaknesses),
                ("preserve_candidate_order", preserve_candidate_order),
            ),
        ),
    )
)
