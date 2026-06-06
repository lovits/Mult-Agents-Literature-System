from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from evireview_core.providers.minimax import MiniMaxProvider, ProviderCallError


class MiniMaxProviderTest(unittest.TestCase):
    def test_reads_key_from_environment_and_returns_structured_payload_with_metadata(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(endpoint: str, payload: dict[str, object], headers: dict[str, str], timeout: int) -> dict[str, object]:
            requests.append({"endpoint": endpoint, "payload": payload, "headers": headers, "timeout": timeout})
            return {"choices": [{"message": {"content": '```json\n{"weaknesses":[{"weakness_text":"Missing ablation."}]}\n```'}}]}

        with patch.dict(os.environ, {"MINIMAX_API_KEY": "private-test-key"}):
            result = MiniMaxProvider(transport=transport).generate_json("system", "paper")

        self.assertEqual(result.payload["weaknesses"][0]["weakness_text"], "Missing ablation.")
        self.assertEqual(result.metadata["provider_name"], "minimax")
        self.assertEqual(result.metadata["model_name"], "MiniMax-M2.7")
        self.assertEqual(result.metadata["attempt_count"], 1)
        self.assertEqual(requests[0]["headers"], {"Content-Type": "application/json", "Authorization": "Bearer private-test-key"})
        self.assertNotIn("private-test-key", json.dumps(result.metadata))

    def test_retries_transient_transport_failure(self) -> None:
        attempts = 0

        def transport(_endpoint: str, _payload: dict[str, object], _headers: dict[str, str], _timeout: int) -> dict[str, object]:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise TimeoutError("private timeout detail")
            return {"choices": [{"message": {"content": '{"weaknesses":[]}'}}]}

        provider = MiniMaxProvider(api_key="private-test-key", transport=transport, sleep=lambda _seconds: None)

        result = provider.generate_json("system", "paper")

        self.assertEqual(attempts, 2)
        self.assertEqual(result.metadata["attempt_count"], 2)

    def test_extracts_json_after_minimax_thinking_block(self) -> None:
        def transport(_endpoint: str, _payload: dict[str, object], _headers: dict[str, str], _timeout: int) -> dict[str, object]:
            return {
                "choices": [
                    {
                        "message": {
                            "content": '<think>I should return {"example":"not output"}.</think>\n```json\n{"weaknesses":[]}\n```'
                        }
                    }
                ]
            }

        result = MiniMaxProvider(api_key="private-test-key", transport=transport).generate_json("system", "paper")

        self.assertEqual(result.payload, {"weaknesses": []})

    def test_public_error_does_not_expose_provider_response_or_key(self) -> None:
        def transport(_endpoint: str, _payload: dict[str, object], _headers: dict[str, str], _timeout: int) -> dict[str, object]:
            raise RuntimeError("private-test-key provider body")

        provider = MiniMaxProvider(api_key="private-test-key", transport=transport, sleep=lambda _seconds: None, max_attempts=1)

        with self.assertRaisesRegex(ProviderCallError, "MiniMax provider call failed") as raised:
            provider.generate_json("system", "paper")

        self.assertNotIn("private-test-key", str(raised.exception))
        self.assertNotIn("provider body", str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
