from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Mapping

from memory.postgres.client import PostgresClient
from memory.redis.client import RedisClient


@dataclass(frozen=True)
class MemoryPipelineConfig:
    """Účel: Konfigurace pipeline pro konsolidaci paměti.

    Vstupy/Výstupy: Topic, streamy a parametry batch/importance.
    Vedlejší efekty: Žádné.
    """
    topic: str = "SYS:MEMORY:CONSOLIDATE"
    hot_stream: str = "SYS:MEMORY:HOT"
    batch_size: int = 50
    episodic_source: str = "redis"
    episodic_importance: float = 0.3


class MemoryPipelineSentinel:
    """Účel: Převádí hot memory na semantic a episodic záznamy.

    Vstupy/Výstupy: Přijímá headers/payload a zapisuje do Postgresu.
    Vedlejší efekty: Čte Redis stream a zapisuje do Postgres.
    """
    name = "memory_pipeline"

    def __init__(
        self,
        config: MemoryPipelineConfig,
        redis_client: RedisClient,
        postgres_client: PostgresClient,
        embedder: Callable[[str], Iterable[float]],
    ) -> None:
        self._config = config
        self._redis_client = redis_client
        self._postgres_client = postgres_client
        self._embedder = embedder
        self._last_id = "0-0"

    def sentinel_scan(self, headers: Dict[str, Any]) -> bool:
        return headers.get("topic") == self._config.topic

    def handle(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> None:
        entries = self._redis_client.read_stream(
            self._config.hot_stream, self._last_id, self._config.batch_size
        )
        for message_id, data in entries:
            self._last_id = message_id
            content = self._to_content(data)
            if not content:
                continue
            embedding = self._vectorize(content)
            self._postgres_client.insert_semantic(content, tags=[], embedding=embedding)
            self._postgres_client.insert_episodic(
                source=self._config.episodic_source,
                payload=data,
                importance=self._config.episodic_importance,
            )

    def _to_content(self, data: Mapping[str, Any]) -> str:
        try:
            return json.dumps(dict(data), ensure_ascii=False)
        except Exception as exc:
            raise RuntimeError(f"Memory content serialization failed: {exc}") from exc

    def _vectorize(self, content: str) -> Iterable[float]:
        try:
            return list(self._embedder(content))
        except Exception as exc:
            raise RuntimeError(f"Memory vectorization failed: {exc}") from exc
