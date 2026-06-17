import argparse
import json
import os
from pathlib import Path

import yaml

from evireview.agent.provider import OpenAICompatibleProvider
from evireview.evaluation.e6_provider_candidate_runner import (
    run_provider_candidate_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    output = root / config["output"]
    report = root / config["report"]
    api_key = os.environ.get("EVIREVIEW_LLM_API_KEY")
    if not api_key:
        result = _pending_environment(config)
        _write_outputs(output, report, result)
        return result
    e6_result = json.loads((root / config["e6_metrics"]).read_text(encoding="utf-8"))
    diagnostics = json.loads((root / config["diagnostics"]).read_text(encoding="utf-8"))
    submissions = json.loads(
        ((root / config["openreview_path"]) / "submissions_with_reviews.json").read_text(
            encoding="utf-8"
        )
    )
    provider_config = config["provider"]
    provider = OpenAICompatibleProvider(
        base_url=os.environ.get("EVIREVIEW_LLM_BASE_URL", provider_config["base_url"]),
        model=os.environ.get("EVIREVIEW_LLM_MODEL", provider_config["model"]),
        api_key=api_key,
        timeout=provider_config["timeout_seconds"],
        max_completion_tokens=provider_config["max_completion_tokens"],
        max_tokens_field=provider_config.get("max_tokens_field", "max_tokens"),
        request_options=provider_config.get("request_options", {}),
        retry_attempts=provider_config.get("retry_attempts", 0),
        retry_backoff_seconds=provider_config.get("retry_backoff_seconds", 1),
    )
    result = run_provider_candidate_experiment(
        e6_result=e6_result,
        diagnostics=diagnostics,
        submissions=submissions,
        provider=provider,
        limit=config["experiment"]["limit"],
        top_k=config["experiment"]["top_k"],
    )
    _write_outputs(output, report, result)
    return result


def _pending_environment(config: dict) -> dict:
    return {
        "status": "pending_environment",
        "passed": False,
        "summary": "E6 provider candidate experiment requires EVIREVIEW_LLM_API_KEY.",
        "protocol": {
            "name": "e6-provider-candidate-failure-slice-v1",
            "provider_backed": False,
            "model": config["provider"]["model"],
            "selection": "e6_candidate_diagnostics_failure_cases",
            "limit": config["experiment"]["limit"],
            "top_k": config["experiment"]["top_k"],
            "prompt_input_boundary": "paper_metadata_and_b3_candidates_only_no_official_reviews",
            "gold_usage": "offline_proxy_evaluation_only",
            "accept_reject_decision": False,
        },
        "checks": {
            "environment": {
                "passed": False,
                "missing": ["EVIREVIEW_LLM_API_KEY"],
            }
        },
        "next_experiment": "Set EVIREVIEW_LLM_API_KEY in the shell and rerun E6-P.",
    }


def _write_outputs(output: Path, report: Path, result: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(result), encoding="utf-8")


def _render_report(result: dict) -> str:
    lines = [
        "# E6 Provider Candidate Failure-Slice Comparison",
        "",
        "## Protocol",
        "",
        f"- Status: `{result.get('status', 'completed')}`",
        f"- Model: `{result['protocol']['model']}`",
        f"- Selection: `{result['protocol']['selection']}`",
        f"- Prompt boundary: `{result['protocol']['prompt_input_boundary']}`",
        f"- Gold usage: `{result['protocol']['gold_usage']}`",
        "- Accept/reject decision: disabled",
        "",
    ]
    if result.get("status") == "pending_environment":
        lines.extend(
            [
                "## Environment",
                "",
                "- Missing `EVIREVIEW_LLM_API_KEY`; no provider calls were made.",
            ]
        )
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "## Dataset",
            "",
            f"- Selected papers: {result['dataset']['selected_papers']}",
            f"- OpenReview reviews in selected papers: {result['dataset']['openreview_reviews_in_selected_papers']}",
            "",
            "## System Metrics",
            "",
            "| System | Proxy Overlap@K | Trace Coverage | Top-K Compliance | Zero Overlap Rate | Review Leakage Free |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name, metrics in result["systems"].items():
        lines.append(
            f"| {name} | {metrics['official_weakness_proxy_overlap@k']:.4f} | "
            f"{metrics['trace_coverage']:.4f} | {metrics['top_k_compliance']:.4f} | "
            f"{metrics['zero_overlap_rate']:.4f} | {metrics['review_leakage_free']} |"
        )
    comparison = result["comparison"]
    integrity = result["integrity"]
    lines.extend(
        [
            "",
            "## Comparison",
            "",
            f"- P1 minus B3 proxy delta: {comparison['p1_minus_b3_proxy_overlap_delta']:.4f}",
            f"- P1 minus B2 proxy delta: {comparison['p1_minus_b2_proxy_overlap_delta']:.4f}",
            f"- P1 improved over B3 papers: {comparison['p1_improved_over_b3_papers']}",
            "",
            "## Integrity",
            "",
            f"- Provider failures: {integrity['provider_failures']}",
            f"- Evidence attribution accuracy: {integrity['evidence_attribution_accuracy']:.4f}",
            f"- Invalid citations: {integrity['invalid_citations']}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e6_deepseek_provider_candidates.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    compact = {key: value for key, value in result.items() if key != "provider_reports"}
    print(json.dumps(compact, ensure_ascii=False, indent=2))
    if result.get("status") == "pending_environment":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
