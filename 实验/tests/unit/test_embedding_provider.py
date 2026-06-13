from evireview.rag.embedding import SentenceTransformerEmbedder


class FakeSentenceTransformer:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        if isinstance(texts, str):
            return [1.0, 0.0]
        return [[float(index), 1.0] for index, _ in enumerate(texts)]


def test_sentence_transformer_embedder_batches_documents_and_caches_them():
    model = FakeSentenceTransformer()
    embedder = SentenceTransformerEmbedder(model=model)

    first = embedder.embed_documents(["first", "second"])
    second = embedder.embed_documents(["second", "first"])

    assert first == [[0.0, 1.0], [1.0, 1.0]]
    assert second == [[1.0, 1.0], [0.0, 1.0]]
    assert len(model.calls) == 1
    assert model.calls[0][0] == ["first", "second"]


def test_sentence_transformer_embedder_prefixes_and_caches_queries():
    model = FakeSentenceTransformer()
    embedder = SentenceTransformerEmbedder(
        model=model,
        query_instruction="Represent this sentence: ",
    )

    assert embedder.embed_query("retrieval ablation") == [1.0, 0.0]
    assert embedder.embed_query("retrieval ablation") == [1.0, 0.0]
    assert len(model.calls) == 1
    assert model.calls[0][0] == "Represent this sentence: retrieval ablation"
