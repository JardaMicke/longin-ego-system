from workers._sentinels.registry import SentinelRegistry


class DummySentinel:
    name = "dummy"

    def __init__(self) -> None:
        self.called = False

    def sentinel_scan(self, headers):
        return headers.get("tag") == "hit"

    def handle(self, headers, payload):
        self.called = True


def test_registry_dispatches() -> None:
    registry = SentinelRegistry()
    sentinel = DummySentinel()
    registry.register(sentinel)
    triggered = registry.dispatch({"tag": "hit"}, {"data": "x"})
    assert triggered == ["dummy"]
    assert sentinel.called is True
