import json

from kernel.runtime import KernelRuntime, KernelRuntimeConfig


class FakeBus:
    def __init__(self) -> None:
        self.published = []
        self.data = {}

    def publish_stream(self, stream: str, payload):
        self.published.append((stream, payload))
        return "1-0"

    def set_key(self, key: str, value: str) -> None:
        self.data[key] = value


class FakeRedisClient:
    def read_stream(self, stream, last_id="0-0", count=10):
        return []


class FakePostgresClient:
    def __init__(self) -> None:
        self.identities = []

    def insert_semantic(self, content, tags, embedding) -> None:
        return None

    def insert_episodic(self, source, payload, importance) -> None:
        return None

    def insert_identity(self, version: str, soul_hash: str, directives) -> None:
        self.identities.append((version, soul_hash, directives))


class FakeRouter:
    def __init__(self) -> None:
        self.called = 0

    def poll_once(self):
        self.called += 1
        return []


def test_kernel_runtime_publish_phase() -> None:
    runtime = KernelRuntime(
        KernelRuntimeConfig(redis_url="redis://localhost:6379", postgres_dsn="dsn", enable_discovery=False),
        bus=FakeBus(),
        redis_client=FakeRedisClient(),
        postgres_client=FakePostgresClient(),
        inbox_router=FakeRouter(),
        memory_router=FakeRouter(),
    )
    runtime._publish_phase("somatic")
    stream, payload = runtime._bus.published[0]
    assert stream == "SYS:INBOX"
    headers = json.loads(payload["headers"])
    assert headers["topic"] == "SYS:HEARTBEAT"


def test_kernel_runtime_network_registry_disabled() -> None:
    runtime = KernelRuntime(
        KernelRuntimeConfig(redis_url="redis://localhost:6379", postgres_dsn="dsn", enable_discovery=False),
        bus=FakeBus(),
        redis_client=FakeRedisClient(),
        postgres_client=FakePostgresClient(),
        inbox_router=FakeRouter(),
        memory_router=FakeRouter(),
    )
    assert runtime.network_registry() is None


def test_kernel_runtime_boots_identity(tmp_path) -> None:
    soul_file = tmp_path / "soul.md"
    soul_file.write_text(
        "# VERSION\nv2\n\n# WHO AM I\nKernel\n\n# PRIME DIRECTIVES\n- Safe\n\n# TONE OF VOICE\nDirect\n",
        encoding="utf-8",
    )
    bus = FakeBus()
    postgres = FakePostgresClient()
    KernelRuntime(
        KernelRuntimeConfig(
            redis_url="redis://localhost:6379",
            postgres_dsn="dsn",
            enable_discovery=False,
            soul_path=str(soul_file),
        ),
        bus=bus,
        redis_client=FakeRedisClient(),
        postgres_client=postgres,
        inbox_router=FakeRouter(),
        memory_router=FakeRouter(),
    )
    assert bus.data["SYS:SOUL:VERSION"] == "v2"
    assert postgres.identities[0][0] == "v2"
