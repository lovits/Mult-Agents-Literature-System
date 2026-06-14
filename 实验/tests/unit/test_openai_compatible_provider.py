import httpx

from evireview.agent.provider import OpenAICompatibleProvider


def test_provider_extracts_json_and_usage_without_exposing_reasoning():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
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
        transport=httpx.MockTransport(handler),
    )

    result = provider.complete_json("judge", {"weakness": "test"})

    assert result.data == {"decision": "keep", "confidence": 0.8}
    assert result.usage["total_tokens"] == 120
    assert "reasoning" not in result.raw_content
