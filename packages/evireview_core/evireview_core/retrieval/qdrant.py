from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from typing import Any


Transport = Callable[[str, str, dict[str, Any]], dict[str, Any]]


def _urllib_transport(method: str, url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


class QdrantQueryClient:
    def __init__(self, base_url: str, transport: Transport | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.transport = transport or _urllib_transport

    def hybrid_query(
        self,
        collection: str,
        dense_vector: list[float],
        sparse_vector: dict[int, float],
        limit: int = 5,
        paper_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        sparse_items = sorted(sparse_vector.items())
        payload: dict[str, Any] = {
            "prefetch": [
                {"query": dense_vector, "using": "dense", "limit": limit * 2},
                {
                    "query": {
                        "indices": [index for index, _ in sparse_items],
                        "values": [value for _, value in sparse_items],
                    },
                    "using": "sparse",
                    "limit": limit * 2,
                },
            ],
            "query": {"fusion": "rrf"},
            "limit": limit,
            "with_payload": True,
        }
        if paper_id is not None:
            payload["filter"] = {"must": [{"key": "paper_id", "match": {"value": paper_id}}]}
        response = self.transport(
            "POST",
            f"{self.base_url}/collections/{collection}/points/query",
            payload,
        )
        result = response.get("result", {})
        return list(result.get("points", [])) if isinstance(result, dict) else []
