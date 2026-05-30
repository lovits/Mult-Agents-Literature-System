from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from common import DATA_DIR, ensure_dirs, read_jsonl, tokenize, write_json, write_jsonl


GENERATOR = "rubric_agent_v0"


RUBRICS = {
    "experiment": {
        "role": "experiment_reviewer",
        "severity": "major",
        "template": "The empirical evaluation may be under-specified: {reason}. This makes it harder to judge whether the reported gains are robust.",
    },
    "method": {
        "role": "method_reviewer",
        "severity": "major",
        "template": "The method section may need stronger technical justification: {reason}. This could make the proposed approach difficult to assess or reproduce.",
    },
    "related_work": {
        "role": "novelty_reviewer",
        "severity": "major",
        "template": "The paper's novelty positioning may be incomplete: {reason}. A clearer comparison to prior work would make the contribution easier to verify.",
    },
    "reproducibility": {
        "role": "reproducibility_reviewer",
        "severity": "minor",
        "template": "The reproducibility details may be insufficient: {reason}. More implementation and hyperparameter detail would improve auditability.",
    },
    "limitation": {
        "role": "validity_reviewer",
        "severity": "minor",
        "template": "The limitations discussion may be too thin: {reason}. A stronger discussion of failure modes would improve the reviewer's confidence.",
    },
    "clarity": {
        "role": "clarity_reviewer",
        "severity": "minor",
        "template": "The presentation may need tightening: {reason}. This can obscure the paper's main technical claims for reviewers.",
    },
}


KEYWORDS = {
    "ablation": ("ablation", "ablated", "sensitivity", "component analysis"),
    "baseline": ("baseline", "compare", "comparison", "state-of-the-art", "sota"),
    "reproducibility": ("hyperparameter", "implementation", "code", "seed", "reproduc", "training details"),
    "limitation": ("limitation", "failure", "future work", "discussion"),
    "theory": ("proof", "theorem", "lemma", "proposition", "derive", "bound"),
}


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in keywords)


def count_any(text: str, keywords: tuple[str, ...]) -> int:
    lower = text.lower()
    return sum(lower.count(keyword) for keyword in keywords)


def compact_reason(reason: str) -> str:
    reason = re.sub(r"\s+", " ", reason).strip()
    return reason[0].lower() + reason[1:] if reason else reason


def top_blocks(blocks: list[dict[str, Any]], section_type: str, limit: int = 2) -> list[str]:
    filtered = [block for block in blocks if block["section_type"] == section_type]
    filtered.sort(key=lambda block: block["token_count"], reverse=True)
    return [block["block_id"] for block in filtered[:limit]]


