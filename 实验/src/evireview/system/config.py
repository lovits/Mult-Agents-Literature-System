from typing import Literal

from pydantic import BaseModel, Field

from evireview.rag.paper_rag import PaperRAGConfig


class AgentRAGSystemConfig(BaseModel):
    """Backend-only system configuration for one paper review run."""

    max_candidates: int = Field(default=6, ge=1)
    top_k_weaknesses: int = Field(default=3, ge=1)
    paper_rag: PaperRAGConfig = Field(default_factory=PaperRAGConfig)
    candidate_generator: Literal["cue_aware", "deterministic"] = "cue_aware"
    literature_rag_enabled: bool = True
    dedup_threshold: float = Field(default=0.48, ge=0, le=1)
