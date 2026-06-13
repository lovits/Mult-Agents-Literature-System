import math
from collections.abc import Callable, Sequence

from evireview.models.evidence import EvidenceBlock, EvidenceItem


Vector = list[float]


def cosine_similarity(left: Vector, right: Vector) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class DenseRetriever:
    def __init__(
        self,
        blocks: list[EvidenceBlock],
        embed: Callable[[str], Vector],
        *,
        query_embed: Callable[[str], Vector] | None = None,
        embed_many: Callable[[Sequence[str]], list[Vector]] | None = None,
    ):
        self.blocks = blocks
        self.query_embed = query_embed or embed
        texts = [block.text for block in blocks]
        self.vectors = embed_many(texts) if embed_many else [embed(text) for text in texts]

    def retrieve(self, query: str, top_k: int) -> list[EvidenceItem]:
        query_vector = self.query_embed(query)
        scored = [
            (block, cosine_similarity(query_vector, vector))
            for block, vector in zip(self.blocks, self.vectors, strict=True)
        ]
        scored.sort(key=lambda item: (-item[1], item[0].ordinal))
        return [
            EvidenceItem(
                evidence_id=block.block_id,
                source="paper",
                text=block.text,
                score=score,
                section=block.section,
                document_id=block.paper_id,
            )
            for block, score in scored[:top_k]
        ]
