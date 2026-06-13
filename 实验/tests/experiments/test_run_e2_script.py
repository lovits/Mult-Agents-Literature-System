import scripts.run_e2 as run_e2_script


def test_build_embedding_provider_uses_pinned_formal_config(monkeypatch):
    captured = {}

    class FakeEmbedder:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(run_e2_script, "SentenceTransformerEmbedder", FakeEmbedder)
    config = {
        "embedding": {
            "name": "BAAI/bge-base-en-v1.5",
            "revision": "fixed-revision",
            "device": "cpu",
            "local_files_only": True,
            "query_instruction": "query: ",
        }
    }

    provider = run_e2_script.build_embedding_provider(config)

    assert isinstance(provider, FakeEmbedder)
    assert captured == {
        "model_name": "BAAI/bge-base-en-v1.5",
        "revision": "fixed-revision",
        "device": "cpu",
        "local_files_only": True,
        "query_instruction": "query: ",
    }


def test_build_embedding_provider_keeps_hashing_smoke_dependency_free():
    assert (
        run_e2_script.build_embedding_provider({"embedding": {"name": "hashing-smoke"}})
        is None
    )
