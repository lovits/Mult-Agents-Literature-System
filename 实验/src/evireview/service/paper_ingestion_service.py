import hashlib
import re
from pathlib import Path

from evireview.models.evidence import EvidenceBlock, EvidenceType
from evireview.models.paper import PaperDocument


SECTION_ALIASES = {
    "abstract": "abstract",
    "introduction": "introduction",
    "related work": "related_work",
    "background": "related_work",
    "method": "method",
    "methodology": "method",
    "approach": "method",
    "experiments": "experiments",
    "experiment": "experiments",
    "results": "experiments",
    "ablation": "ablation",
    "limitations": "limitations",
    "conclusion": "conclusion",
}


def normalize_section(heading: str) -> str:
    lowered = re.sub(r"^\d+(?:\.\d+)*\s*", "", heading).strip().lower()
    if lowered.startswith("appendix"):
        return "appendix"
    return SECTION_ALIASES.get(lowered, lowered.replace(" ", "_"))


def classify_evidence(text: str, section: str, is_heading: bool) -> EvidenceType:
    lowered = text.lower()
    if section == "appendix":
        return "appendix"
    if lowered.startswith("table ") or lowered.startswith("table:"):
        return "table_caption"
    if lowered.startswith("figure ") or lowered.startswith("figure:"):
        return "figure_caption"
    if (is_heading and lowered.startswith("algorithm")) or lowered.startswith("algorithm "):
        return "algorithm"
    return "paragraph"


class PaperIngestionService:
    def from_markdown(self, source_path: str | Path, paper_id: str) -> PaperDocument:
        path = Path(source_path)
        lines = path.read_text(encoding="utf-8").splitlines()
        title = path.stem
        section = "front_matter"
        sections: list[str] = []
        blocks: list[EvidenceBlock] = []
        paragraph: list[str] = []

        def add_block(text: str, *, is_heading: bool = False) -> None:
            cleaned = " ".join(text.split())
            if not cleaned:
                return
            ordinal = len(blocks)
            fingerprint = f"{paper_id}\0{ordinal}\0{section}\0{cleaned}".encode()
            blocks.append(
                EvidenceBlock(
                    block_id=f"{paper_id}:b{hashlib.sha1(fingerprint).hexdigest()[:12]}",
                    paper_id=paper_id,
                    section=section,
                    evidence_type=classify_evidence(cleaned, section, is_heading),
                    text=cleaned,
                    ordinal=ordinal,
                )
            )

        def flush_paragraph() -> None:
            if paragraph:
                add_block(" ".join(paragraph))
                paragraph.clear()

        for line in lines:
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                flush_paragraph()
                heading_text = heading.group(2).strip()
                if len(heading.group(1)) == 1:
                    title = heading_text
                    continue
                if heading_text.lower().startswith("algorithm"):
                    add_block(heading_text, is_heading=True)
                    continue
                section = normalize_section(heading_text)
                if section not in sections:
                    sections.append(section)
                continue
            if not line.strip():
                flush_paragraph()
                continue
            if re.match(r"^(Table|Figure|Algorithm)\s+\d+", line.strip(), re.IGNORECASE):
                flush_paragraph()
                add_block(line.strip())
                continue
            paragraph.append(line.strip())
        flush_paragraph()

        return PaperDocument(
            paper_id=paper_id,
            title=title,
            source_path=str(path),
            sections=sections,
            blocks=blocks,
            metadata={"parser": "markdown-v1"},
        )
