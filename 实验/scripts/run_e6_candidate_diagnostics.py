import argparse
import json
from pathlib import Path

import yaml

from evireview.evaluation.e6_candidate_diagnostics import run_candidate_diagnostics


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    e6_result = json.loads((root / config["e6_metrics"]).read_text(encoding="utf-8"))
    openreview_path = root / config["openreview_path"]
    submissions = json.loads(
        (openreview_path / "submissions_with_reviews.json").read_text(encoding="utf-8")
    )
    result = run_candidate_diagnostics(
        e6_result,
        submissions,
        top_failure_count=config.get("top_failure_count", 8),
    )
    output = root / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = root / config["report"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(result), encoding="utf-8")
    return result


def _render_report(result: dict) -> str:
    lines = [
        "# E6 Candidate Generation Diagnostics",
        "",
        "## Protocol",
        "",
        f"- Source experiment: `{result['protocol']['source_experiment']}`",
        f"- Gold usage: `{result['protocol']['gold_usage']}`",
        "- Accept/reject decision: disabled",
        "",
        "## Dataset",
        "",
        f"- OpenReview papers: {result['dataset']['openreview_papers']}",
        f"- OpenReview official reviews: {result['dataset']['openreview_reviews']}",
        "",
        "## System Summary",
        "",
        "| System | Overall Proxy Overlap@K | Zero Overlap Rate | Paper Mean | Paper Median |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in result["systems"].items():
        lines.append(
            f"| {name} | {metrics['overall_proxy_overlap@k']:.4f} | "
            f"{metrics['zero_overlap_rate']:.4f} | {metrics['paper_score_mean']:.4f} | "
            f"{metrics['paper_score_median']:.4f} |"
        )
    comparison = result["comparison"]
    lines.extend(
        [
            "",
            "## B3 vs B2 Paper-Level Comparison",
            "",
            f"- Mean delta: {comparison['b3_minus_b2_mean_delta']:.4f}",
            f"- Improved papers: {comparison['b3_improved_papers']}",
            f"- Tied papers: {comparison['b3_tied_papers']}",
            f"- Regressed papers: {comparison['b3_regressed_papers']}",
            f"- Failure-or-tie rate: {comparison['failure_or_tie_rate']:.4f}",
            "",
            "## Aspect Distribution",
            "",
        ]
    )
    for name, metrics in result["systems"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| Aspect | Count | Proxy Overlap@K |")
        lines.append("|---|---:|---:|")
        for aspect, count in metrics["aspect_distribution"].items():
            score = metrics["aspect_proxy_overlap@k"].get(aspect, 0.0)
            lines.append(f"| {aspect} | {count} | {score:.4f} |")
        lines.append("")
    lines.extend(["## Failure Or Tie Cases", ""])
    for item in result["failure_cases"]:
        lines.append(
            f"- `{item['paper_id']}` delta={item['delta_b3_minus_b2']:.4f}, "
            f"B2={item['b2_proxy_overlap@k']:.4f}, B3={item['b3_proxy_overlap@k']:.4f}: "
            f"{item['title']}"
        )
    lines.extend(["", "## Next Optimization Hints", ""])
    for hint in result["next_optimization_hints"]:
        lines.append(f"- {hint}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e6_candidate_diagnostics.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
