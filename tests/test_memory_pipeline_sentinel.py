from workers._sentinels.memory_pipeline_sentinel import MemoryPipelineConfig, MemoryPipelineSentinel


class FakeRedisClient:
    def __init__(self) -> None:
        self.reads = [("1-0", {"text": "hello"})]

    def read_stream(self, stream: str, last_id: str, count: int):
        return self.reads


class FakePostgresClient:
    def __init__(self) -> None:
        self.semantic = []
        self.episodic = []

    def insert_semantic(self, content: str, tags, embedding):
        self.semantic.append((content, list(tags), list(embedding)))

    def insert_episodic(self, source: str, payload, importance: float):
        self.episodic.append((source, payload, importance))


def test_memory_pipeline_sentinel_consolidates() -> None:
    redis_client = FakeRedisClient()
    postgres_client = FakePostgresClient()
    sentinel = MemoryPipelineSentinel(
        MemoryPipelineConfig(hot_stream="SYS:MEMORY:HOT"),
        redis_client,
        postgres_client,
        embedder=lambda text: [0.1, 0.2],
    )
    sentinel.handle({"topic": "SYS:MEMORY:CONSOLIDATE"}, {})
    assert len(postgres_client.semantic) == 1
    assert len(postgres_client.episodic) == 1
