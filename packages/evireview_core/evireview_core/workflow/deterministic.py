from __future__ import annotations

from typing import Any

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import rank_weaknesses
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.verification.heuristic import verify_with_heuristics


def run_deterministic_review_audit(
    weaknesses: list[Weakness],
    blocks: list[EvidenceBlock],
    top_k: int = 5,
    finding_top_k: int = 3,
) -> dict[str, Any]:
    retrieval: dict[str, list[dict[str, Any]]] = {}
    verification: dict[str, VerificationResult] = {}

    for weakness in weaknesses:
        candidates = hierarchical_search(weakness, blocks, top_k=top_k)
        retrieval[weakness.weakness_id] = [
            {
                "block_id": item.block_id,
                "rank": item.rank,
                "score": item.score,
                "section_type": item.section_type,
                "retriever": item.retriever,
            }
            for item in candidates
        ]
        verification[weakness.weakness_id] = verify_with_heuristics(weakness, candidates)

    ranked = rank_weaknesses(weaknesses, verification, top_k=finding_top_k)
    return {
        "workflow": "deterministic_review_audit_v1",
        "weakness_count": len(weaknesses),
        "evidence_block_count": len(blocks),
        "retrieval": retrieval,
        "verification": {key: value.to_dict() for key, value in verification.items()},
        "ranked_findings": [item.to_dict() for item in ranked],
        "metric_boundary": "silver diagnostic",
    }
