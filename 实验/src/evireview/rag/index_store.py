import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from evireview.models.evidence import EvidenceBlock


class IndexIdentity(BaseModel):
    paper_id: str
    parser_version: str
    embedding_model: str
    block_hash: str
    cache_key: str

    @classmethod
    def from_blocks(
        cls,
        paper_id: str,
        parser_version: str,
        embedding_model: str,
        blocks: list[EvidenceBlock],
    ) -> "IndexIdentity":
        payload = [
            {
                "block_id": block.block_id,
                "section": block.section,
                "evidence_type": block.evidence_type,
                "text": block.text,
            }
            for block in blocks
        ]
        block_hash = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()
        cache_key = hashlib.sha256(
            f"{paper_id}\0{parser_version}\0{embedding_model}\0{block_hash}".encode()
        ).hexdigest()
        return cls(
            paper_id=paper_id,
            parser_version=parser_version,
            embedding_model=embedding_model,
            block_hash=block_hash,
            cache_key=cache_key,
        )


class IndexStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def save_manifest(self, identity: IndexIdentity) -> Path:
        path = self.root / identity.cache_key / "manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(identity.model_dump_json(indent=2), encoding="utf-8")
        return path
