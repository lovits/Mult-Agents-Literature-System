import json

from scripts.validate_e4_agnes_bounded_optimization import validate


def _result(profile, ids, *, a2_f1, a3_f1, a4_f1, a2_tokens, a4_tokens):
    system = lambda f1, tokens: {
        "agreement_proxy_macro_f1": f1,
        "tokens_per_candidate": tokens,
    }
    return {
        "protocol": {
            "audit_profile": profile,
            "provider_backed": True,
            "selection": "stratified_proxy",
        },
        "systems": {
            "A0": system(0.1, 0),
            "A1": system(0.2, 10),
            "A2": system(a2_f1, a2_tokens),
            "A3": system(a3_f1, a2_tokens * 1.5),
            "A4": system(a4_f1, a4_tokens),
        },
        "integrity": {"evidence_attribution_accuracy": 1.0, "failures": 0},
        "traces": [{"example_id": value} for value in ids],
    }


def test_validator_requires_same_sample_and_reports_scale_decision(tmp_path):
    ids = [f"main:{index}" for index in range(20)]
    baseline_path = tmp_path / "baseline.json"
    optimized_path = tmp_path / "optimized.json"
    baseline_path.write_text(
        json.dumps(
            _result(
                "standard_v1",
                ids,
                a2_f1=0.25,
                a3_f1=0.25,
                a4_f1=0.17,
                a2_tokens=4000,
                a4_tokens=14000,
            )
        ),
        encoding="utf-8",
    )
    optimized_path.write_text(
        json.dumps(
            _result(
                "bounded_v2",
                ids,
                a2_f1=0.25,
                a3_f1=0.24,
                a4_f1=0.28,
                a2_tokens=4000,
                a4_tokens=9000,
            )
        ),
        encoding="utf-8",
    )

    result = validate(baseline_path, optimized_path)

    assert result["passed"] is True
    assert result["experiment_verdict"] == "passed_success_criteria"
    assert result["scale_decision"] == "scale_to_main"
    assert result["checks"]["same_frozen_sample"]["passed"] is True


def test_validator_stops_scaling_when_bounded_optimization_misses_gate(tmp_path):
    ids = [f"main:{index}" for index in range(20)]
    baseline_path = tmp_path / "baseline.json"
    optimized_path = tmp_path / "optimized.json"
    baseline_path.write_text(
        json.dumps(
            _result(
                "standard_v1",
                ids,
                a2_f1=0.25,
                a3_f1=0.25,
                a4_f1=0.17,
                a2_tokens=4000,
                a4_tokens=14000,
            )
        ),
        encoding="utf-8",
    )
    optimized_path.write_text(
        json.dumps(
            _result(
                "bounded_v2",
                ids,
                a2_f1=0.25,
                a3_f1=0.24,
                a4_f1=0.18,
                a2_tokens=4000,
                a4_tokens=12000,
            )
        ),
        encoding="utf-8",
    )

    result = validate(baseline_path, optimized_path)

    assert result["passed"] is True
    assert result["experiment_verdict"] == "failed_with_metrics"
    assert result["scale_decision"] == "stop_after_bounded_optimization"
