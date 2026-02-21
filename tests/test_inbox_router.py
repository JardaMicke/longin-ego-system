from kernel.bus.inbox_router import InboxRouter, InboxRouterConfig
from workers._sentinels.registry import SentinelRegistry


class FakeBus:
    def __init__(self) -> None:
        self.reads = [
            ("1-0", {"headers": '{"tag":"hit"}', "payload": '{"data":"x"}'}),
        ]
        self.published = []

    def read_stream(self, stream, last_id, count):
        return self.reads

    def publish_stream(self, stream: str, payload):
        self.published.append((stream, payload))
        return "1-0"


class DummySentinel:
    name = "dummy"

    def __init__(self) -> None:
        self.called = False

    def sentinel_scan(self, headers):
        return headers.get("tag") == "hit"

    def handle(self, headers, payload):
        self.called = True


class FakeIdentity:
    def get_identity_state(self):
        return "hash-1", False


def test_inbox_router_dispatches() -> None:
    registry = SentinelRegistry()
    sentinel = DummySentinel()
    registry.register(sentinel)
    router = InboxRouter(InboxRouterConfig(), FakeBus(), registry, identity_firewall=FakeIdentity())
    results = router.poll_once()
    assert results[0][1] == ["dummy"]
    assert sentinel.called is True


class ChangingIdentity:
    def get_identity_state(self):
        return "hash-9", True


def test_inbox_router_identity_flush() -> None:
    registry = SentinelRegistry()
    sentinel = DummySentinel()
    registry.register(sentinel)
    bus = FakeBus()
    router = InboxRouter(
        InboxRouterConfig(identity_flush_stream="SYS:MEMORY:FLUSH", identity_flush_min_interval_seconds=0.0),
        bus,
        registry,
        identity_firewall=ChangingIdentity(),
    )
    router.poll_once()
    assert bus.published[0][0] == "SYS:MEMORY:FLUSH"


def test_inbox_router_throttles_identity_flush() -> None:
    registry = SentinelRegistry()
    sentinel = DummySentinel()
    registry.register(sentinel)
    bus = FakeBus()
    router = InboxRouter(
        InboxRouterConfig(identity_flush_stream="SYS:MEMORY:FLUSH", identity_flush_min_interval_seconds=9999.0),
        bus,
        registry,
        identity_firewall=ChangingIdentity(),
    )
    router.poll_once()
    router.poll_once()
    flushes = [stream for stream, _ in bus.published if stream == "SYS:MEMORY:FLUSH"]
    assert len(flushes) == 1
