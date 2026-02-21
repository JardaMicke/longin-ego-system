from kernel.embeddings.simple_embedder import SimpleEmbedder


def test_simple_embedder_dimensions() -> None:
    embedder = SimpleEmbedder(dimensions=8)
    embedding = embedder.embed("hello")
    assert len(embedding) == 8


def test_simple_embedder_is_deterministic() -> None:
    embedder = SimpleEmbedder(dimensions=16)
    assert embedder.embed("same") == embedder.embed("same")
