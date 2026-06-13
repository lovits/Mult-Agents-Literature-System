import json
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
                weaknesses = item["response"]["Weakness associated with claims"]
                for index, weakness in enumerate(weaknesses):
                    annotation = weakness["Weakness Annotation"]
                    examples.append(
                        ClaimCheckWeakness(
                            example_id=f"{split}:{paper_review_id}:{index}",
                            paper_review_id=paper_review_id,
                            split=split,
                            weakness=weakness["Weakness span"],
                            groundedness_confidence=int(
                                weakness["Weakness confidence score"]
                            ),
                            target_claims=weakness["Target claims"],
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
