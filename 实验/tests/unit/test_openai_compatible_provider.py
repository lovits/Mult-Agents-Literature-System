import httpx

from evireview.agent.provider import OpenAICompatibleProvider


def test_provider_extracts_json_and_usage_without_exposing_reasoning():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        payload = __import__("json").loads(request.content)
        assert payload["max_tokens"] == 256
        assert "reasoning_split" not in payload
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '```json\n{"decision":"keep","confidence":0.8}\n```',
                            "reasoning_content": "private reasoning",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                },
            },
        )

    provider = OpenAICompatibleProvider(
        base_url="https://example.test/v1",
        model="MiniMax-M2.7",
        api_key="test-key",
        max_tokens_field="max_tokens",
        max_completion_tokens=256,
        transport=httpx.MockTransport(handler),
    )

    result = provider.complete_json("judge", {"weakness": "test"})

    assert result.data == {"decision": "keep", "confidence": 0.8}
    assert result.usage["total_tokens"] == 120
    assert "reasoning" not in result.raw_content


def test_provider_retries_transient_network_failure():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("temporary", request=request)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"decision":"keep"}'}}],
                "usage": {"total_tokens": 10},
            },
        )

    provider = OpenAICompatibleProvider(
        base_url="https://example.test/v1",
        model="agnes-2.0-flash",
        api_key="test-key",
        max_tokens_field="max_tokens",
        retry_attempts=1,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    result = provider.complete_json("judge", {"weakness": "test"})

    assert result.data["decision"] == "keep"
    assert calls == 2
