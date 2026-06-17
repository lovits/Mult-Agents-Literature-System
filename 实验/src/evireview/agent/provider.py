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
    "support_strict": (
        "Build an evidence case only when the supplied evidence demonstrates that "
        "the weakness is actually present; mere relatedness is insufficient. If no "
        "supplied evidence explicitly supports the weakness, evidence_ids must be "
        "empty and strength must be at most 0.3. Return JSON with claim, evidence_ids "
        "selected only from supplied IDs, strength 0-1, and rationale."
    ),
    "refutation": (
        "Build the strongest evidence case that the paper already addresses, refutes, "
        "or makes the weakness invalid. Return JSON with claim, evidence_ids selected "
        "only from supplied IDs, strength 0-1, and rationale."
    ),
    "refutation_strict": (
        "Build an evidence case only when the supplied evidence explicitly shows that "
        "the paper resolves, addresses, or refutes the weakness; mere relatedness is "
        "insufficient. If no supplied evidence explicitly resolves the weakness, "
        "evidence_ids must be empty and strength must be at most 0.3. Return JSON with "
        "claim, evidence_ids selected only from supplied IDs, strength 0-1, and "
        "rationale."
    ),
    "adjudicate": (
        "Compare the supplied support and refutation cases. Return JSON with decision "
        "keep/rewrite/reject/uncertain, confidence 0-1, evidence_ids selected only "
        "from supplied IDs, and reason. Do not request human review."
    ),
    "adjudicate_compact": (
        "Conservatively compare the supplied structured support and refutation cases "
        "using only their cited evidence. Relatedness alone is not decisive. Do not "
        "default to keep when support is weak or evidence is inconclusive. Return JSON "
        "with decision keep/rewrite/reject/uncertain, confidence 0-1, evidence_ids "
        "selected only from supplied IDs, and reason. Do not request human review."
    ),
    "generate_review_candidates": (
        "Generate leakage-free scientific peer-review weakness candidates from the "
        "supplied paper metadata and evidence snippets only. Do not infer accept or "
        "reject decisions. Return JSON with candidates as a list of up to the requested "
        "top_k items. Each item must include weakness, aspect, severity, suggestion, "
        "confidence 0-1, and evidence_ids selected only from supplied IDs."
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
        max_tokens_field: str = "max_completion_tokens",
        request_options: dict[str, Any] | None = None,
        retry_attempts: int = 0,
        retry_backoff_seconds: float = 1.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.max_completion_tokens = max_completion_tokens
        self.max_tokens_field = max_tokens_field
        self.request_options = request_options or {}
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds
        self.client = httpx.Client(timeout=timeout, transport=transport)

    def complete_json(self, role: str, payload: dict[str, Any]) -> ProviderResult:
        if role not in ROLE_INSTRUCTIONS:
            raise ValueError(f"unknown provider role: {role}")
        started = time.perf_counter()
        request_body = {
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
            "stream": False,
            self.max_tokens_field: self.max_completion_tokens,
            **self.request_options,
        }
        response = self._post_with_retry(request_body)
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

    def _post_with_retry(self, request_body: dict[str, Any]) -> httpx.Response:
        for attempt in range(self.retry_attempts + 1):
            try:
                response = self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=request_body,
                )
                if response.status_code not in {408, 429, 500, 502, 503, 504}:
                    return response
            except (httpx.ConnectError, httpx.RemoteProtocolError):
                if attempt >= self.retry_attempts:
                    raise
            if attempt < self.retry_attempts:
                time.sleep(self.retry_backoff_seconds * (attempt + 1))
        return response


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
