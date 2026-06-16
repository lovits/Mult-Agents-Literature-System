import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class SubstanEvidenceSpan(BaseModel):
    start: int
    end: int
    text: str


class SubstanClaim(BaseModel):
    claim_id: str
    review_id: str
    split: Literal["train", "test"]
    review: str
    polarity: Literal["positive", "negative", "major"]
    claim_start: int
    claim_end: int
    claim_text: str
    evidence_spans: list[SubstanEvidenceSpan]

    @property
    def supported(self) -> bool:
        return bool(self.evidence_spans)


class SubstanReviewDataset(BaseModel):
    review_counts: dict[str, int]
    claims: list[SubstanClaim]

    @classmethod
    def from_source_dir(cls, source_dir: str | Path) -> "SubstanReviewDataset":
        root = Path(source_dir)
        claims = []
        review_counts = {}
        for split in ("train", "test"):
            rows = [
                json.loads(line)
                for line in (root / f"{split}.jsonl").read_text(
                    encoding="utf-8"
                ).splitlines()
                if line.strip()
            ]
            review_counts[split] = len(rows)
            for row in rows:
                claims.extend(_claims_from_row(row, split))
        return cls(review_counts=review_counts, claims=claims)

    def audit_summary(self) -> dict:
        return {
            "reviews": sum(self.review_counts.values()),
            "train_reviews": self.review_counts.get("train", 0),
            "test_reviews": self.review_counts.get("test", 0),
            "claims": len(self.claims),
            "supported_claims": sum(claim.supported for claim in self.claims),
            "supports": {
                "claim_evidence_substantiation": True,
                "weakness_validity": False,
                "covered_refuted_gold": False,
            },
        }


def _claims_from_row(row: dict, split: str) -> list[SubstanClaim]:
    review = row["review"]
    labels = row["label"]
    evidence_by_label: dict[str, list[SubstanEvidenceSpan]] = {}
    for start, end, label in labels:
        if label.startswith("Jus_"):
            evidence_by_label.setdefault(label.removeprefix("Jus_"), []).append(
                SubstanEvidenceSpan(start=start, end=end, text=review[start:end])
            )
    claims = []
    for index, (start, end, label) in enumerate(labels):
        if not (label.startswith("Eval_") or label == "Major_claim"):
            continue
        relation = label.removeprefix("Eval_") if label.startswith("Eval_") else None
        polarity = (
            "positive"
            if label.startswith("Eval_pos")
            else "negative"
            if label.startswith("Eval_neg")
            else "major"
        )
        claims.append(
            SubstanClaim(
                claim_id=f"{split}:{row['id']}:{index}",
                review_id=f"{split}:{row['id']}",
                split=split,
                review=review,
                polarity=polarity,
                claim_start=start,
                claim_end=end,
                claim_text=review[start:end],
                evidence_spans=evidence_by_label.get(relation, []),
            )
        )
    return claims
