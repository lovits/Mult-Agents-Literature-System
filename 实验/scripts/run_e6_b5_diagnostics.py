import argparse
import json
from pathlib import Path

import yaml

from evireview.evaluation.e6_b5_diagnostics import run_b5_diagnostics


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    e6_result = json.loads((root / config["e6_metrics"]).read_text(encoding="utf-8"))
    openreview_path = root / config["openreview_path"]
    submissions = json.loads(
        (openreview_path / "submissions_with_reviews.json").read_text(encoding="utf-8")
    )
    result = run_b5_diagnostics(
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
        "# E6 B5 Balanced Agent-RAG Diagnostics",
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
        "| System | Overall Proxy Overlap@K | Zero Overlap Rate | Paper Mean | Paper Median | Support Mean | Refutation Mean |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in result["systems"].items():
        lines.append(
            f"| {name} | {metrics['overall_proxy_overlap@k']:.4f} | "
            f"{metrics['zero_overlap_rate']:.4f} | {metrics['paper_score_mean']:.4f} | "
            f"{metrics['paper_score_median']:.4f} | "
            f"{metrics.get('support_strength_mean', 0.0):.4f} | "
            f"{metrics.get('refutation_strength_mean', 0.0):.4f} |"
        )
    comparison = result["comparison"]
    lines.extend(
        [
            "",
            "## B5 Comparisons",
            "",
            f"- B5 minus B4 mean delta: {comparison['b5_minus_b4_mean_delta']:.4f}",
            f"- B5 improved/tied/regressed vs B4: {comparison['b5_improved_vs_b4_papers']}/"
            f"{comparison['b5_tied_vs_b4_papers']}/{comparison['b5_regressed_vs_b4_papers']}",
            f"- B5 minus B3 mean delta: {comparison['b5_minus_b3_mean_delta']:.4f}",
            f"- B5 improved/tied/regressed vs B3: {comparison['b5_improved_vs_b3_papers']}/"
            f"{comparison['b5_tied_vs_b3_papers']}/{comparison['b5_regressed_vs_b3_papers']}",
            "",
            "## Aspect Bottlenecks",
            "",
            "| Aspect | Count | Proxy Overlap@K |",
            "|---|---:|---:|",
        ]
    )
    for item in result["aspect_bottlenecks"]:
        lines.append(
            f"| {item['aspect']} | {item['count']} | {item['proxy_overlap@k']:.4f} |"
        )
    lines.extend(["", "## Low-Overlap B5 Cases", ""])
    for item in result["low_overlap_cases"]:
        lines.append(
            f"- `{item['paper_id']}` B5={item['b5_proxy_overlap@k']:.4f}, "
            f"support={item['b5_support_strength_mean']:.4f}, "
            f"refutation={item['b5_refutation_strength_mean']:.4f}, "
            f"aspects={item['b5_aspects']}: {item['title']}"
        )
    lines.extend(["", "## B5 Regressions vs B4", ""])
    for item in result["regression_vs_b4_cases"]:
        lines.append(
            f"- `{item['paper_id']}` delta={item['delta_b5_minus_b4']:.4f}, "
            f"B4={item['b4_proxy_overlap@k']:.4f}, B5={item['b5_proxy_overlap@k']:.4f}: "
            f"{item['title']}"
        )
    lines.extend(["", "## Next Optimization Hints", ""])
    for hint in result["next_optimization_hints"]:
        lines.append(f"- {hint}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e6_b5_diagnostics.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