def paper_signals(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    by_section: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in blocks:
        by_section[block["section_type"]].append(block)
    section_tokens = {
        section: sum(int(block["token_count"]) for block in section_blocks)
        for section, section_blocks in by_section.items()
    }
    section_text = {
        section: " ".join(block["text"] for block in section_blocks)
        for section, section_blocks in by_section.items()
    }
    all_text = " ".join(block["text"] for block in blocks)
    return {
        "by_section": by_section,
        "section_tokens": section_tokens,
        "section_text": section_text,
        "all_text": all_text,
        "section_counts": Counter(block["section_type"] for block in blocks),
    }


def candidate_rules(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signals = paper_signals(blocks)
    section_tokens = signals["section_tokens"]
    section_text = signals["section_text"]
    all_text = signals["all_text"]
    candidates = []

    experiment_text = section_text.get("experiment", "")
    experiment_tokens = section_tokens.get("experiment", 0)
    if experiment_tokens < 900:
        candidates.append(
            {
                "category": "experiment",
                "score": 0.92,
                "reason": f"the experiment section is short ({experiment_tokens} tokens) relative to the paper and may not provide enough empirical detail",
                "evidence_block_ids": top_blocks(blocks, "experiment") or top_blocks(blocks, "method"),
            }
        )
    if not contains_any(experiment_text, KEYWORDS["ablation"]):
        candidates.append(
            {
                "category": "experiment",
                "score": 0.86,
                "reason": "the retrieved experiment sections do not contain explicit ablation or sensitivity-analysis signals",
                "evidence_block_ids": top_blocks(blocks, "experiment") or top_blocks(blocks, "method"),
            }
        )
    if count_any(experiment_text, KEYWORDS["baseline"]) < 2:
        candidates.append(
            {
                "category": "experiment",
                "score": 0.82,
                "reason": "baseline-comparison terms are sparse in the experiment sections",
                "evidence_block_ids": top_blocks(blocks, "experiment") or top_blocks(blocks, "introduction"),
            }
        )

    method_tokens = section_tokens.get("method", 0)
    if method_tokens < 1200:
        candidates.append(
            {
                "category": "method",
                "score": 0.78,
                "reason": f"the method section has limited technical detail ({method_tokens} tokens)",
                "evidence_block_ids": top_blocks(blocks, "method"),
            }
        )
    if contains_any(all_text, KEYWORDS["theory"]) and count_any(section_text.get("method", ""), KEYWORDS["theory"]) < 3:
        candidates.append(
            {
                "category": "method",
                "score": 0.72,
                "reason": "the paper appears to make formal or theoretical claims, but theory-related terms are sparse in the method evidence",
                "evidence_block_ids": top_blocks(blocks, "method") or top_blocks(blocks, "introduction"),
            }
        )

    related_tokens = section_tokens.get("related_work", 0)
    if related_tokens < 700:
        candidates.append(
            {
                "category": "related_work",
                "score": 0.8,
                "reason": f"the related-work evidence is short ({related_tokens} tokens), which may weaken novelty positioning",
                "evidence_block_ids": top_blocks(blocks, "related_work") or top_blocks(blocks, "introduction"),
            }
        )

    if count_any(all_text, KEYWORDS["reproducibility"]) < 4:
        candidates.append(
            {
                "category": "reproducibility",
                "score": 0.76,
                "reason": "implementation, code, seed, or hyperparameter signals are sparse in the paper text",
                "evidence_block_ids": top_blocks(blocks, "method") or top_blocks(blocks, "appendix"),
            }
        )

    limitation_tokens = section_tokens.get("limitation", 0)
    if limitation_tokens < 250:
        candidates.append(
            {
                "category": "limitation",
                "score": 0.7,
                "reason": f"the limitation section is absent or short ({limitation_tokens} tokens)",
                "evidence_block_ids": top_blocks(blocks, "limitation") or top_blocks(blocks, "conclusion"),
            }
        )

    abstract_tokens = section_tokens.get("abstract", 0)
    intro_tokens = section_tokens.get("introduction", 0)
    if abstract_tokens > 0 and intro_tokens < 500:
        candidates.append(
            {
                "category": "clarity",
                "score": 0.64,
                "reason": "the introduction evidence is short relative to the abstract and may not fully unpack the motivation",
                "evidence_block_ids": top_blocks(blocks, "introduction") or top_blocks(blocks, "abstract"),
            }
        )
    return candidates


def render_weakness(candidate: dict[str, Any]) -> str:
    rubric = RUBRICS[candidate["category"]]
    return rubric["template"].format(reason=compact_reason(candidate["reason"]))


def main() -> None:
    ensure_dirs()
    blocks_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[block["paper_id"]].append(block)

    generated = []
    for paper_id, blocks in sorted(blocks_by_paper.items()):
        blocks.sort(key=lambda item: item["block_id"])
        title = blocks[0]["title"]
        ranked = sorted(candidate_rules(blocks), key=lambda item: item["score"], reverse=True)
        seen_categories = Counter()
        selected = []
        for candidate in ranked:
            if seen_categories[candidate["category"]] >= 2:
                continue
            selected.append(candidate)
            seen_categories[candidate["category"]] += 1
            if len(selected) == 5:
                break
        for index, candidate in enumerate(selected, start=1):
            rubric = RUBRICS[candidate["category"]]
            generated.append(
                {
                    "generated_weakness_id": f"{paper_id}_{GENERATOR}_{index:02d}",
                    "paper_id": paper_id,
                    "forum": blocks[0]["forum"],
                    "paper_index": blocks[0]["paper_index"],
                    "title": title,
                    "decision": blocks[0]["decision"],
                    "weakness_text": render_weakness(candidate),
                    "category": candidate["category"],
                    "severity": rubric["severity"],
                    "confidence": round(candidate["score"], 4),
                    "reviewer_role": rubric["role"],
                    "evidence_block_ids": candidate["evidence_block_ids"],
                    "generator": GENERATOR,
                    "generation_note": "Deterministic rubric-agent baseline from paper structure and evidence-block signals; not an LLM result.",
                }
            )

    write_jsonl(DATA_DIR / "rubric_agent_weaknesses.jsonl", generated)
    summary = {
        "generator": GENERATOR,
        "paper_count": len(blocks_by_paper),
        "generated_weakness_count": len(generated),
        "mean_generated_per_paper": round(len(generated) / len(blocks_by_paper), 4),
        "category_counts": dict(Counter(item["category"] for item in generated)),
        "severity_counts": dict(Counter(item["severity"] for item in generated)),
        "warning": "This is a deterministic rubric-agent baseline for pipeline validation; it is not a final LLM reviewer.",
    }
    write_json(DATA_DIR / "rubric_agent_weaknesses_summary.json", summary)
    print(f"generated={len(generated)} papers={len(blocks_by_paper)}")


if __name__ == "__main__":
    main()
