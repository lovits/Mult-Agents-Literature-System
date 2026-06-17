from evireview.agent.provider import ProviderResult
from evireview.evaluation.e6_provider_candidate_runner import (
    run_provider_candidate_experiment,
)


class FakeProvider:
    model = "deepseek-v4-flash-free"

    def __init__(self):
        self.calls = []

    def complete_json(self, role, payload):
        self.calls.append((role, payload))
        evidence_ids = [item["evidence_id"] for item in payload["evidence"]]
        return ProviderResult(
            data={
                "candidates": [
                    {
                        "weakness": "The method assumptions are unclear and need validation.",
                        "aspect": "method",
                        "severity": "major",
                        "suggestion": "Clarify assumptions and add targeted validation.",
                        "confidence": 0.8,
                        "evidence_ids": evidence_ids[:1] + ["invalid:id"],
                    },
                    {
                        "weakness": "The experiment needs stronger ablation evidence.",
                        "aspect": "experiment",
                        "severity": "major",
                        "suggestion": "Add ablations.",
                        "confidence": 0.7,
                        "evidence_ids": evidence_ids[:1],
                    },
                ]
            },
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            latency_ms=2.0,
            raw_content="{}",
        )


def test_e6_provider_candidate_runner_uses_failure_slice_without_review_prompt_leakage():
    submissions = [
        {
            "paper_id": "p1",
            "content": {
                "title": "Paper",
                "abstract": "A method with experiments.",
                "keywords": ["method"],
            },
            "reviews": [
                {
                    "id": "r1",
                    "content": {"weaknesses": "The method assumptions are unclear."},
                }
            ],
        }
    ]
    e6_result = {
        "system_generated_reports": [
            {
                "paper_id": "p1",
                "top_weaknesses": [
                    {
                        "weakness": "The empirical evaluation may need stronger ablation analysis.",
                        "aspect": "experiment",
                        "evidence_ids": ["p1:content:abstract"],
                    }
                ],
                "decision": "not_applicable",
            }
        ],
        "cue_aware_reports": [
            {
                "paper_id": "p1",
                "top_weaknesses": [
                    {
                        "weakness": "The novelty claim may need clearer positioning.",
                        "aspect": "novelty",
                        "evidence_ids": ["p1:content:title"],
                    }
                ],
                "decision": "not_applicable",
            }
        ],
    }
    diagnostics = {"failure_cases": [{"paper_id": "p1"}]}
    provider = FakeProvider()

    result = run_provider_candidate_experiment(
        e6_result=e6_result,
        diagnostics=diagnostics,
        submissions=submissions,
        provider=provider,
        limit=1,
        top_k=2,
    )

    assert result["protocol"]["provider_backed"] is True
    assert result["dataset"]["selected_papers"] == 1
    assert result["systems"]["P1_provider_generated_failure_slice"]["trace_coverage"] == 1.0
    assert result["integrity"]["invalid_citations"] == 1
    assert result["provider_reports"][0]["top_weaknesses"][0]["source_review_id"] is None
    role, payload = provider.calls[0]
    assert role == "generate_review_candidates"
    assert "reviews" not in payload["paper"]
    assert "Official Review" not in str(payload)
