import types

from kernel.bus.redis_bus import RedisBus, RedisBusConfig


class FakeRedis:
    def __init__(self) -> None:
        self.store = {}

    def set(self, key: str, value: str) -> None:
        self.store[key] = value

    def xadd(self, stream: str, payload) -> str:
        return f"{stream}-1"


class FakeRedisModule:
    @staticmethod
    def Redis_from_url(url: str, decode_responses: bool) -> FakeRedis:
        return FakeRedis()


def test_redis_bus_set_and_publish(monkeypatch) -> None:
    fake_module = types.SimpleNamespace()
    fake_module.Redis = types.SimpleNamespace(from_url=FakeRedisModule.Redis_from_url)
    monkeypatch.setitem(__import__("sys").modules, "redis", fake_module)
    bus = RedisBus(RedisBusConfig(url="redis://localhost:6379/0"))
    bus.set_key("key", "value")
    message_id = bus.publish_stream("stream", {"a": "b"})
    assert message_id == "stream-1"
