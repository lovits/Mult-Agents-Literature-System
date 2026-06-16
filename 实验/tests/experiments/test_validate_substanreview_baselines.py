import json

from scripts.validate_substanreview_baselines import validate


def _result(*, reviews=550, test_claims=580, best="S2_hybrid"):
    systems = {
        "S0_proximity": {
            "supported_f1": 0.30,
            "evidence_hit@1": 0.10,
            "evidence_token_f1": 0.20,
        },
        "S1_lexical": {
            "supported_f1": 0.31,
            "evidence_hit@1": 0.11,
            "evidence_token_f1": 0.21,
        },
        "S2_hybrid": {
            "supported_f1": 0.40,
            "evidence_hit@1": 0.20,
            "evidence_token_f1": 0.30,
        },
    }
    if best == "S1_lexical":
        systems["S1_lexical"]["supported_f1"] = 0.45
    return {
        "protocol": {
            "development_split": "train",
            "evaluation_split": "test",
            "gold_claim_spans": True,
            "development_gold_used_for_threshold_tuning": True,
            "evaluation_gold_used_only_for_metrics": True,
            "weakness_validity_gold": False,
            "covered_refuted_gold": False,
        },
        "dataset": {
            "reviews": reviews,
            "train_reviews": 440,
            "test_reviews": 110,
            "claims": 2940,
            "supports": {
                "claim_evidence_substantiation": True,
                "weakness_validity": False,
                "covered_refuted_gold": False,
            },
        },
        "evaluation": {
            "reviews": 110,
            "claims": test_claims,
            "supported_claims": 241,
            "claim_evidence_coverage": 241 / 580,
            "substantiated_claim_rate": 0.42,
        },
        "systems": systems,
        "sample_results": [{"claim_id": str(index)} for index in range(test_claims)],
    }


def test_substanreview_validator_accepts_gold_auxiliary_experiment(tmp_path):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps(_result()), encoding="utf-8")

    result = validate(metrics)

    assert result["status"] == "passed"
    assert result["passed"] is True
    assert result["best_system"] == "S2_hybrid"
    assert result["checks"]["evaluation_boundary"]["passed"] is True


def test_substanreview_validator_fails_when_weakness_gold_is_claimed(tmp_path):
    payload = _result()
    payload["protocol"]["weakness_validity_gold"] = True
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps(payload), encoding="utf-8")

    result = validate(metrics)

    assert result["status"] == "failed"
    assert result["checks"]["evaluation_boundary"]["passed"] is False
