from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Optional

from kernel.arbiter.core import Arbiter, ArbiterPolicy
from kernel.bus.inbox_router import InboxRouter, InboxRouterConfig
from kernel.bus.memory_router import MemoryRouter, MemoryRouterConfig
from kernel.bus.redis_bus import RedisBus, RedisBusConfig
from kernel.chronos.heartbeat import ChronosConfig, ChronosHeartbeat
from kernel.embeddings.simple_embedder import SimpleEmbedder
from kernel.network.discovery import DiscoveryConfig, DiscoveryService
from kernel.network.registry import NetworkRegistry
from kernel.security.identity_boot import IdentityBootConfig, IdentityBootLoader
from kernel.security.identity_firewall import IdentityConfig, IdentityFirewall
from memory.postgres.client import PostgresClient, PostgresConfig
from memory.redis.client import RedisClient, RedisConfig
from workers._sentinels.chronos_sentinel import ChronosSentinel, ChronosSentinelConfig
from workers._sentinels.memory_consolidate_sentinel import (
    MemoryConsolidateConfig,
    MemoryConsolidateSentinel,
)
from workers._sentinels.memory_pipeline_sentinel import MemoryPipelineConfig, MemoryPipelineSentinel
from workers._sentinels.registry import SentinelRegistry


@dataclass(frozen=True)
class KernelRuntimeConfig:
    """Účel: Konfiguruje běh kernel runtime a přístup k infrastruktuře.

    Vstupy/Výstupy: URL/DSN pro Redis/Postgres, volby discovery a heartbeat period.
    Vedlejší efekty: Žádné.
    """
    redis_url: str
    postgres_dsn: str
    redis_memory_url: Optional[str] = None
    soul_path: Optional[str] = None
    poll_interval_seconds: float = 1.0
    heartbeat_period_seconds: float = 15.0
    enable_discovery: bool = True
    discovery_port: int = 8765
    discovery_service_name: str = "longin-ego"
    node_id: Optional[str] = None


class KernelRuntime:
    """Účel: Skládá a spouští všechny klíčové subsystémy jádra.

    Vstupy/Výstupy: Přijímá konfiguraci a volitelné závislosti, poskytuje běh smyčky a registry.
    Vedlejší efekty: Připojuje se k Redis/Postgres, spouští discovery a heartbeat, publikuje zprávy.
    """
    def __init__(
        self,
        config: KernelRuntimeConfig,
        bus: Optional[RedisBus] = None,
        redis_client: Optional[RedisClient] = None,
        postgres_client: Optional[PostgresClient] = None,
        embedder: Optional[SimpleEmbedder] = None,
        registry: Optional[SentinelRegistry] = None,
        inbox_router: Optional[InboxRouter] = None,
        memory_router: Optional[MemoryRouter] = None,
    ) -> None:
        self._config = config
        self._bus = bus or RedisBus(RedisBusConfig(url=config.redis_url))
        self._redis_client = redis_client or RedisClient(
            RedisConfig(url=config.redis_memory_url or config.redis_url)
        )
        self._postgres_client = postgres_client or PostgresClient(PostgresConfig(dsn=config.postgres_dsn))
        self._embedder = embedder or SimpleEmbedder()
        self._registry = registry or SentinelRegistry()
        self._identity_firewall = self._build_identity_firewall()
        self._boot_identity()
        self._discovery = self._build_discovery()
        self._chronos = ChronosHeartbeat(
            ChronosConfig(period_seconds=config.heartbeat_period_seconds),
            self._bus,
            on_phase=self._publish_phase,
        )
        self._inbox_router = inbox_router or InboxRouter(
            InboxRouterConfig(),
            self._bus,
            self._registry,
            identity_firewall=self._identity_firewall,
        )
        pipeline = MemoryPipelineSentinel(
            MemoryPipelineConfig(),
            self._redis_client,
            self._postgres_client,
            self._embedder.embed,
        )
        self._memory_router = memory_router or MemoryRouter(
            MemoryRouterConfig(),
            self._bus,
            pipeline,
        )
        self._chronos_task: Optional[asyncio.Task[None]] = None
        self._running = False
        self._register_default_sentinels()

    async def run(self) -> None:
        if self._running:
            return
        self._running = True
        if self._discovery is not None:
            self._discovery.start()
        self._chronos_task = asyncio.create_task(self._chronos.run())
        try:
            while self._running:
                self._inbox_router.poll_once()
                self._memory_router.poll_once()
                await asyncio.sleep(self._config.poll_interval_seconds)
        except Exception as exc:
            self._running = False
            raise RuntimeError(f"Kernel runtime failed: {exc}") from exc
        finally:
            await self.stop()

    async def stop(self) -> None:
        self._running = False
        self._chronos.stop()
        if self._chronos_task is not None:
            self._chronos_task.cancel()
            try:
                await self._chronos_task
            except Exception:
                pass
        if self._discovery is not None:
            self._discovery.stop()

    def network_registry(self) -> Optional[NetworkRegistry]:
        if self._discovery is None:
            return None
        return self._discovery.registry()

    def _publish_phase(self, phase: str) -> None:
        payload = {"phase": phase}
        headers = {"topic": "SYS:HEARTBEAT"}
        self._bus.publish_stream("SYS:INBOX", {"headers": json.dumps(headers), "payload": json.dumps(payload)})

    def _register_default_sentinels(self) -> None:
        arbiter = Arbiter(ArbiterPolicy())
        chronos_sentinel = ChronosSentinel(ChronosSentinelConfig(), self._bus, arbiter)
        memory_consolidate = MemoryConsolidateSentinel(MemoryConsolidateConfig(), self._bus)
        for sentinel in (chronos_sentinel, memory_consolidate):
            try:
                self._registry.register(sentinel)
            except Exception:
                continue

    def _build_identity_firewall(self) -> Optional[IdentityFirewall]:
        if not self._config.soul_path:
            return None
        return IdentityFirewall(IdentityConfig(soul_path=self._config.soul_path), self._bus)

    def _boot_identity(self) -> None:
        if not self._config.soul_path:
            return
        loader = IdentityBootLoader(IdentityBootConfig(soul_path=self._config.soul_path))
        loader.boot(self._bus, self._postgres_client)

    def _build_discovery(self) -> Optional[DiscoveryService]:
        if not self._config.enable_discovery:
            return None
        registry = NetworkRegistry()
        discovery_config = DiscoveryConfig(
            service_name=self._config.discovery_service_name,
            port=self._config.discovery_port,
            node_id=self._config.node_id,
            advertise=True,
            browse=True,
        )
        return DiscoveryService(discovery_config, registry)
