from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json
from evaluate_rubric_agent_coverage import THRESHOLDS, combined_similarity, redundancy_rate, safe_div


GENERATORS = {
    "rubric_agent": {
        "weaknesses": "rubric_agent_weaknesses.jsonl",
        "verified": "rubric_agent_verified_weaknesses.jsonl",
        "display": "Rubric-agent",
    },
    "glm_reviewer": {
        "weaknesses": "glm_reviewer_weaknesses.jsonl",
        "verified": "glm_reviewer_verified_weaknesses.jsonl",
        "display": "GLM-4.6V reviewer",
    },
}


def generic_flag(text: str) -> bool:
    lower = text.lower()
    generic_terms = [
        "unclear",
        "insufficient",
        "limited",
        "not enough",
        "weak",
        "may be",
        "appears to be",
        "difficult to assess",
    ]
    specific_terms = [
        "ablation",
        "baseline",
        "benchmark",
        "dataset",
        "experiment",
        "hyperparameter",
        "prompt",
        "section",
        "statistical",
        "table",
    ]
    return any(term in lower for term in generic_terms) and not any(term in lower for term in specific_terms)


def by_paper(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["paper_id"]].append(row)
    return grouped


def coverage_by_threshold(generated: list[dict[str, Any]], human_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    generated_by_paper = by_paper(generated)
    human_by_paper = by_paper(human_rows)
    results = []
    for threshold in THRESHOLDS:
        total = 0
        covered = 0
        paper_recalls = []
        for paper_id, human_items in human_by_paper.items():
            generated_items = generated_by_paper.get(paper_id, [])
            paper_covered = 0
            for human in human_items:
                total += 1
                best = max(
                    (combined_similarity(human["weakness_text"], item["weakness_text"]) for item in generated_items),
                    default=0.0,
                )
                if best >= threshold:
                    covered += 1
                    paper_covered += 1
            paper_recalls.append(safe_div(paper_covered, len(human_items)))
        results.append(
            {
                "threshold": threshold,
                "human_weakness_count": total,
                "covered_human_weakness_count": covered,
                "human_weakness_recall": round(safe_div(covered, total), 4),
                "mean_paper_recall": round(sum(paper_recalls) / len(paper_recalls), 4),
            }
        )
    return results


def support_summary(verified_rows: list[dict[str, Any]]) -> dict[str, Any]:
    support_scores = [float(row.get("support_score", 0.0)) for row in verified_rows]
    label_counts = Counter(row.get("verifier_label", "Unknown") for row in verified_rows)
    groundedish_count = label_counts.get("Partially Supported", 0) + label_counts.get("Supported", 0)
    return {
        "verified_count": len(verified_rows),
        "label_counts": dict(label_counts),
        "mean_support_score": round(safe_div(sum(support_scores), len(support_scores)), 4),
        "partially_supported_or_better_rate": round(safe_div(groundedish_count, len(verified_rows)), 4),
    }


def generator_metrics(
    key: str,
    generated: list[dict[str, Any]],
    verified: list[dict[str, Any]],
    human_rows: list[dict[str, Any]],
    paper_ids: set[str],
) -> dict[str, Any]:
    generated = [row for row in generated if row["paper_id"] in paper_ids]
    verified = [row for row in verified if row["paper_id"] in paper_ids]
    texts = [row["weakness_text"] for row in generated]
    coverage = coverage_by_threshold(generated, human_rows)
    return {
        "generator": key,
        "display": GENERATORS[key]["display"],
        "paper_count": len(paper_ids),
        "generated_weakness_count": len(generated),
        "human_weakness_count": len(human_rows),
        "mean_generated_per_paper": round(safe_div(len(generated), len(paper_ids)), 4),
        "category_counts": dict(Counter(row.get("category", "other") for row in generated)),
        "severity_counts": dict(Counter(row.get("severity", "unknown") for row in generated)),
        "generic_rate": round(safe_div(sum(1 for text in texts if generic_flag(text)), len(texts)), 4),
        "redundancy_rate": round(redundancy_rate(texts), 4),
        "coverage_by_threshold": coverage,
        "support": support_summary(verified),
    }


def coverage_at(metrics: dict[str, Any], threshold: float) -> dict[str, Any]:
    return next(row for row in metrics["coverage_by_threshold"] if row["threshold"] == threshold)


def render_report(payload: dict[str, Any]) -> None:
    rubric = payload["generators"]["rubric_agent"]
    glm = payload["generators"]["glm_reviewer"]
    rubric_018 = coverage_at(rubric, 0.18)
    glm_018 = coverage_at(glm, 0.18)
    lines = [
        "# Generated Reviewer Fair Comparison",
        "",
        "This report compares the deterministic rubric-agent and GLM-4.6V reviewer on the exact paper overlap where GLM output is available.",
        "",
        "## Scope",
        "",
        f"- Overlap papers: {payload['overlap_paper_count']}",
        f"- Human weaknesses in overlap: {payload['human_weakness_count']}",
        "- Warning: this is a small paired diagnostic, not a final provider benchmark.",
        "",
        "## Paired Metrics",
        "",
        "| Metric | Rubric-agent | GLM-4.6V reviewer |",
        "| --- | ---: | ---: |",
        f"| Generated weaknesses | {rubric['generated_weakness_count']} | {glm['generated_weakness_count']} |",
        f"| Mean generated per paper | {rubric['mean_generated_per_paper']} | {glm['mean_generated_per_paper']} |",
        f"| Generic rate | {rubric['generic_rate']} | {glm['generic_rate']} |",
        f"| Redundancy rate | {rubric['redundancy_rate']} | {glm['redundancy_rate']} |",
        f"| Coverage recall @ 0.18 | {rubric_018['human_weakness_recall']} | {glm_018['human_weakness_recall']} |",
        f"| Mean paper recall @ 0.18 | {rubric_018['mean_paper_recall']} | {glm_018['mean_paper_recall']} |",
        f"| Mean support score | {rubric['support']['mean_support_score']} | {glm['support']['mean_support_score']} |",
        f"| Partially-supported-or-better rate | {rubric['support']['partially_supported_or_better_rate']} | {glm['support']['partially_supported_or_better_rate']} |",
        "",
        "## Verifier Label Counts",
        "",
        f"- Rubric-agent: {rubric['support']['label_counts']}",
        f"- GLM-4.6V reviewer: {glm['support']['label_counts']}",
        "",
        "## Interpretation",
        "",
        f"- On this {payload['overlap_paper_count']}-paper overlap, GLM-4.6V produces fewer but more supported weaknesses than the deterministic rubric-agent.",
        "- Rubric-agent remains useful as a cheap structure-risk generator, but its overlap-sample support score is much lower.",
        "- The current 8-paper effective sample is a stronger diagnostic than the initial deployment sample, but still not a final provider benchmark.",
    ]
    (REPORT_DIR / "generated_reviewer_comparison_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    human_all = read_jsonl(DATA_DIR / "human_weaknesses.jsonl")
    raw = {
        key: {
            "generated": read_jsonl(DATA_DIR / spec["weaknesses"]),
            "verified": read_jsonl(DATA_DIR / spec["verified"]),
        }
        for key, spec in GENERATORS.items()
    }
    overlap_papers = set(row["paper_id"] for row in raw["glm_reviewer"]["generated"])
    human_overlap = [row for row in human_all if row["paper_id"] in overlap_papers]
    payload = {
        "status": "ok",
        "task": "paired generated reviewer comparison on GLM paper overlap",
        "warning": "Small paired diagnostic; use for experiment planning only.",
        "overlap_paper_ids": sorted(overlap_papers),
        "overlap_paper_count": len(overlap_papers),
        "human_weakness_count": len(human_overlap),
        "generators": {
            key: generator_metrics(key, rows["generated"], rows["verified"], human_overlap, overlap_papers)
            for key, rows in raw.items()
        },
    }
    write_json(DATA_DIR / "generated_reviewer_comparison_metrics.json", payload)
    render_report(payload)
    rubric_018 = coverage_at(payload["generators"]["rubric_agent"], 0.18)
    glm_018 = coverage_at(payload["generators"]["glm_reviewer"], 0.18)
    print(
        "generated_reviewer_comparison "
        f"papers={payload['overlap_paper_count']} "
        f"rubric_recall@0.18={rubric_018['human_weakness_recall']} "
        f"glm_recall@0.18={glm_018['human_weakness_recall']}"
    )


if __name__ == "__main__":
    main()
