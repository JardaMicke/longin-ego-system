from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Callable, Optional

from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class ChronosConfig:
    """Účel: Konfigurace heartbeat period a cílů pro publikaci.

    Vstupy/Výstupy: Perioda, Redis key a volitelný stream.
    Vedlejší efekty: Žádné.
    """
    period_seconds: float = 15.0
    heartbeat_key: str = "SYS:HEARTBEAT"
    heartbeat_stream: str | None = None


class ChronosHeartbeat:
    """Účel: Spouští cyklický heartbeat a publikuje fáze systému.

    Vstupy/Výstupy: Přijímá konfiguraci, RedisBus a callback, publikuje heartbeat.
    Vedlejší efekty: Periodické zápisy do Redis a volání callbacku.
    """
    def __init__(
        self,
        config: ChronosConfig,
        bus: RedisBus,
        on_phase: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._config = config
        self._bus = bus
        self._on_phase = on_phase
        self._running = False

    async def run(self) -> None:
        if self._running:
            return
        self._running = True
        try:
            while self._running:
                cycle_id = str(int(time.time() * 1000))
                for phase in ("somatic", "cognitive", "execute"):
                    await self._pulse(cycle_id, phase)
                await asyncio.sleep(self._config.period_seconds)
        except Exception as exc:
            self._running = False
            raise RuntimeError(f"Chronos run failed: {exc}") from exc

    def stop(self) -> None:
        self._running = False

    async def _pulse(self, cycle_id: str, phase: str) -> None:
        payload = {
            "cycle_id": cycle_id,
            "phase": phase,
            "timestamp": time.time(),
        }
        try:
            self._bus.set_key(self._config.heartbeat_key, json.dumps(payload))
            if self._config.heartbeat_stream is not None:
                envelope = {
                    "headers": json.dumps({"topic": "SYS:HEARTBEAT"}),
                    "payload": json.dumps(payload),
                }
                self._bus.publish_stream(self._config.heartbeat_stream, envelope)
            if self._on_phase is not None:
                self._on_phase(phase)
        except Exception as exc:
            raise RuntimeError(f"Chronos pulse failed for phase {phase}: {exc}") from exc
