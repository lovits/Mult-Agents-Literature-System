import pytest
from pydantic import ValidationError

from evireview.models.audit import AdjudicationResult
from evireview.models.weakness import CandidateWeakness, QueryPlan


def test_candidate_rejects_unknown_aspect():
    with pytest.raises(ValidationError):
        CandidateWeakness(
            candidate_id="w1",
            paper_id="p1",
            aspect="writing_style",
            target="method",
            weakness="The method is unclear.",
            severity="major",
            suggestion="Clarify the method.",
            source_agent="method_reviewer",
        )


def test_query_plan_only_enables_literature_for_external_aspects():
    with pytest.raises(ValidationError):
        QueryPlan(
            candidate_id="w1",
            aspect="experiment",
            keyword_queries=["ablation"],
            semantic_query="retrieval module ablation",
            expected_sections=["experiments"],
            expected_evidence_types=["table_caption"],
            literature_required=True,
        )


def test_adjudication_rejects_confidence_outside_unit_interval():
    with pytest.raises(ValidationError):
        AdjudicationResult(
            candidate_id="w1",
            decision="keep",
            confidence=1.2,
            evidence_ids=["p1:b1"],
            reason="Supported by the ablation table.",
        )
