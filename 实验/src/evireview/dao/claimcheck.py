import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ClaimCheckWeakness(BaseModel):
    example_id: str
    paper_review_id: str
    split: Literal["main", "pilot"]
    weakness: str
    groundedness_confidence: int = Field(ge=1, le=5)
    target_claims: list[str]
    paper_texts: list[str]
    relevant_text_ids: set[str]
    exclusion_reason: str | None = None
    subjectivity: int = Field(ge=1, le=5)
    agreement: int = Field(ge=1, le=5)
    weakness_types: set[str]


class ClaimCheckDataset(BaseModel):
    examples: list[ClaimCheckWeakness]
    paper_review_pairs: int

    @classmethod
    def from_source_dir(cls, source_dir: str | Path) -> "ClaimCheckDataset":
        root = Path(source_dir)
        examples = []
        paper_review_pairs = 0
        for split in ("main", "pilot"):
            payload = json.loads((root / f"{split}.json").read_text(encoding="utf-8"))
            paper_review_pairs += len(payload)
            for paper_review_id, item in payload.items():
                paper_texts = item["meta"]["text"]
                weaknesses = item["response"]["Weakness associated with claims"]
                for index, weakness in enumerate(weaknesses):
                    annotation = weakness["Weakness Annotation"]
                    target_claims = weakness["Target claims"]
                    relevant_text_ids = _map_target_claims(
                        paper_review_id,
                        paper_texts,
                        target_claims,
                    )
                    examples.append(
                        ClaimCheckWeakness(
                            example_id=f"{split}:{paper_review_id}:{index}",
                            paper_review_id=paper_review_id,
                            split=split,
                            weakness=weakness["Weakness span"],
                            groundedness_confidence=int(
                                weakness["Weakness confidence score"]
                            ),
                            target_claims=target_claims,
                            paper_texts=paper_texts,
                            relevant_text_ids=relevant_text_ids,
                            exclusion_reason=(
                                None
                                if relevant_text_ids
                                else (
                                    "no_target_claim"
                                    if not target_claims
                                    else "target_claim_not_mapped"
                                )
                            ),
                            subjectivity=int(annotation["subjectivity"]),
                            agreement=int(annotation["agreement"]),
                            weakness_types={
                                name
                                for name, enabled in annotation["weakness_type"].items()
                                if enabled
                            },
                        )
                    )
        return cls(examples=examples, paper_review_pairs=paper_review_pairs)

    def audit_summary(self) -> dict:
        return {
            "paper_review_pairs": self.paper_review_pairs,
            "weaknesses": len(self.examples),
            "main_weaknesses": sum(
                example.split == "main" for example in self.examples
            ),
            "pilot_weaknesses": sum(
                example.split == "pilot" for example in self.examples
            ),
            "main_mapped_weaknesses": sum(
                example.split == "main" and bool(example.relevant_text_ids)
                for example in self.examples
            ),
            "pilot_mapped_weaknesses": sum(
                example.split == "pilot" and bool(example.relevant_text_ids)
                for example in self.examples
            ),
            "target_claim_grounded_weaknesses": sum(
                bool(example.target_claims) for example in self.examples
            ),
            "supports": {
                "claim_association": True,
                "weakness_labeling": True,
                "groundedness_confidence": True,
                "covered_refuted_gold": False,
            },
        }


def _map_target_claims(
    paper_review_id: str,
    paper_texts: list[str],
    target_claims: list[str],
) -> set[str]:
    normalized_texts = [_normalize(text) for text in paper_texts]
    return {
        f"{paper_review_id}:{index}"
        for target in target_claims
        for index, text in enumerate(normalized_texts)
        if _normalize(target) in text
    }


def _normalize(text: str) -> str:
    without_claim_prefix = re.sub(r"^\s*claim\s*\d+\s*:\s*", "", text, flags=re.I)
    return re.sub(r"\s+", " ", without_claim_prefix).strip().lower()
