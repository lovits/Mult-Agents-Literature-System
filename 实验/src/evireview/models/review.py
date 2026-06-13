from pydantic import BaseModel


class RankedWeakness(BaseModel):
    candidate_id: str
    weakness: str
    evidence_ids: list[str]
    confidence: float
    rank_score: float


class ReviewReport(BaseModel):
    paper_id: str
    summary: str
    top_weaknesses: list[RankedWeakness]
    trace_path: str
