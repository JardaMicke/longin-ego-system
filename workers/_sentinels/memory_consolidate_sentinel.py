from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class MemoryConsolidateConfig:
    """Účel: Konfigurace pro memory consolidate sentinel.

    Vstupy/Výstupy: Topic a cílový stream.
    Vedlejší efekty: Žádné.
    """
    topic: str = "MEM:CONSOLIDATE"
    target_stream: str = "SYS:MEMORY:CONSOLIDATE"


class MemoryConsolidateSentinel:
    """Účel: Přesměrovává consolidaci do memory streamu.

    Vstupy/Výstupy: Přijímá headers/payload a publikuje do Redis streamu.
    Vedlejší efekty: Publikuje do Redis.
    """
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
