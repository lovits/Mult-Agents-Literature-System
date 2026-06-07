from __future__ import annotations

import unittest

from evireview_core.providers.embedding import OpenAICompatibleEmbedder


class OpenAICompatibleEmbedderTest(unittest.TestCase):
    def test_maps_texts_to_openai_compatible_embedding_request(self) -> None:
        calls = []

        def transport(url, headers, payload):
            calls.append((url, headers, payload))
            return {"data": [{"index": 1, "embedding": [0.0, 1.0]}, {"index": 0, "embedding": [1.0, 0.0]}]}

        embedder = OpenAICompatibleEmbedder(
            base_url="https://embedding.example/v1",
            api_key="secret",
            model="embed-model",
            transport=transport,
        )

        vectors = embedder(["first", "second"])

        self.assertEqual(vectors, [[1.0, 0.0], [0.0, 1.0]])
        self.assertEqual(calls[0][0], "https://embedding.example/v1/embeddings")
        self.assertEqual(calls[0][1]["Authorization"], "Bearer secret")
        self.assertEqual(calls[0][2], {"model": "embed-model", "input": ["first", "second"]})

    def test_rejects_missing_embedding_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "embedding"):
            OpenAICompatibleEmbedder(base_url="", api_key="", model="")


if __name__ == "__main__":
    unittest.main()
