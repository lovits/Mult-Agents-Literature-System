import json
from pathlib import Path

from pydantic import BaseModel

from evireview.models.evidence import EvidenceBlock, EvidenceType


PEERQA_TYPE_MAP: dict[str, EvidenceType] = {
    "table": "table_caption",
    "figure": "figure_caption",
    "algorithm": "algorithm",
}


class PeerQAExample(BaseModel):
    question_id: str
    paper_id: str
    question: str
    relevant_evidence_ids: set[str]


class PeerQADataset(BaseModel):
    blocks_by_paper: dict[str, list[EvidenceBlock]]
    examples: list[PeerQAExample]

    @classmethod
    def from_jsonl(cls, papers_path: Path, qa_path: Path) -> "PeerQADataset":
        blocks_by_paper = _load_blocks(papers_path)
        valid_ids = {
            block.block_id for blocks in blocks_by_paper.values() for block in blocks
        }
        examples = _load_examples(qa_path, valid_ids)
        return cls(blocks_by_paper=blocks_by_paper, examples=examples)


def _load_blocks(path: Path) -> dict[str, list[EvidenceBlock]]:
    blocks_by_paper: dict[str, list[EvidenceBlock]] = {}
    current_section: dict[str, str] = {}
    for row in _read_jsonl(path):
        paper_id = row["paper_id"]
        row_type = row.get("type", "paragraph")
        if row_type == "heading":
            current_section[paper_id] = row["content"]
        section = row.get("last_heading") or current_section.get(paper_id) or "Unknown"
        blocks_by_paper.setdefault(paper_id, []).append(
            EvidenceBlock(
                block_id=f"{paper_id}:{row['idx']}",
                paper_id=paper_id,
                section=section,
                evidence_type=PEERQA_TYPE_MAP.get(row_type, "paragraph"),
                text=row["content"],
                ordinal=int(row["idx"]),
            )
        )
    return blocks_by_paper


def _load_examples(path: Path, valid_ids: set[str]) -> list[PeerQAExample]:
    examples = []
    for row in _read_jsonl(path):
        if not row.get("answerable_mapped", False):
            continue
        paper_id = row["paper_id"]
        relevant_ids = {
            f"{paper_id}:{idx}"
            for mapping in row.get("answer_evidence_mapped", [])
            for idx in mapping.get("idx", [])
            if f"{paper_id}:{idx}" in valid_ids
        }
        if relevant_ids:
            examples.append(
                PeerQAExample(
                    question_id=row["question_id"],
                    paper_id=paper_id,
                    question=row["question"],
                    relevant_evidence_ids=relevant_ids,
                )
            )
    return examples


def _read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)
