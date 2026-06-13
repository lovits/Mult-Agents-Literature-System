from typing import Literal

from pydantic import BaseModel


EvidenceType = Literal[
    "paragraph",
    "table_caption",
    "figure_caption",
    "algorithm",
    "implementation_detail",
    "appendix",
    "absence_signal",
]


class EvidenceBlock(BaseModel):
    block_id: str
    paper_id: str
    section: str
    evidence_type: EvidenceType
    text: str
    ordinal: int


class EvidenceItem(BaseModel):
    evidence_id: str
    source: Literal["paper", "literature"]
    text: str
    score: float
    section: str | None = None
    document_id: str | None = None
    url: str | None = None


class EvidenceBundle(BaseModel):
    candidate_id: str
    paper_evidence: list[EvidenceItem]
    literature_evidence: list[EvidenceItem]
