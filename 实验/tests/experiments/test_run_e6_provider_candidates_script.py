import json

from scripts.run_e6_provider_candidates import run


def test_run_e6_provider_candidates_writes_pending_environment_without_key(tmp_path, monkeypatch):
    monkeypatch.delenv("EVIREVIEW_LLM_API_KEY", raising=False)
    output = tmp_path / "metrics.json"
    report = tmp_path / "report.md"
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                "e6_metrics: e6.json",
                "diagnostics: diagnostics.json",
                "openreview_path: openreview",
                "provider:",
                "  base_url: https://api.ccode.vip/v1",
                "  model: deepseek-v4-flash-free",
                "  timeout_seconds: 180",
                "  max_completion_tokens: 1024",
                "  max_tokens_field: max_tokens",
                "experiment:",
                "  limit: 8",
                "  top_k: 3",
                f"output: {output}",
                f"report: {report}",
            ]
        ),
        encoding="utf-8",
    )

    result = run(config, root=tmp_path)

    assert result["status"] == "pending_environment"
    assert output.exists()
    assert report.exists()
    assert "EVIREVIEW_LLM_API_KEY" in report.read_text(encoding="utf-8")
