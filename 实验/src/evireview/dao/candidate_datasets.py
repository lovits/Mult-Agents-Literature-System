import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from evireview.models.evidence import EvidenceBlock, EvidenceType
from evireview.models.paper import PaperDocument


SECTION_KEYWORDS = {
    "abstract": "abstract",
    "introduction": "introduction",
    "background": "related_work",
    "related work": "related_work",
    "method": "method",
    "methods": "method",
    "approach": "method",
    "model": "method",
    "experiments": "experiments",
    "experiment": "experiments",
    "evaluation": "experiments",
    "results": "experiments",
    "ablation": "ablation",
    "analysis": "discussion",
    "discussion": "discussion",
    "limitations": "limitations",
    "conclusion": "conclusion",
    "appendix": "appendix",
}


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def coerce_review_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [text for item in value for text in coerce_review_list(item)]
    if isinstance(value, dict):
        return [json.dumps(value, ensure_ascii=False)]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("[") or text.startswith("{"):
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        return coerce_review_list(decoded)
    return [text]


def paper_from_neurips_record(record: dict[str, Any], max_blocks: int = 120) -> PaperDocument:
    paper_id = str(record["paper_id"])
    paper_text = str(record.get("paper_text") or "")
    blocks = split_paper_text(paper_id, paper_text, max_blocks=max_blocks)
    if not blocks:
        blocks = [
            EvidenceBlock(
                block_id=f"{paper_id}:metadata:0000",
                paper_id=paper_id,
                section="metadata",
                evidence_type="paragraph",
                text=_clean(str(record.get("abstract") or record.get("title") or paper_id)),
                ordinal=0,
            )
        ]
    return PaperDocument(
        paper_id=paper_id,
        title=_clean(str(record.get("title") or paper_id)),
        source_path=str(record.get("pdf_url") or ""),
        sections=list(dict.fromkeys(block.section for block in blocks)),
        blocks=blocks,
        metadata={
            "dataset": "djroytburg/NeurIPS-2023-2025",
            "year": record.get("year"),
            "conference": record.get("conference"),
            "accepted": record.get("accepted"),
            "keywords": record.get("keywords"),
            "pdf_url": record.get("pdf_url"),
            "review_count": len(coerce_review_list(record.get("reviews"))),
        },
    )


def split_paper_text(
    paper_id: str, paper_text: str, *, max_blocks: int = 120
) -> list[EvidenceBlock]:
    section = "front_matter"
    blocks: list[EvidenceBlock] = []
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal paragraph
        text = _clean(" ".join(paragraph))
        paragraph = []
        if not text:
            return
        ordinal = len(blocks)
        blocks.append(
            EvidenceBlock(
                block_id=_block_id(paper_id, section, ordinal, text),
                paper_id=paper_id,
                section=section,
                evidence_type=_evidence_type(section, text),
                text=text,
                ordinal=ordinal,
            )
        )

    for raw_line in paper_text.splitlines():
        line = _clean(raw_line)
        if not line:
            flush()
            if len(blocks) >= max_blocks:
                break
            continue
        maybe_section = detect_section(line)
        if maybe_section and len(line) <= 120:
            flush()
            section = maybe_section
            continue
        paragraph.append(line)
        if len(" ".join(paragraph)) > 1_200:
            flush()
        if len(blocks) >= max_blocks:
            break
    flush()
    return blocks[:max_blocks]


def detect_section(line: str) -> str | None:
    cleaned = re.sub(r"^\d+(?:\.\d+)*\s*", "", line).strip().lower().rstrip(":")
    cleaned = re.sub(r"[^a-z ]", "", cleaned)
    if cleaned.startswith("appendix"):
        return "appendix"
    return SECTION_KEYWORDS.get(cleaned)


def reviewrebuttal_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    decision_counts: Counter[str] = Counter()
    review_counts: list[int] = []
    rating_records = 0
    metareview_present = 0
    for row in payload:
        decision = _clean(str(row.get("decision") or "unknown")).lower() or "unknown"
        decision_counts[decision] += 1
        reviews = row.get("reviews") or []
        review_counts.append(len(reviews) if isinstance(reviews, list) else 0)
        if row.get("metareview"):
            metareview_present += 1
        rating_records += len(row.get("review_initial_ratings_unified") or [])
        rating_records += len(row.get("review_final_ratings_unified") or [])
    return {
        "papers": len(payload),
        "reviews": sum(review_counts),
        "mean_reviews_per_paper": round(sum(review_counts) / max(len(review_counts), 1), 4),
        "metareview_present": metareview_present,
        "rating_records": rating_records,
        "decision_counts": dict(sorted(decision_counts.items())),
    }


def peercheck_summary(path: Path) -> dict[str, Any]:
    rows = list(read_jsonl(path))
    citation_markers = 0
    weakness_sections = 0
    score_mentions = 0
    for row in rows:
        answer = str(row.get("answer") or "")
        citation_markers += len(re.findall(r"【[^】]+】", answer))
        if "Weaknesses" in answer:
            weakness_sections += 1
        if re.search(r"Overall Score:\s*\d", answer):
            score_mentions += 1
    return {
        "rows": len(rows),
        "citation_markers": citation_markers,
        "weakness_sections": weakness_sections,
        "overall_score_mentions": score_mentions,
    }


def _block_id(paper_id: str, section: str, ordinal: int, text: str) -> str:
    digest = hashlib.sha1(f"{paper_id}\0{section}\0{ordinal}\0{text}".encode()).hexdigest()
    return f"{paper_id}:n23:{digest[:12]}"


def _evidence_type(section: str, text: str) -> EvidenceType:
    lower = text.lower()
    if section == "appendix":
        return "appendix"
    if lower.startswith("table") or " table " in f" {lower} ":
        return "table_caption"
    if lower.startswith("figure") or " figure " in f" {lower} ":
        return "figure_caption"
    if "algorithm" in lower:
        return "algorithm"
    if "implementation" in lower or "hyperparameter" in lower or "random seed" in lower:
        return "implementation_detail"
    return "paragraph"


def _clean(text: str) -> str:
    return " ".join(text.split())
