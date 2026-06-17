from evireview.models.evidence import EvidenceType
from evireview.models.weakness import CandidateWeakness, EXTERNAL_ASPECTS, QueryPlan


SECTION_PRIORS = {
    "method": ["method", "approach", "algorithm", "model", "system"],
    "experiment": ["experiments", "evaluation", "results", "ablation", "appendix"],
    "reproducibility": ["implementation", "experiments", "appendix", "supplementary"],
    "novelty": ["introduction", "related work", "method", "discussion"],
    "related_work": ["related work", "introduction", "discussion"],
    "missing_baseline": ["experiments", "evaluation", "related work", "ablation"],
    "external_comparison": ["related work", "experiments", "discussion"],
}

EVIDENCE_TYPE_PRIORS: dict[str, list[EvidenceType]] = {
    "method": ["paragraph", "algorithm", "implementation_detail"],
    "experiment": ["table_caption", "paragraph", "appendix"],
    "reproducibility": ["implementation_detail", "appendix", "paragraph"],
    "novelty": ["paragraph"],
    "related_work": ["paragraph"],
    "missing_baseline": ["table_caption", "paragraph"],
    "external_comparison": ["paragraph"],
}


class QueryPlanner:
    """Creates reproducible section/type-aware retrieval plans per weakness."""

    def plan(self, candidate: CandidateWeakness) -> QueryPlan:
        keyword_queries = [
            f"{candidate.target} {candidate.aspect}",
            candidate.weakness,
            candidate.suggestion,
        ]
        return QueryPlan(
            candidate_id=candidate.candidate_id,
            aspect=candidate.aspect,
            keyword_queries=keyword_queries,
            semantic_query=f"{candidate.target}. {candidate.weakness} {candidate.suggestion}",
            expected_sections=SECTION_PRIORS[candidate.aspect],
            expected_evidence_types=EVIDENCE_TYPE_PRIORS[candidate.aspect],
            literature_required=candidate.aspect in EXTERNAL_ASPECTS,
        )
