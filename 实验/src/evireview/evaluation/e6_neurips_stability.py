import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from evireview.evaluation.end_to_end_report_runner import (
    run_end_to_end_report_baseline,
)
from evireview.models.paper import PaperDocument


WEAKNESS_CUES = (
    "weakness",
    "limitation",
    "concern",
    "lack",
    "missing",
    "unclear",
    "should",
    "need",
    "baseline",
    "ablation",
    "reproduc",
    "limited",
    "however",
)


def run_neurips_stability_experiment(
    processed_root: Path,
    *,
    sample_size: int = 50,
    top_k: int = 3,
) -> dict[str, Any]:
    submissions = load_neurips_submissions(processed_root, sample_size=sample_size)
    component_metrics = {
        "e2": {"status": "available_from_existing_formal_run"},
        "e3": {"status": "available_from_existing_literature_rag_run"},
        "e4": {"status": "available_from_existing_audit_protocol_run"},
        "e5": {"status": "available_from_existing_meta_reviewer_run"},
    }
    result = run_end_to_end_report_baseline(
        submissions,
        [],
        component_metrics,
        top_k=top_k,
    )
    return {
        "protocol": {
            "name": "e6-neurips-2023-stability-v1",
            "sample_size": sample_size,
            "top_k": top_k,
            "gold_boundary": "official review text is used only as a proxy, not strict weakness gold",
            "accept_reject_decision": False,
        },
        "dataset": {
            "papers": len(submissions),
            "reviews": sum(len(item.get("reviews", [])) for item in submissions),
            "source": "dataset/processed/candidate_expansion_2026_06_17",
        },
        "systems": result["systems"],
        "comparison": _comparison(result["systems"]),
        "experiment_verdict": _verdict(result["systems"]),
    }


def load_neurips_submissions(processed_root: Path, *, sample_size: int = 50) -> list[dict]:
    papers_path = processed_root / "neurips_2023_sample_papers.jsonl"
    reviews_path = processed_root / "neurips_2023_review_pool.jsonl"
    reviews_by_paper: dict[str, list[dict]] = defaultdict(list)
    for row in _read_jsonl(reviews_path):
        paper_id = str(row["paper_id"])
        review_index = int(row["review_index"])
        reviews_by_paper[paper_id].append(
            {
                "id": f"neurips2023-review-{review_index}",
                "content": {
                    "weaknesses": extract_weakness_proxy(str(row.get("text") or "")),
                    "rating": None,
                    "confidence": None,
                },
            }
        )

    submissions = []
    for index, row in enumerate(_read_jsonl(papers_path)):
        if index >= sample_size:
            break
        paper = PaperDocument.model_validate(row)
        submissions.append(_submission_from_paper(paper, reviews_by_paper[paper.paper_id]))
    return submissions


def extract_weakness_proxy(review_text: str, *, max_sentences: int = 5) -> str:
    sentences = [
        _clean(sentence)
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", review_text)
        if _clean(sentence)
    ]
    selected = [
        sentence
        for sentence in sentences
        if any(cue in sentence.lower() for cue in WEAKNESS_CUES)
    ]
    if not selected:
        selected = sentences[:max_sentences]
    return "\n".join(selected[:max_sentences])


def _submission_from_paper(paper: PaperDocument, reviews: list[dict]) -> dict:
    content = {
        "title": paper.title,
        "abstract": _section_text(paper, "abstract", fallback=True),
        "keywords": _keywords(paper),
        "primary_area": str(paper.metadata.get("conference") or "machine learning"),
        "method": _section_text(paper, "method"),
        "experiments": _section_text(paper, "experiments"),
        "related_work": _section_text(paper, "related_work"),
        "limitations": _section_text(paper, "limitations"),
    }
    return {
        "paper_id": paper.paper_id,
        "content": content,
        "source_path": paper.source_path,
        "metadata": paper.metadata,
        "reviews": reviews,
    }


def _section_text(paper: PaperDocument, section: str, *, fallback: bool = False) -> str:
    texts = [block.text for block in paper.blocks if block.section == section]
    if not texts and fallback:
        texts = [block.text for block in paper.blocks[:3]]
    return " ".join(texts[:4])[:2_000]


def _keywords(paper: PaperDocument) -> list[str]:
    raw = paper.metadata.get("keywords")
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()][:8]
    if isinstance(raw, str):
        return [item.strip() for item in re.split(r"[,;]", raw) if item.strip()][:8]
    return []


def _comparison(systems: dict[str, dict]) -> dict[str, float]:
    b3 = systems["B3_cue_aware_structured_report"]
    b4 = systems["B4_agent_rag_pipeline_report"]
    b5 = systems["B5_balanced_agent_rag_pipeline_report"]
    return {
        "b5_overlap_delta_vs_b3": round(
            b5["official_weakness_proxy_overlap@k"]
            - b3["official_weakness_proxy_overlap@k"],
            6,
        ),
        "b5_overlap_delta_vs_b4": round(
            b5["official_weakness_proxy_overlap@k"]
            - b4["official_weakness_proxy_overlap@k"],
            6,
        ),
        "b5_aspect_diversity_delta_vs_b4": round(
            b5["aspect_diversity@k"] - b4["aspect_diversity@k"],
            6,
        ),
        "b5_redundancy_delta_vs_b4": round(
            b5["redundancy_rate@k"] - b4["redundancy_rate@k"],
            6,
        ),
    }


def _verdict(systems: dict[str, dict]) -> str:
    comparison = _comparison(systems)
    if (
        comparison["b5_overlap_delta_vs_b4"] > 0
        and comparison["b5_aspect_diversity_delta_vs_b4"] >= 0
    ):
        return "improved_with_proxy_metrics"
    return "failed_with_metrics"


def _read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _clean(text: str) -> str:
    return " ".join(text.split())
