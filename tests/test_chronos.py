import asyncio
import json

from kernel.chronos.heartbeat import ChronosConfig, ChronosHeartbeat
from kernel.bus.redis_bus import RedisBus


class FakeRedisBus(RedisBus):
    def __init__(self) -> None:
        self.data = {}

    def set_key(self, key: str, value: str) -> None:
        self.data[key] = value


def test_chronos_pulse_writes_heartbeat() -> None:
    bus = FakeRedisBus()
    chronos = ChronosHeartbeat(ChronosConfig(period_seconds=0.01), bus)
    asyncio.run(chronos._pulse("1", "somatic"))
    payload = json.loads(bus.data["SYS:HEARTBEAT"])
    assert payload["phase"] == "somatic"
