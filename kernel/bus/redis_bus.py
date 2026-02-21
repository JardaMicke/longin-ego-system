from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Mapping, Tuple, cast


@dataclass(frozen=True)
class RedisBusConfig:
    """Účel: Konfigurace připojení k Redis busu.

    Vstupy/Výstupy: Redis URL uložené v konfiguraci.
    Vedlejší efekty: Žádné.
    """
    url: str


class RedisBus:
    """Účel: Poskytuje publish/read operace nad Redis Streams a klíči.

    Vstupy/Výstupy: Přijímá konfiguraci, publikuje zprávy a vrací jejich ID.
    Vedlejší efekty: Síťová komunikace s Redis serverem.
    """
    def __init__(self, config: RedisBusConfig) -> None:
        self._config = config
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import redis
        except Exception as exc:
            raise RuntimeError(f"Redis client import failed: {exc}") from exc
        try:
            self._client = redis.Redis.from_url(self._config.url, decode_responses=True)
        except Exception as exc:
            raise RuntimeError(f"Redis client initialization failed: {exc}") from exc
        return cast(Any, self._client)

    def set_key(self, key: str, value: str) -> None:
        try:
            client = self._get_client()
            client.set(key, value)
        except Exception as exc:
            raise RuntimeError(f"Redis set failed for key {key}: {exc}") from exc

    def publish_stream(self, stream: str, payload: Mapping[str, Any]) -> str:
        try:
            client = self._get_client()
            message_id = client.xadd(stream, payload)
            return str(message_id)
        except Exception as exc:
            raise RuntimeError(f"Redis stream publish failed for {stream}: {exc}") from exc

    def read_stream(self, stream: str, last_id: str = "0-0", count: int = 10) -> List[Tuple[str, Mapping[str, Any]]]:
        try:
            client = self._get_client()
            entries = client.xread({stream: last_id}, count=count)
            results: List[Tuple[str, Mapping[str, Any]]] = []
            for _, messages in entries:
                for message_id, data in messages:
                    results.append((str(message_id), data))
            return results
        except Exception as exc:
            raise RuntimeError(f"Redis stream read failed for {stream}: {exc}") from exc
