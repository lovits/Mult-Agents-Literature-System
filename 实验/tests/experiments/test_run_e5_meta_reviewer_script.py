import json

from scripts.run_e5_meta_reviewer import run


def test_run_e5_meta_reviewer_writes_metrics_and_report(tmp_path):
    data = tmp_path / "claimcheck"
    data.mkdir()
    payload = {
        "paper1": {
            "meta": {"text": ["Claim 1: The model is evaluated on one baseline."]},
            "response": {
                "Weakness associated with claims": [
                    {
                        "Weakness span": "The paper lacks baseline comparisons.",
                        "Target claims": ["The model is evaluated on one baseline."],
                        "Weakness confidence score": 5,
                        "Weakness Annotation": {
                            "subjectivity": 2,
                            "agreement": 5,
                            "weakness_type": {"experiment": True},
                        },
                    }
                ]
            },
        }
    }
    (data / "main.json").write_text(json.dumps(payload), encoding="utf-8")
    (data / "pilot.json").write_text(json.dumps({}), encoding="utf-8")
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"traces": []}), encoding="utf-8")
    substan = tmp_path / "substan.json"
    substan.write_text(
        json.dumps(
            {
                "evaluation": {"substantiated_claim_rate": 0.42},
                "protocol": {"covered_refuted_gold": False},
            }
        ),
        encoding="utf-8",
    )
    literature = tmp_path / "literature.json"
    literature.write_text(
        json.dumps(
            {
                "systems": {
                    "L3_hybrid_metadata_filter": {
                        "citation_validity_rate": 1.0,
                        "future_leakage_count": 0,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "metrics.json"
    report = tmp_path / "report.md"
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                f"claimcheck_path: {data}",
                f"audit_metrics: {audit}",
                f"substanreview_metrics: {substan}",
                f"literature_metrics: {literature}",
                "top_k: 1",
                f"output: {output}",
                f"report: {report}",
            ]
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert report.exists()
    assert result["systems"]["R3_evidence_aware"]["top_k_agreement_precision"] == 1.0
    assert "E5 Meta-Reviewer Ranker" in report.read_text(encoding="utf-8")
