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

    def server_info(self) -> dict[str, Any]:
        return self.transport("GET", f"{self.base_url}/", {})

    def recreate_collection(self, collection: str, dense_size: int) -> None:
        if dense_size <= 0:
            raise ValueError("dense_size must be positive")
        try:
            self.transport("DELETE", f"{self.base_url}/collections/{collection}", {})
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        self.transport(
            "PUT",
            f"{self.base_url}/collections/{collection}",
            {
                "vectors": {"dense": {"size": dense_size, "distance": "Cosine"}},
                "sparse_vectors": {"sparse": {}},
            },
        )

    def recreate_sparse_collection(self, collection: str) -> None:
        try:
            self.transport("DELETE", f"{self.base_url}/collections/{collection}", {})
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        self.transport(
            "PUT",
            f"{self.base_url}/collections/{collection}",
            {"sparse_vectors": {"sparse": {}}},
        )

    def upsert_points(self, collection: str, points: list[dict[str, Any]]) -> None:
        if not points:
            return
        self.transport(
            "PUT",
            f"{self.base_url}/collections/{collection}/points?wait=true",
            {"points": points},
        )

    def create_keyword_index(self, collection: str, field_name: str) -> None:
        if not field_name:
            raise ValueError("field_name must not be empty")
        self.transport(
            "PUT",
            f"{self.base_url}/collections/{collection}/index?wait=true",
            {"field_name": field_name, "field_schema": "keyword"},
        )

    def dense_query(
        self,
        collection: str,
        dense_vector: list[float],
        limit: int = 5,
        filters: dict[str, str | int] | None = None,
    ) -> list[dict[str, Any]]:
        return self._query(collection, dense_vector, "dense", limit, filters)

    def sparse_query(
        self,
        collection: str,
        sparse_vector: dict[int, float],
        limit: int = 5,
        filters: dict[str, str | int] | None = None,
    ) -> list[dict[str, Any]]:
        sparse_items = sorted(sparse_vector.items())
        query = {
            "indices": [index for index, _ in sparse_items],
            "values": [value for _, value in sparse_items],
        }
        return self._query(collection, query, "sparse", limit, filters)

    def _query(
        self,
        collection: str,
        query: Any,
        using: str,
        limit: int,
        filters: dict[str, str | int] | None,
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        payload: dict[str, Any] = {
            "query": query,
            "using": using,
            "limit": limit,
            "with_payload": True,
        }
        if filters:
            payload["filter"] = self._filter(filters)
        return self._points(
            self.transport("POST", f"{self.base_url}/collections/{collection}/points/query", payload)
        )

    def hybrid_query(
        self,
        collection: str,
        dense_vector: list[float],
        sparse_vector: dict[int, float],
        limit: int = 5,
        paper_id: str | None = None,
        filters: dict[str, str | int] | None = None,
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
        query_filters = dict(filters or {})
        if paper_id is not None:
            query_filters["paper_id"] = paper_id
        if query_filters:
            payload["filter"] = self._filter(query_filters)
        return self._points(self.transport(
            "POST",
            f"{self.base_url}/collections/{collection}/points/query",
            payload,
        ))

    @staticmethod
    def _filter(filters: dict[str, str | int]) -> dict[str, Any]:
        return {
            "must": [
                {"key": key, "match": {"value": value}}
                for key, value in filters.items()
            ]
        }

    @staticmethod
    def _points(response: dict[str, Any]) -> list[dict[str, Any]]:
        result = response.get("result", {})
        return list(result.get("points", [])) if isinstance(result, dict) else []
