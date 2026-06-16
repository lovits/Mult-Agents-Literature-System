import json

import yaml

from scripts.run_substanreview_baselines import run


def test_run_substanreview_baselines_writes_configured_output(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    review = "The method is weak because no ablation is reported."
    row = {
        "id": 1,
        "review": review,
        "label": [
            [0, len("The method is weak"), "Eval_neg_1"],
            [
                review.index("because"),
                len(review) - 1,
                "Jus_neg_1",
            ],
        ],
    }
    (data / "train.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (data / "test.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    output = tmp_path / "metrics.json"
    config = tmp_path / "config.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "dataset": {"path": str(data)},
                "output": str(output),
            }
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert output.exists()
    assert result["evaluation"]["claims"] == 1
    assert result["systems"]["S0_proximity"]["evidence_hit@1"] == 1.0
