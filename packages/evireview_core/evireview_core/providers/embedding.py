from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from typing import Any


EmbeddingTransport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


def _urllib_transport(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


class OpenAICompatibleEmbedder:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        transport: EmbeddingTransport | None = None,
    ) -> None:
        if not base_url or not api_key or not model:
            raise ValueError("embedding base URL, API key, and model are required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.transport = transport or _urllib_transport

    @classmethod
    def from_env(cls) -> "OpenAICompatibleEmbedder":
        return cls(
            base_url=os.getenv("EVIREVIEW_EMBEDDING_BASE_URL", ""),
            api_key=os.getenv("EVIREVIEW_EMBEDDING_API_KEY", ""),
            model=os.getenv("EVIREVIEW_EMBEDDING_MODEL", ""),
        )

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.transport(
            f"{self.base_url}/embeddings",
            {"Authorization": f"Bearer {self.api_key}"},
            {"model": self.model, "input": texts},
        )
        rows = sorted(response.get("data", []), key=lambda item: int(item["index"]))
        vectors = [[float(value) for value in item["embedding"]] for item in rows]
        if len(vectors) != len(texts):
            raise ValueError("embedding provider must return one vector per input text")
        return vectors
