import math
import re
from collections import Counter

from evireview.models.evidence import EvidenceBlock, EvidenceItem


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Retriever:
    def __init__(self, blocks: list[EvidenceBlock], k1: float = 1.5, b: float = 0.75):
        self.blocks = blocks
        self.k1 = k1
        self.b = b
        self.documents = [tokenize(block.text) for block in blocks]
        self.average_length = (
            sum(len(document) for document in self.documents) / len(self.documents)
            if self.documents
            else 0.0
        )
        self.document_frequency = Counter(
            token for document in self.documents for token in set(document)
        )

    def retrieve(self, query: str, top_k: int) -> list[EvidenceItem]:
        query_tokens = tokenize(query)
        scored = [
            (block, self._score(document, query_tokens))
            for block, document in zip(self.blocks, self.documents, strict=True)
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

    def _score(self, document: list[str], query_tokens: list[str]) -> float:
        frequencies = Counter(document)
        score = 0.0
        for token in query_tokens:
            frequency = frequencies[token]
            if frequency == 0:
                continue
            document_frequency = self.document_frequency[token]
            inverse_document_frequency = math.log(
                1 + (len(self.documents) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            denominator = frequency + self.k1 * (
                1 - self.b + self.b * len(document) / max(self.average_length, 1.0)
            )
            score += inverse_document_frequency * frequency * (self.k1 + 1) / denominator
        return score
