from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional


@dataclass
class NetworkNode:
    """Účel: Ukládá metadata o objeveném uzlu v síti.

    Vstupy/Výstupy: Identifikátor, adresa, port a properties uzlu.
    Vedlejší efekty: Žádné.
    """
    node_id: str
    hostname: str
    address: str
    port: int
    properties: Dict[str, str] = field(default_factory=dict)
    last_seen: float = field(default_factory=lambda: time.time())


class NetworkRegistry:
    """Účel: Registr uzlů s TTL a základními CRUD operacemi.

    Vstupy/Výstupy: Přijímá TTL, vrací uzly a seznamy uzlů.
    Vedlejší efekty: Časové purge expirovaných uzlů.
    """
    def __init__(self, ttl_seconds: float = 120.0) -> None:
        self._ttl_seconds = ttl_seconds
        self._nodes: Dict[str, NetworkNode] = {}

    def upsert(
        self,
        node_id: str,
        hostname: str,
        address: str,
        port: int,
        properties: Optional[Mapping[str, str]] = None,
    ) -> NetworkNode:
        node = NetworkNode(
            node_id=node_id,
            hostname=hostname,
            address=address,
            port=port,
            properties=dict(properties or {}),
            last_seen=time.time(),
        )
        self._nodes[node_id] = node
        return node

    def remove(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)

    def get(self, node_id: str) -> Optional[NetworkNode]:
        self._purge_expired()
        return self._nodes.get(node_id)

    def list_nodes(self) -> List[NetworkNode]:
        self._purge_expired()
        return list(self._nodes.values())

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [node_id for node_id, node in self._nodes.items() if now - node.last_seen > self._ttl_seconds]
        for node_id in expired:
            self._nodes.pop(node_id, None)
