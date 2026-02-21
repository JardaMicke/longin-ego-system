from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class MemoryConsolidateConfig:
    topic: str = "MEM:CONSOLIDATE"
    target_stream: str = "SYS:MEMORY:CONSOLIDATE"


class MemoryConsolidateSentinel:
    name = "memory_consolidate"

    def __init__(self, config: MemoryConsolidateConfig, bus: RedisBus) -> None:
        self._config = config
        self._bus = bus

    def sentinel_scan(self, headers: Dict[str, Any]) -> bool:
        return headers.get("topic") == self._config.topic

    def handle(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> None:
        try:
            self._bus.publish_stream(
                self._config.target_stream,
                {
                    "headers": json.dumps({"topic": self._config.target_stream, "source": "MEM:CONSOLIDATE"}),
                    "payload": json.dumps(payload),
                },
            )
        except Exception as exc:
            raise RuntimeError(f"Memory consolidate failed: {exc}") from exc
