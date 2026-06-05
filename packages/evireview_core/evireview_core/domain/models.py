from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PaperSection:
    paper_id: str
    section_path: str
    section_type: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PaperSection":
        return cls(
            paper_id=str(payload["paper_id"]),
            section_path=str(payload["section_path"]),
            section_type=str(payload["section_type"]),
            text=str(payload["text"]),
        )


@dataclass(frozen=True)
class EvidenceBlock:
    block_id: str
    paper_id: str
    section_path: str
    section_type: str
    text: str
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceBlock":
        return cls(
            block_id=str(payload["block_id"]),
            paper_id=str(payload["paper_id"]),
            section_path=str(payload["section_path"]),
            section_type=str(payload["section_type"]),
            text=str(payload["text"]),
            score=float(payload.get("score", 0.0)),
        )


@dataclass(frozen=True)
class Weakness:
    weakness_id: str
    paper_id: str
    weakness_text: str
    category: str
    severity: str = "unknown"
    source: str = "human_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Weakness":
        return cls(
            weakness_id=str(payload["weakness_id"]),
            paper_id=str(payload["paper_id"]),
            weakness_text=str(payload["weakness_text"]),
            category=str(payload.get("category", payload.get("category_rule", "other"))),
            severity=str(payload.get("severity", payload.get("severity_hint", "unknown"))),
            source=str(payload.get("source", "human_review")),
        )


@dataclass(frozen=True)
class RetrievalCandidate:
    weakness_id: str
    block_id: str
    rank: int
    score: float
    retriever: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationResult:
    weakness_id: str
    label: str
    support_score: float
    evidence_block_ids: tuple[str, ...]
    rationale: str
    verifier: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_block_ids"] = list(self.evidence_block_ids)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VerificationResult":
        return cls(
            weakness_id=str(payload["weakness_id"]),
            label=str(payload.get("label", payload.get("pred_label", ""))),
            support_score=float(payload.get("support_score", 0.0)),
            evidence_block_ids=tuple(str(item) for item in payload.get("evidence_block_ids", [])),
            rationale=str(payload.get("rationale", "")),
            verifier=str(payload.get("verifier", "")),
        )


@dataclass(frozen=True)
class RankedFinding:
    weakness_id: str
    rank: int
    rank_score: float
    label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
