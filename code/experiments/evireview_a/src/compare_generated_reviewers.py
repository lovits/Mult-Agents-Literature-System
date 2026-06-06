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
    "minimax_reviewer": {
        "weaknesses": "minimax_reviewer_weaknesses.jsonl",
        "verified": "minimax_reviewer_verified_weaknesses.jsonl",
        "display": "MiniMax-M2.7 reviewer",
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


def common_paper_ids(raw: dict[str, dict[str, list[dict[str, Any]]]]) -> set[str]:
    paper_sets = [{row["paper_id"] for row in rows["generated"]} for rows in raw.values()]
    return set.intersection(*paper_sets) if paper_sets else set()


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
    generators = payload["generators"]
    displays = [item["display"] for item in generators.values()]
    metric_rows = [
        ("Generated weaknesses", lambda item: item["generated_weakness_count"]),
        ("Mean generated per paper", lambda item: item["mean_generated_per_paper"]),
        ("Generic rate", lambda item: item["generic_rate"]),
        ("Redundancy rate", lambda item: item["redundancy_rate"]),
        ("Coverage recall @ 0.18", lambda item: coverage_at(item, 0.18)["human_weakness_recall"]),
        ("Mean paper recall @ 0.18", lambda item: coverage_at(item, 0.18)["mean_paper_recall"]),
        ("Mean support score", lambda item: item["support"]["mean_support_score"]),
        ("Partially-supported-or-better rate", lambda item: item["support"]["partially_supported_or_better_rate"]),
    ]
    lines = [
        "# Generated Reviewer Fair Comparison",
        "",
        "This report compares all available reviewer generators on their exact common paper overlap.",
        "",
        "## Scope",
        "",
        f"- Overlap papers: {payload['overlap_paper_count']}",
        f"- Human weaknesses in overlap: {payload['human_weakness_count']}",
        "- Warning: this is a small paired diagnostic, not a final provider benchmark.",
        "",
        "## Paired Metrics",
        "",
        f"| Metric | {' | '.join(displays)} |",
        f"| --- | {' | '.join('---:' for _ in displays)} |",
        *[
            f"| {label} | {' | '.join(str(getter(item)) for item in generators.values())} |"
            for label, getter in metric_rows
        ],
        "",
        "## Verifier Label Counts",
        "",
        *[f"- {item['display']}: {item['support']['label_counts']}" for item in generators.values()],
        "",
        "## Interpretation",
        "",
        f"- The {payload['overlap_paper_count']}-paper common overlap enables a paired diagnostic without paper-selection differences.",
        "- This remains a small provider diagnostic and must not be interpreted as a final model ranking.",
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
    overlap_papers = common_paper_ids(raw)
    human_overlap = [row for row in human_all if row["paper_id"] in overlap_papers]
    payload = {
        "status": "ok",
        "task": "paired generated reviewer comparison on common provider overlap",
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
    summaries = " ".join(
        f"{key}_recall@0.18={coverage_at(item, 0.18)['human_weakness_recall']}"
        for key, item in payload["generators"].items()
    )
    print(f"generated_reviewer_comparison papers={payload['overlap_paper_count']} {summaries}")


if __name__ == "__main__":
    main()
