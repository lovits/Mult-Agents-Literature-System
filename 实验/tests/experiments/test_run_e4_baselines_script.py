import scripts.run_e4_baselines as run_script


def test_build_formal_provider_uses_pinned_embedding(monkeypatch):
    captured = {}

    class FakeEmbedder:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(run_script, "SentenceTransformerEmbedder", FakeEmbedder)

    provider = run_script.build_embedding_provider(
        {
            "embedding": {
                "name": "BAAI/bge-base-en-v1.5",
                "revision": "fixed",
                "device": "cpu",
                "local_files_only": True,
                "query_instruction": "query: ",
            }
        }
    )

    assert isinstance(provider, FakeEmbedder)
    assert captured["revision"] == "fixed"
    assert captured["local_files_only"] is True
