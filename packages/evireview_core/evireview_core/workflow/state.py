from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from evireview_core.domain.models import EvidenceBlock, RankedFinding, RetrievalCandidate, VerificationResult, Weakness


@dataclass
class ReviewAuditState:
    weaknesses: list[Weakness]
    evidence_blocks: list[EvidenceBlock]
    top_k: int = 5
    finding_top_k: int = 3
    retrieval: dict[str, list[RetrievalCandidate]] = field(default_factory=dict)
    verification: dict[str, VerificationResult] = field(default_factory=dict)
    ranked_findings: list[RankedFinding] = field(default_factory=list)
    agent_trace: list[dict[str, Any]] = field(default_factory=list)

    def record(self, node: str, status: str, **details: Any) -> None:
        self.agent_trace.append({"node": node, "status": status, **details})
