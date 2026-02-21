from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from kernel.arbiter.core import Arbiter
from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class ChronosSentinelConfig:
    topic: str = "SYS:HEARTBEAT"
    alerts_stream: str = "SYS:ALERTS"


class ChronosSentinel:
    name = "chronos_sentinel"

    def __init__(self, config: ChronosSentinelConfig, bus: RedisBus, arbiter: Arbiter) -> None:
        self._config = config
        self._bus = bus
        self._arbiter = arbiter

    def sentinel_scan(self, headers: Dict[str, Any]) -> bool:
        return headers.get("topic") == self._config.topic

    def handle(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> None:
        try:
            allowed = self._arbiter.check_resources()
            if not allowed:
                self._bus.publish_stream(
                    self._config.alerts_stream,
                    {"type": "resource_block", "payload": str(payload)},
                )
        except Exception as exc:
            raise RuntimeError(f"Chronos sentinel failed: {exc}") from exc
