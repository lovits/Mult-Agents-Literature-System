from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Callable

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json
from evaluate_claimcheck_retrieval import char_ngrams, set_cosine


THRESHOLDS = (0.12, 0.18, 0.24)


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def similarity(left: str, right: str, analyzer: Callable[[str], list[str]] = tokenize) -> float:
    return set_cosine(left, right, analyzer)


def combined_similarity(left: str, right: str) -> float:
    return 0.55 * similarity(left, right, tokenize) + 0.45 * similarity(left, right, char_ngrams)


def generic_flag(text: str) -> bool:
    lower = text.lower()
    generic_patterns = [
        "may be under-specified",
        "may need stronger",
        "may be incomplete",
        "may be insufficient",
        "may need tightening",
    ]
    has_specific_signal = any(
        token in lower
        for token in ["tokens", "ablation", "baseline", "hyperparameter", "related-work", "limitation section"]
    )
    return any(pattern in lower for pattern in generic_patterns) and not has_specific_signal


def redundancy_rate(texts: list[str], threshold: float = 0.72) -> float:
    if len(texts) < 2:
        return 0.0
    duplicate_pairs = 0
    total_pairs = 0
    for left_index in range(len(texts)):
        for right_index in range(left_index + 1, len(texts)):
            total_pairs += 1
            if combined_similarity(texts[left_index], texts[right_index]) >= threshold:
                duplicate_pairs += 1
    return safe_div(duplicate_pairs, total_pairs)


def evaluate_threshold(
    generated_by_paper: dict[str, list[dict]],
    human_by_paper: dict[str, list[dict]],
    threshold: float,
) -> dict:
    total_human = 0
    covered_human = 0
    category_total = Counter()
    category_covered = Counter()
    paper_recalls = []
    for paper_id, human_items in human_by_paper.items():
        generated = generated_by_paper.get(paper_id, [])
        paper_covered = 0
        for human in human_items:
            total_human += 1
            category_total[human["category_rule"]] += 1
            best = max(
                (combined_similarity(human["weakness_text"], item["weakness_text"]) for item in generated),
                default=0.0,
            )
            if best >= threshold:
                covered_human += 1
                paper_covered += 1
                category_covered[human["category_rule"]] += 1
        paper_recalls.append(safe_div(paper_covered, len(human_items)))

    return {
        "threshold": threshold,
        "human_weakness_count": total_human,
        "covered_human_weakness_count": covered_human,
        "human_weakness_recall": round(safe_div(covered_human, total_human), 4),
        "mean_paper_recall": round(sum(paper_recalls) / len(paper_recalls), 4),
        "category_recall": {
            category: round(safe_div(category_covered[category], count), 4)
            for category, count in sorted(category_total.items())
        },
    }


def top_match_examples(generated_by_paper: dict[str, list[dict]], human_by_paper: dict[str, list[dict]], limit: int = 8) -> list[dict]:
    examples = []
    for paper_id, human_items in human_by_paper.items():
        generated = generated_by_paper.get(paper_id, [])
        for human in human_items:
            scored = [
                (combined_similarity(human["weakness_text"], item["weakness_text"]), item)
                for item in generated
            ]
            if not scored:
                continue
            score, item = max(scored, key=lambda pair: pair[0])
            examples.append(
                {
                    "paper_id": paper_id,
                    "human_weakness_id": human["weakness_id"],
                    "generated_weakness_id": item["generated_weakness_id"],
                    "similarity": round(score, 4),
                    "human_category": human["category_rule"],
                    "generated_category": item["category"],
                }
            )
    return sorted(examples, key=lambda item: item["similarity"], reverse=True)[:limit]


def main() -> None:
    ensure_dirs()
    generated_rows = read_jsonl(DATA_DIR / "rubric_agent_weaknesses.jsonl")
    human_rows = read_jsonl(DATA_DIR / "human_weaknesses.jsonl")
    generated_by_paper: dict[str, list[dict]] = defaultdict(list)
    human_by_paper: dict[str, list[dict]] = defaultdict(list)
    for row in generated_rows:
        generated_by_paper[row["paper_id"]].append(row)
    for row in human_rows:
        human_by_paper[row["paper_id"]].append(row)

    generated_texts = [row["weakness_text"] for row in generated_rows]
    payload = {
        "status": "ok",
        "generator": "rubric_agent_v0",
        "task": "Coverage diagnostic for deterministic rubric-agent weaknesses against human reviewer weaknesses",
        "warning": "Lexical/character overlap is a weak proxy for semantic coverage; use this as a pipeline baseline before LLM pairwise judging or human review.",
        "paper_count": len(human_by_paper),
        "generated_weakness_count": len(generated_rows),
        "human_weakness_count": len(human_rows),
        "mean_generated_per_paper": round(len(generated_rows) / len(human_by_paper), 4),
        "generated_category_counts": dict(Counter(row["category"] for row in generated_rows)),
        "generated_severity_counts": dict(Counter(row["severity"] for row in generated_rows)),
        "generic_rate": round(safe_div(sum(1 for text in generated_texts if generic_flag(text)), len(generated_texts)), 4),
        "redundancy_rate": round(redundancy_rate(generated_texts), 4),
        "coverage_by_threshold": [
            evaluate_threshold(generated_by_paper, human_by_paper, threshold)
            for threshold in THRESHOLDS
        ],
        "top_match_examples": top_match_examples(generated_by_paper, human_by_paper),
    }
    write_json(DATA_DIR / "rubric_agent_coverage_metrics.json", payload)
    primary = payload["coverage_by_threshold"][1]
    print(
        "rubric_agent_coverage "
        f"generated={len(generated_rows)} "
        f"recall@0.18={primary['human_weakness_recall']} "
        f"generic_rate={payload['generic_rate']}"
    )


if __name__ == "__main__":
    main()
