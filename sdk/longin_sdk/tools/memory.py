from __future__ import annotations

from typing import Callable, Iterable, List, Mapping, Optional, Tuple

from memory.postgres.client import PostgresClient, PostgresConfig


class MemoryClient:
    """Účel: SDK klient pro ukládání a vyhledávání v paměti.

    Vstupy/Výstupy: Přijímá DSN a embedder, vrací výsledky vyhledávání.
    Vedlejší efekty: Přistupuje k Postgres databázi.
    """
    def __init__(self, dsn: Optional[str] = None, embedder: Optional[Callable[[str], Iterable[float]]] = None) -> None:
        self._dsn = dsn
        self._embedder = embedder

    def recall(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        if self._dsn is None:
            raise RuntimeError("Memory DSN is not configured")
        if self._embedder is None:
            raise RuntimeError("Embedder is not configured")
        try:
            embedding = list(self._embedder(query))
        except Exception as exc:
            raise RuntimeError(f"Embedding generation failed: {exc}") from exc
        try:
            client = PostgresClient(PostgresConfig(dsn=self._dsn))
            return client.vector_search(embedding=embedding, limit=limit)
        except Exception as exc:
            raise RuntimeError(f"Memory recall failed: {exc}") from exc

    def store(
        self,
        content: str,
        metadata: Mapping[str, object],
        user_id: Optional[str] = None,
    ) -> None:
        if self._dsn is None:
            raise RuntimeError("Memory DSN is not configured")
        if self._embedder is None:
            raise RuntimeError("Embedder is not configured")
        try:
            embedding = list(self._embedder(content))
        except Exception as exc:
            raise RuntimeError(f"Embedding generation failed: {exc}") from exc
        try:
            client = PostgresClient(PostgresConfig(dsn=self._dsn))
            client.insert_memory(content=content, embedding=embedding, metadata=metadata, user_id=user_id)
        except Exception as exc:
            raise RuntimeError(f"Memory store failed: {exc}") from exc

    def recall_memories(
        self,
        query: str,
        limit: int = 5,
        user_id: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        if self._dsn is None:
            raise RuntimeError("Memory DSN is not configured")
        if self._embedder is None:
            raise RuntimeError("Embedder is not configured")
        try:
            embedding = list(self._embedder(query))
        except Exception as exc:
            raise RuntimeError(f"Embedding generation failed: {exc}") from exc
        try:
            client = PostgresClient(PostgresConfig(dsn=self._dsn))
            return client.search_memories(embedding=embedding, limit=limit, user_id=user_id)
        except Exception as exc:
            raise RuntimeError(f"Memory recall failed: {exc}") from exc
