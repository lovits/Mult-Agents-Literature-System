import re
from collections.abc import Mapping
from typing import Any

from evireview.models.evidence import EvidenceBlock, EvidenceType
from evireview.models.paper import PaperDocument


SECTION_FIELDS = (
    "abstract",
    "introduction",
    "related_work",
    "method",
    "experiments",
    "evaluation",
    "ablation",
    "results",
    "discussion",
    "limitations",
    "appendix",
)


def paper_from_submission(submission: Mapping[str, Any]) -> PaperDocument:
    """Builds a minimal PaperDocument from OpenReview-like content dictionaries."""

    paper_id = str(submission["paper_id"])
    content = submission.get("content", {})
    if not isinstance(content, Mapping):
        content = {}
    title = _clean(str(content.get("title") or submission.get("title") or paper_id))
    blocks: list[EvidenceBlock] = []
    ordinal = 0
    for field in SECTION_FIELDS:
        value = content.get(field)
        for paragraph_index, text in enumerate(_paragraphs(value)):
            blocks.append(
                EvidenceBlock(
                    block_id=f"{paper_id}:content:{field}:{paragraph_index}",
                    paper_id=paper_id,
                    section=_section_name(field),
                    evidence_type=_evidence_type(field, text),
                    text=text,
                    ordinal=ordinal,
                )
            )
            ordinal += 1
    if not blocks:
        fallback = _clean(" ".join(str(value) for value in content.values() if value))
        blocks.append(
            EvidenceBlock(
                block_id=f"{paper_id}:content:metadata:0",
                paper_id=paper_id,
                section="metadata",
                evidence_type="paragraph",
                text=fallback or title,
                ordinal=0,
            )
        )
    return PaperDocument(
        paper_id=paper_id,
        title=title,
        source_path=str(submission.get("source_path", "")),
        sections=list(dict.fromkeys(block.section for block in blocks)),
        blocks=blocks,
        metadata=dict(submission.get("metadata", {})),
    )


def _paragraphs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        values = value
    else:
        values = re.split(r"\n\s*\n", str(value))
    return [_clean(str(item)) for item in values if _clean(str(item))]


def _section_name(field: str) -> str:
    return field.replace("_", " ")


def _evidence_type(field: str, text: str) -> EvidenceType:
    lower = text.lower()
    if field == "appendix":
        return "appendix"
    if "algorithm" in lower or field == "method" and "step" in lower:
        return "algorithm"
    if "implementation" in lower or "hyperparameter" in lower or "seed" in lower:
        return "implementation_detail"
    if lower.startswith("table") or " table " in f" {lower} ":
        return "table_caption"
    if lower.startswith("figure") or " figure " in f" {lower} ":
        return "figure_caption"
    return "paragraph"


def _clean(text: str) -> str:
    return " ".join(text.split())
