from collections.abc import Sequence
from typing import Any


DEFAULT_BGE_QUERY_INSTRUCTION = (
    "Represent this sentence for searching relevant passages: "
)


class SentenceTransformerEmbedder:
    def __init__(
        self,
        *,
        model_name: str | None = None,
        revision: str | None = None,
        device: str = "cpu",
        local_files_only: bool = True,
        query_instruction: str = DEFAULT_BGE_QUERY_INSTRUCTION,
        model: Any = None,
    ):
        if model is None:
            if not model_name:
                raise ValueError("model_name is required when model is not injected")
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(
                model_name,
                revision=revision,
                device=device,
                local_files_only=local_files_only,
            )
        self.model = model
        self.query_instruction = query_instruction
        self._document_cache: dict[str, list[float]] = {}
        self._query_cache: dict[str, list[float]] = {}

    def embed_document(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        missing = list(dict.fromkeys(text for text in texts if text not in self._document_cache))
        if missing:
            vectors = self.model.encode(missing, normalize_embeddings=True)
            self._document_cache.update(zip(missing, _to_vectors(vectors), strict=True))
        return [self._document_cache[text] for text in texts]

    def embed_query(self, text: str) -> list[float]:
        if text not in self._query_cache:
            vector = self.model.encode(
                f"{self.query_instruction}{text}",
                normalize_embeddings=True,
            )
            self._query_cache[text] = _to_vector(vector)
        return self._query_cache[text]


def _to_vectors(values: Any) -> list[list[float]]:
    converted = values.tolist() if hasattr(values, "tolist") else values
    return [list(vector) for vector in converted]


def _to_vector(value: Any) -> list[float]:
    converted = value.tolist() if hasattr(value, "tolist") else value
    return list(converted)
