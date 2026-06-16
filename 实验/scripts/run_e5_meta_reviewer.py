import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.claimcheck import ClaimCheckDataset
from evireview.evaluation.meta_reviewer_runner import run_meta_reviewer_baselines


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    dataset = ClaimCheckDataset.from_source_dir(root / config["claimcheck_path"])
    audit = _read_json(root / config["audit_metrics"])
    substanreview = _read_json(root / config["substanreview_metrics"])
    literature = _read_json(root / config["literature_metrics"])
    result = run_meta_reviewer_baselines(
        dataset,
        audit,
        substanreview,
        literature,
        top_k=config.get("top_k", 3),
    )
    output = root / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = root / config["report"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(result), encoding="utf-8")
    return result


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _render_report(result: dict) -> str:
    lines = [
        "# E5 Meta-Reviewer Ranker",
        "",
        "## Protocol",
        "",
        "- Gold labels are used only for metrics.",
        "- Candidate severity is not read from gold-derived smoke traces.",
        "- Covered/refuted Gold is not claimed.",
        "",
        "## Dataset",
        "",
        f"- Evaluated candidates: {result['dataset']['evaluated_candidates']}",
        f"- Paper groups: {result['dataset']['paper_groups']}",
        f"- Gold keep candidates: {result['dataset']['gold_keep_candidates']}",
        "",
        "## Metrics",
        "",
        "| System | Top-K Agreement Precision | Keep Coverage@K | High-Agreement Coverage@K | Redundancy Rate | Confidence Brier |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in result["systems"].items():
        lines.append(
            "| {name} | {precision:.4f} | {coverage:.4f} | {high:.4f} | {red:.4f} | {brier:.4f} |".format(
                name=name,
                precision=metrics["top_k_agreement_precision"],
                coverage=metrics["keep_coverage@k"],
                high=metrics["high_agreement_coverage@k"],
                red=metrics["redundancy_rate"],
                brier=metrics["confidence_brier"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "R3_evidence_aware combines text severity, audit decisions, support/refutation strength, "
            "SubstanReview substantiation prior, and the E3 controlled Literature-RAG boundary. "
            "It is evaluated as a ranking component, not as an accept/reject classifier.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e5_meta_reviewer.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    print(json.dumps({key: value for key, value in result.items() if key != "sample_rankings"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
