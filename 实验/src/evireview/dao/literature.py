import re
from pathlib import Path

from pydantic import BaseModel

from evireview.models.evidence import EvidenceBlock


CURATED_YEAR_HINTS = {
    "marg": 2024,
    "peerread": 2018,
    "factreview": 2026,
    "opennovelty": 2026,
    "noveltyagent": 2026,
    "reviewgrounder": 2026,
    "rottenreviews": 2025,
    "deepreview": 2025,
    "reviewagents": 2025,
    "scholarpeer": 2026,
    "agentreview": 2024,
    "useful-feedback": 2024,
    "llms-provide-useful-feedback": 2024,
    "reliable-reviewer": 2025,
    "substanreview": 2023,
    "can-we-automate-scientific-reviewing": 2018,
}


class LiteratureDocument(BaseModel):
    doc_id: str
    title: str
    year: int | None
    source_path: str
    text: str

    @property
    def citation_metadata_complete(self) -> bool:
        return bool(self.title and self.year and self.source_path)


class LiteratureCorpus(BaseModel):
    source_path: str
    documents: list[LiteratureDocument]

    @classmethod
    def from_source_dir(cls, source_dir: str | Path) -> "LiteratureCorpus":
        root = Path(source_dir)
        resolved = root.resolve()
        documents = [
            _document_from_markdown(path, resolved)
            for path in sorted(resolved.rglob("*.md"))
            if path.is_file()
        ]
        return cls(source_path=str(root), documents=documents)

    def audit_summary(self) -> dict:
        metadata_complete = sum(
            document.citation_metadata_complete for document in self.documents
        )
        years = [document.year for document in self.documents if document.year]
        return {
            "source_path": self.source_path,
            "source_exists": Path(self.source_path).exists(),
            "markdown_docs": len(self.documents),
            "metadata_complete_docs": metadata_complete,
            "min_year": min(years) if years else None,
            "max_year": max(years) if years else None,
        }

    def to_evidence_blocks(self) -> list[EvidenceBlock]:
        return [
            EvidenceBlock(
                block_id=f"{document.doc_id}:abstract",
                paper_id=f"lit:{document.doc_id}",
                section="literature",
                evidence_type="paragraph",
                text=f"{document.title}\n\n{document.text}",
                ordinal=index,
            )
            for index, document in enumerate(self.documents)
        ]

    def find_by_title_keyword(self, keyword: str) -> LiteratureDocument:
        normalized = keyword.lower()
        for document in self.documents:
            if normalized in document.title.lower() or normalized in document.doc_id.lower():
                return document
        raise ValueError(f"No literature document matches title keyword: {keyword}")


def _document_from_markdown(path: Path, root: Path) -> LiteratureDocument:
    text = path.read_text(encoding="utf-8", errors="ignore")
    relative = path.relative_to(root)
    title = _extract_title(text) or _title_from_path(path)
    return LiteratureDocument(
        doc_id=_doc_id(relative),
        title=title,
        year=_extract_year(str(relative), text),
        source_path=str(path),
        text=text,
    )


def _doc_id(relative_path: Path) -> str:
    raw = str(relative_path.with_suffix(""))
    return re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def _title_from_path(path: Path) -> str:
    title = re.sub(r"^\d+_", "", path.stem)
    title = re.sub(r"_(?:19|20)\d{2}$", "", title)
    title = re.sub(r"_[2-9]\d{3}\.\d+$", "", title)
    return title.replace("_", " ").strip()


def _extract_year(relative_path: str, text: str) -> int | None:
    explicit = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", relative_path)
    if explicit:
        return int(explicit.group(1))
    arxiv = re.search(r"(?<!\d)(2[3-6])\d{2}\.\d+", relative_path)
    if arxiv:
        return 2000 + int(arxiv.group(1))
    body = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", text[:2000])
    if body:
        return int(body.group(1))
    normalized_path = relative_path.lower().replace("_", "-")
    for keyword, year in CURATED_YEAR_HINTS.items():
        if keyword in normalized_path:
            return year
    return None
