import types

import pytest

from longin_sdk.tools.memory import MemoryClient


def test_memory_client_requires_dsn() -> None:
    client = MemoryClient()
    with pytest.raises(RuntimeError):
        client.recall("query")


def test_memory_client_requires_embedder() -> None:
    client = MemoryClient(dsn="postgresql://user:pass@localhost/db")
    with pytest.raises(RuntimeError):
        client.recall("query")


def test_memory_client_recall(monkeypatch) -> None:
    fake_module = types.SimpleNamespace()

    class FakePostgresClient:
        def __init__(self, config) -> None:
            self.config = config

        def vector_search(self, embedding, limit=5):
            return [("result", 0.1)]

        def insert_memory(self, content, embedding, metadata, user_id=None) -> None:
            return None

        def search_memories(self, embedding, limit=5, user_id=None):
            return [("memory", 0.2)]

    fake_module.PostgresClient = FakePostgresClient
    fake_module.PostgresConfig = lambda dsn: types.SimpleNamespace(dsn=dsn)
    monkeypatch.setattr("longin_sdk.tools.memory.PostgresClient", FakePostgresClient)
    monkeypatch.setattr("longin_sdk.tools.memory.PostgresConfig", fake_module.PostgresConfig)
    client = MemoryClient(dsn="postgresql://user:pass@localhost/db", embedder=lambda q: [0.1, 0.2])
    assert client.recall("query", limit=1) == [("result", 0.1)]
    client.store("content", metadata={"tag": "x"}, user_id="user-1")
    assert client.recall_memories("query", limit=1) == [("memory", 0.2)]
