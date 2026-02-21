from kernel.bus.memory_router import MemoryRouter, MemoryRouterConfig


class FakeBus:
    def __init__(self) -> None:
        self.reads = [
            ("1-0", {"headers": '{"topic":"SYS:MEMORY:CONSOLIDATE"}', "payload": '{"data":"x"}'}),
        ]

    def read_stream(self, stream, last_id, count):
        return self.reads


class FakePipeline:
    name = "pipeline"

    def __init__(self) -> None:
        self.called = False

    def sentinel_scan(self, headers):
        return headers.get("topic") == "SYS:MEMORY:CONSOLIDATE"

    def handle(self, headers, payload):
        self.called = True


def test_memory_router_dispatches() -> None:
    router = MemoryRouter(MemoryRouterConfig(), FakeBus(), FakePipeline())
    processed = router.poll_once()
    assert processed == ["1-0"]
