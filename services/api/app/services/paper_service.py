from __future__ import annotations

import hashlib
from typing import Any

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from evireview_core.parsing.markdown_sections import chunk_text, iter_sections


def _stable_id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256("\x1f".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


class PaperService:
    def __init__(self, repository: SQLiteRunRepository) -> None:
        self.repository = repository

    def import_markdown(self, paper_id: str, title: str, markdown: str) -> dict[str, Any]:
        sections: list[dict[str, Any]] = []
        blocks: list[dict[str, Any]] = []
        for section_ordinal, section in enumerate(iter_sections(markdown)):
            section_id = _stable_id("section", paper_id, section_ordinal, section.section_path, section.text)
            sections.append(
                {
                    "section_id": section_id,
                    "paper_id": paper_id,
                    "ordinal": section_ordinal,
                    "section_path": section.section_path,
                    "section_type": section.section_type,
                    "text": section.text,
                }
            )
            for chunk_ordinal, text in enumerate(chunk_text(section.text, min_tokens=1)):
                blocks.append(
                    {
                        "block_id": _stable_id("block", paper_id, section_ordinal, chunk_ordinal, section.section_path, text),
                        "paper_id": paper_id,
                        "ordinal": len(blocks),
                        "section_path": section.section_path,
                        "section_type": section.section_type,
                        "text": text,
                        "score": 0.0,
                    }
                )
        if not sections:
            raise ValueError("markdown must contain usable text")
        self.repository.replace_paper_assets(paper_id, title, sections, blocks)
        return {
            **self.get_paper(paper_id),
            "section_count": len(sections),
            "evidence_block_count": len(blocks),
        }

    def get_paper(self, paper_id: str) -> dict[str, Any]:
        return self.repository.get_paper(paper_id)

    def get_sections(self, paper_id: str) -> list[dict[str, Any]]:
        self.repository.get_paper(paper_id)
        return self.repository.list_paper_sections(paper_id)

    def get_evidence_blocks(self, paper_id: str) -> list[dict[str, Any]]:
        self.repository.get_paper(paper_id)
        return [
            {key: value for key, value in block.items() if key != "ordinal"}
            for block in self.repository.list_evidence_blocks(paper_id)
        ]
