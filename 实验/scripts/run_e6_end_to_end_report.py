import argparse
import json
from pathlib import Path

import yaml

from evireview.evaluation.end_to_end_report_runner import (
    run_end_to_end_report_baseline,
)


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    openreview_path = root / config["openreview_path"]
    unseen_path = root / config["unseen_path"]
    submissions = json.loads(
        (openreview_path / "submissions_with_reviews.json").read_text(encoding="utf-8")
    )
    arxiv_papers = json.loads((unseen_path / "papers.json").read_text(encoding="utf-8"))
    component_metrics = {
        name: json.loads((root / path).read_text(encoding="utf-8"))
        for name, path in config["component_metrics"].items()
    }
    result = run_end_to_end_report_baseline(
        submissions,
        arxiv_papers,
        component_metrics,
        top_k=config.get("top_k", 3),
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
        "# E6 End-to-End Structured Review Report",
        "",
        "## Protocol",
        "",
        "- Accept/reject decision: disabled",
        "- arXiv unseen Gold metrics: disabled",
        "- Component outputs: E2, E3, E4, E5",
        "",
        "## Dataset",
        "",
        f"- OpenReview papers: {result['dataset']['openreview_papers']}",
        f"- OpenReview official reviews: {result['dataset']['openreview_reviews']}",
        f"- arXiv unseen demo papers: {result['dataset']['arxiv_unseen_papers']}",
        "",
        "## System Metrics",
        "",
        "| System | Paper Report Coverage | Trace Coverage | Top-K Compliance | Accept/Reject Decisions | Review Leakage Free | Official Weakness Proxy Overlap@K |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in result["systems"].items():
        lines.append(
            "| {name} | {coverage:.4f} | {trace:.4f} | {topk:.4f} | {decisions} | {leakage} | {overlap:.4f} |".format(
                name=name,
                coverage=metrics["paper_report_coverage"],
                trace=metrics["trace_coverage"],
                topk=metrics["top_k_compliance"],
                decisions=metrics["accept_reject_decisions"],
                leakage=str(metrics.get("review_leakage_free", "n/a")),
                overlap=metrics.get("official_weakness_proxy_overlap@k", 0.0),
            )
        )
    lines.extend(["", "## Sample OpenReview Reports", ""])
    for report in result["openreview_reports"][:3]:
        lines.append(f"### {report['paper_id']}: {report['title']}")
        lines.append("")
        for item in report["top_weaknesses"]:
            lines.append(
                f"- `{item['candidate_id']}` score={item['rank_score']:.4f}, "
                f"evidence={', '.join(item['evidence_ids'])}: {item['weakness']}"
            )
        lines.append("")
    lines.extend(["", "## Sample System-Generated Reports", ""])
    for report in result["system_generated_reports"][:3]:
        lines.append(f"### {report['paper_id']}: {report['title']}")
        lines.append("")
        lines.append(f"- Candidate source: `{report['candidate_source']}`")
        lines.append("")
        for item in report["top_weaknesses"]:
            lines.append(
                f"- `{item['candidate_id']}` aspect={item['aspect']}, score={item['rank_score']:.4f}, "
                f"evidence={', '.join(item['evidence_ids'])}: {item['weakness']}"
            )
        lines.append("")
    lines.extend(
        [
            "## arXiv Unseen Demo Boundary",
            "",
            f"- Papers: {result['unseen_demo']['papers']}",
            f"- Gold metrics reported: {result['unseen_demo']['gold_metrics_reported']}",
            "",
            "The unseen set is used only to verify that the pipeline can carry new-paper metadata and PDF paths into a report-ready manifest.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e6_end_to_end_report.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    compact = {
        key: value
        for key, value in result.items()
        if key not in {"openreview_reports", "system_generated_reports"}
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
