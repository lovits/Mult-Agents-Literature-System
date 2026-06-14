import json
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx


ROLE_INSTRUCTIONS = {
    "judge": (
        "Judge whether the review weakness is valid. Return JSON with decision "
        "keep/rewrite/reject/uncertain, confidence 0-1, evidence_ids, and reason."
    ),
    "judge_no_evidence": (
        "Judge whether the review weakness is valid using only the weakness text. "
        "Return JSON with decision keep/reject/uncertain, confidence 0-1, "
        "evidence_ids as an empty list, and reason."
    ),
    "judge_with_evidence": (
        "Judge whether the review weakness is valid using only the supplied evidence. "
        "Return JSON with decision keep/rewrite/reject/uncertain, confidence 0-1, "
        "evidence_ids selected only from supplied IDs, and reason."
    ),
    "support": (
        "Build the strongest evidence case that the weakness is valid and grounded. "
        "Return JSON with claim, evidence_ids selected only from supplied IDs, "
        "strength 0-1, and rationale."
    ),
    "refutation": (
        "Build the strongest evidence case that the paper already addresses, refutes, "
        "or makes the weakness invalid. Return JSON with claim, evidence_ids selected "
        "only from supplied IDs, strength 0-1, and rationale."
    ),
    "adjudicate": (
        "Compare the supplied support and refutation cases. Return JSON with decision "
        "keep/rewrite/reject/uncertain, confidence 0-1, evidence_ids selected only "
        "from supplied IDs, and reason. Do not request human review."
    ),
}


@dataclass(frozen=True)
class ProviderResult:
    data: dict[str, Any]
    usage: dict[str, int]
    latency_ms: float
    raw_content: str


class ProviderHTTPError(RuntimeError):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout: float = 120.0,
        max_completion_tokens: int = 1024,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.max_completion_tokens = max_completion_tokens
        self.client = httpx.Client(timeout=timeout, transport=transport)

    def complete_json(self, role: str, payload: dict[str, Any]) -> ProviderResult:
        if role not in ROLE_INSTRUCTIONS:
            raise ValueError(f"unknown provider role: {role}")
        started = time.perf_counter()
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an evidence-audit component for scientific peer "
                            "review. Be conservative and output one JSON object only. "
                            + ROLE_INSTRUCTIONS[role]
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False),
                    },
                ],
                "temperature": 0,
                "max_completion_tokens": self.max_completion_tokens,
                "reasoning_split": True,
                "stream": False,
            },
        )
        latency_ms = (time.perf_counter() - started) * 1000
        if response.is_error:
            try:
                message = response.json().get("error", {}).get("message", response.text)
            except ValueError:
                message = response.text
            raise ProviderHTTPError(response.status_code, message)
        body = response.json()
        content = body["choices"][0]["message"]["content"]
        return ProviderResult(
            data=_extract_json(content),
            usage={
                key: int(value)
                for key, value in body.get("usage", {}).items()
                if isinstance(value, int)
            },
            latency_ms=latency_ms,
            raw_content=content,
        )


def _extract_json(content: str) -> dict[str, Any]:
    stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if match is None:
            raise ValueError("provider response does not contain a JSON object")
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("provider response JSON must be an object")
    return value
