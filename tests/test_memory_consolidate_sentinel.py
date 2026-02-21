from workers._sentinels.memory_consolidate_sentinel import MemoryConsolidateConfig, MemoryConsolidateSentinel


class FakeBus:
    def __init__(self) -> None:
        self.messages = []

    def publish_stream(self, stream: str, payload):
        self.messages.append((stream, payload))
        return "1-0"


def test_memory_consolidate_sentinel_publishes() -> None:
    bus = FakeBus()
    sentinel = MemoryConsolidateSentinel(MemoryConsolidateConfig(target_stream="SYS:MEMORY:CONSOLIDATE"), bus)
    sentinel.handle({"topic": "MEM:CONSOLIDATE"}, {"data": "x"})
    assert bus.messages[0][0] == "SYS:MEMORY:CONSOLIDATE"
    assert "headers" in bus.messages[0][1]
    assert "payload" in bus.messages[0][1]
