from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.e4_provider_runner import run_e4_provider_experiment


def _example() -> ClaimCheckWeakness:
    return ClaimCheckWeakness(
        example_id="main:1",
        split="main",
        paper_review_id="paper-1",
        weakness="The retrieval component lacks an ablation.",
        groundedness_confidence=4,
        target_claims=["We report an ablation."],
        paper_texts=["We report an ablation of the retrieval component."],
        relevant_text_ids={"paper-1:0"},
        subjectivity=2,
        agreement=5,
        weakness_types={"insufficient"},
    )


class FakeProvider:
    model = "fake-provider"

    def __init__(self):
        self.calls = []

    def complete_json(self, role, payload):
        from evireview.agent.provider import ProviderResult

        self.calls.append((role, payload))
        evidence_ids = [item["evidence_id"] for item in payload.get("evidence", [])]
        if role in {"support", "refutation", "support_strict", "refutation_strict"}:
            data = {
                "claim": f"{role} case",
                "evidence_ids": evidence_ids[:1],
                "strength": 0.8 if role.startswith("support") else 0.2,
                "rationale": role,
            }
        else:
            data = {
                "decision": "keep",
                "confidence": 0.8,
                "evidence_ids": evidence_ids[:1],
                "reason": role,
            }
        return ProviderResult(
            data=data,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            latency_ms=1.0,
            raw_content="{}",
        )


def test_provider_runner_contains_a0_a4_costs_and_traces():
    result = run_e4_provider_experiment(
        ClaimCheckDataset(examples=[_example()], paper_review_pairs=1),
        FakeProvider(),
        limit=1,
    )

    assert set(result["systems"]) == {"A0", "A1", "A2", "A3", "A4"}
    assert result["protocol"]["provider_backed"] is True
    assert result["evaluated"] == 1
    assert len(result["traces"]) == 1
    assert result["systems"]["A4"]["tokens_per_candidate"] > 0
    assert result["integrity"]["invalid_citations"] == 0
    assert result["integrity"]["evidence_attribution_accuracy"] == 1.0
    assert result["integrity"]["failures"] == 0


def test_provider_runner_can_use_deterministic_proxy_stratified_sample():
    examples = []
    for agreement in [5, 5, 5, 1, 1, 1, 3, 3, 3]:
        example = _example().model_copy(
            update={
                "example_id": f"main:{agreement}:{len(examples)}",
                "agreement": agreement,
            }
        )
        examples.append(example)

    result = run_e4_provider_experiment(
        ClaimCheckDataset(examples=examples, paper_review_pairs=1),
        FakeProvider(),
        limit=6,
        selection="stratified_proxy",
    )

    gold = [trace["gold_agreement_proxy"] for trace in result["traces"]]
    assert gold.count("keep") == 2
    assert gold.count("reject") == 2
    assert gold.count("uncertain") == 2


def test_bounded_v2_uses_strict_roles_and_compact_adjudicator_evidence():
    provider = FakeProvider()

    result = run_e4_provider_experiment(
        ClaimCheckDataset(examples=[_example()], paper_review_pairs=1),
        provider,
        limit=1,
        audit_profile="bounded_v2",
    )

    roles = [role for role, _ in provider.calls]
    assert roles == [
        "judge_no_evidence",
        "judge_with_evidence",
        "support_strict",
        "adjudicate_compact",
        "refutation_strict",
        "adjudicate_compact",
    ]
    adjudicator_payloads = [
        payload for role, payload in provider.calls if role == "adjudicate_compact"
    ]
    assert result["protocol"]["audit_profile"] == "bounded_v2"
    assert all(len(payload["evidence"]) == 1 for payload in adjudicator_payloads)
    assert all(
        payload["evidence"][0]["evidence_id"]
        in {
            evidence_id
            for case_name in ("support", "refutation")
            for evidence_id in (
                payload.get(case_name) or {"evidence_ids": []}
            )["evidence_ids"]
        }
        for payload in adjudicator_payloads
    )


def test_standard_v1_keeps_original_roles_and_full_adjudicator_evidence():
    provider = FakeProvider()

    result = run_e4_provider_experiment(
        ClaimCheckDataset(examples=[_example()], paper_review_pairs=1),
        provider,
        limit=1,
        audit_profile="standard_v1",
    )

    roles = [role for role, _ in provider.calls]
    assert roles == [
        "judge_no_evidence",
        "judge_with_evidence",
        "support",
        "adjudicate",
        "refutation",
        "adjudicate",
    ]
    assert result["protocol"]["audit_profile"] == "standard_v1"


def test_provider_runner_rejects_unknown_audit_profile():
    try:
        run_e4_provider_experiment(
            ClaimCheckDataset(examples=[_example()], paper_review_pairs=1),
            FakeProvider(),
            limit=1,
            audit_profile="unknown",
        )
    except ValueError as error:
        assert "unknown audit profile" in str(error)
    else:
        raise AssertionError("unknown audit profile must fail")
