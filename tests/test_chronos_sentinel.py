from kernel.arbiter.core import Arbiter, ArbiterPolicy
from workers._sentinels.chronos_sentinel import ChronosSentinel, ChronosSentinelConfig


class FakeBus:
    def __init__(self) -> None:
        self.messages = []

    def publish_stream(self, stream: str, payload):
        self.messages.append((stream, payload))
        return "1-0"


def test_chronos_sentinel_publishes_alert(monkeypatch) -> None:
    arbiter = Arbiter(ArbiterPolicy(min_free_gb=9999))
    bus = FakeBus()
    sentinel = ChronosSentinel(ChronosSentinelConfig(alerts_stream="SYS:ALERTS"), bus, arbiter)
    sentinel.handle({"topic": "SYS:HEARTBEAT"}, {"phase": "somatic"})
    assert bus.messages[0][0] == "SYS:ALERTS"
