import argparse
import json
from pathlib import Path

from evireview.evaluation.e6_neurips_stability import run_neurips_stability_experiment


ROOT = Path(__file__).resolve().parents[1]


def run(
    *,
    processed_root: Path | None = None,
    output: Path | None = None,
    report: Path | None = None,
    sample_size: int = 50,
    top_k: int = 3,
) -> dict:
    processed_root = processed_root or (
        ROOT / "dataset/processed/candidate_expansion_2026_06_17"
    )
    result = run_neurips_stability_experiment(
        processed_root,
        sample_size=sample_size,
        top_k=top_k,
    )
    output = output or ROOT / "outputs/metrics/e6_neurips_stability.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = report or ROOT / "reports/e6_neurips_stability_2026-06-17.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(result), encoding="utf-8")
    return result


def _render_report(result: dict) -> str:
    systems = result["systems"]
    comparison = result["comparison"]
    rows = []
    for name in [
        "B2_system_generated_structured_report",
        "B3_cue_aware_structured_report",
        "B4_agent_rag_pipeline_report",
        "B5_balanced_agent_rag_pipeline_report",
    ]:
        metrics = systems[name]
        rows.append(
            "| {name} | {coverage:.4f} | {trace:.4f} | {topk:.4f} | {overlap:.4f} | {diversity:.4f} | {redundancy:.4f} | {decision_count} |".format(
                name=name,
                coverage=metrics["paper_report_coverage"],
                trace=metrics["trace_coverage"],
                topk=metrics["top_k_compliance"],
                overlap=metrics["official_weakness_proxy_overlap@k"],
                diversity=metrics["aspect_diversity@k"],
                redundancy=metrics["redundancy_rate@k"],
                decision_count=metrics["accept_reject_decisions"],
            )
        )

    return "\n".join(
        [
            "# E6 NeurIPS 2023 Stability Diagnostic",
            "",
            "## Protocol",
            "",
            f"- Name: `{result['protocol']['name']}`",
            f"- Sample size: {result['protocol']['sample_size']}",
            f"- Top-K: {result['protocol']['top_k']}",
            f"- Gold boundary: {result['protocol']['gold_boundary']}",
            f"- Accept/reject decision: {result['protocol']['accept_reject_decision']}",
            "",
            "## Dataset",
            "",
            f"- Papers: {result['dataset']['papers']}",
            f"- Reviews: {result['dataset']['reviews']}",
            f"- Source: `{result['dataset']['source']}`",
            "",
            "## Metrics",
            "",
            "| System | Coverage | Trace Coverage | Top-K Compliance | Review Proxy Overlap@K | Aspect Diversity@K | Redundancy@K | Accept/Reject Decisions |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            *rows,
            "",
            "## Comparison",
            "",
            f"- B5 overlap delta vs B3: {comparison['b5_overlap_delta_vs_b3']:.6f}",
            f"- B5 overlap delta vs B4: {comparison['b5_overlap_delta_vs_b4']:.6f}",
            f"- B5 aspect diversity delta vs B4: {comparison['b5_aspect_diversity_delta_vs_b4']:.6f}",
            f"- B5 redundancy delta vs B4: {comparison['b5_redundancy_delta_vs_b4']:.6f}",
            f"- Experiment verdict: `{result['experiment_verdict']}`",
            "",
            "## Interpretation",
            "",
            "This diagnostic tests whether the existing E6 Agent-RAG assembly remains stable when moved from the OpenReview seed to a 50-paper NeurIPS 2023 processed sample. The official review text is used only as a weak proxy for weakness overlap; it is not a strict human Gold weakness annotation.",
            "",
            "No paper-level accept/reject decision is produced. The result should be used to guide the next engineering step, not as final thesis evidence.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    result = run(
        sample_size=args.sample_size,
        top_k=args.top_k,
        output=args.output,
        report=args.report,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
