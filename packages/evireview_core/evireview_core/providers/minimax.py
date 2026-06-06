from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from collections.abc import Callable
from typing import Any

from evireview_core.providers.base import ProviderCallError, ProviderGeneration


DEFAULT_ENDPOINT = "https://api.minimaxi.com/v1/chat/completions"
DEFAULT_MODEL = "MiniMax-M2.7"
Transport = Callable[[str, dict[str, object], dict[str, str], int], dict[str, object]]


def _default_transport(endpoint: str, payload: dict[str, object], headers: dict[str, str], timeout: int) -> dict[str, object]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_json_content(content: str) -> dict[str, Any]:
    normalized = content.strip()
    normalized = re.sub(r"<think>.*?</think>", "", normalized, flags=re.IGNORECASE | re.DOTALL).strip()
    normalized = re.sub(r"^```(?:json)?", "", normalized, flags=re.IGNORECASE).strip()
    normalized = re.sub(r"```$", "", normalized).strip()
    if normalized.startswith('"') and normalized.endswith('"'):
        decoded = json.loads(normalized)
        if isinstance(decoded, str):
            normalized = decoded.strip()
    try:
        result = json.loads(normalized)
    except json.JSONDecodeError:
        start, end = normalized.find("{"), normalized.rfind("}")
        if start < 0 or end <= start:
            raise
        result = json.loads(normalized[start : end + 1])
    if not isinstance(result, dict):
        raise ValueError("provider response must be a JSON object")
    return result


class MiniMaxProvider:
    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        model: str = DEFAULT_MODEL,
        transport: Transport = _default_transport,
        timeout: int = 180,
        max_attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.endpoint = endpoint or os.getenv("MINIMAX_ENDPOINT", DEFAULT_ENDPOINT)
        self.model = model
        self.transport = transport
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.sleep = sleep

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        prompt_version: str = "structured_reviewer_v1",
        schema_version: str = "weaknesses_v1",
        temperature: float = 0.2,
        max_tokens: int = 1800,
    ) -> ProviderGeneration:
        if not self._api_key:
            raise ProviderCallError("MiniMax provider call failed: missing MINIMAX_API_KEY")
        request_payload: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self._api_key}"}
        started = time.monotonic()
        for attempt in range(1, self.max_attempts + 1):
            try:
                body = self.transport(self.endpoint, request_payload, headers, self.timeout)
                content = body["choices"][0]["message"]["content"]  # type: ignore[index]
                payload = _parse_json_content(str(content))
                return ProviderGeneration(
                    payload=payload,
                    metadata={
                        "provider_name": "minimax",
                        "model_name": self.model,
                        "prompt_version": prompt_version,
                        "schema_version": schema_version,
                        "is_silver": True,
                        "generation_error": None,
                        "attempt_count": attempt,
                        "latency_seconds": round(time.monotonic() - started, 4),
                        "generation_config": {"temperature": temperature, "max_tokens": max_tokens},
                    },
                )
            except Exception:
                if attempt == self.max_attempts:
                    raise ProviderCallError(f"MiniMax provider call failed after {attempt} attempt(s)") from None
                self.sleep(min(2 * attempt, 6))
        raise ProviderCallError("MiniMax provider call failed")


__all__ = ["MiniMaxProvider", "ProviderCallError"]
