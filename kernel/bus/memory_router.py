from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, cast

from kernel.bus.redis_bus import RedisBus


class MemoryPipeline(Protocol):
    name: str

    def sentinel_scan(self, headers: Dict[str, Any]) -> bool:
        raise NotImplementedError("sentinel_scan must be implemented")

    def handle(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> None:
        raise NotImplementedError("handle must be implemented")


@dataclass(frozen=True)
class MemoryRouterConfig:
    stream: str = "SYS:MEMORY:CONSOLIDATE"
    start_id: str = "0-0"
    batch_size: int = 10


class MemoryRouter:
    def __init__(self, config: MemoryRouterConfig, bus: RedisBus, pipeline: MemoryPipeline) -> None:
        self._config = config
        self._bus = bus
        self._pipeline = pipeline
        self._last_id = config.start_id

    def poll_once(self) -> List[str]:
        entries = self._bus.read_stream(self._config.stream, self._last_id, self._config.batch_size)
        processed: List[str] = []
        for message_id, data in entries:
            self._last_id = message_id
            headers = self._decode_json(data.get("headers", "{}"))
            payload = self._decode_json(data.get("payload", "{}"))
            if self._pipeline.sentinel_scan(headers):
                self._pipeline.handle(headers, payload)
                processed.append(message_id)
        return processed

    def _decode_json(self, raw: Any) -> Dict[str, Any]:
        try:
            if isinstance(raw, str):
                return cast(Dict[str, Any], json.loads(raw))
            return cast(Dict[str, Any], dict(raw))
        except Exception as exc:
            raise RuntimeError(f"Memory router decode failed: {exc}") from exc
