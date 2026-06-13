from typing import Any

from pydantic import BaseModel, Field

from evireview.models.evidence import EvidenceBlock


class PaperDocument(BaseModel):
    paper_id: str
    title: str
    source_path: str
    sections: list[str]
    blocks: list[EvidenceBlock]
    metadata: dict[str, Any] = Field(default_factory=dict)
