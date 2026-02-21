from __future__ import annotations

import socket
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, cast

from kernel.network.registry import NetworkRegistry


@dataclass
class DiscoveryConfig:
    service_type: str = "_longin-ego._tcp.local."
    service_name: str = "longin-ego"
    port: int = 8765
    properties: Dict[str, str] = field(default_factory=dict)
    hostname: Optional[str] = None
    node_id: Optional[str] = None
    advertise: bool = True
    browse: bool = True


class DiscoveryService:
    def __init__(self, config: DiscoveryConfig, registry: NetworkRegistry) -> None:
        self._config = config
        self._registry = registry
        self._zeroconf: Any | None = None
        self._service_info: Any | None = None
        self._browser: Any | None = None

    def start(self) -> None:
        try:
            from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf
        except Exception as exc:
            raise RuntimeError(f"Zeroconf import failed: {exc}") from exc
        if self._zeroconf is None:
            self._zeroconf = Zeroconf()
        zeroconf = self._zeroconf
        if zeroconf is None:
            raise RuntimeError("Zeroconf initialization failed")
        if self._config.advertise:
            info = ServiceInfo(
                type_=self._config.service_type,
                name=self._service_full_name(),
                addresses=[socket.inet_aton(self._resolve_address())],
                port=self._config.port,
                properties=self._build_properties(),
                server=self._hostname() + ".local.",
            )
            zeroconf.register_service(info)
            self._service_info = info
        if self._config.browse:
            listener = _ServiceListener(self._registry, self._config.service_type)
            self._browser = ServiceBrowser(zeroconf, self._config.service_type, cast(Any, listener))

    def stop(self) -> None:
        if self._zeroconf is None:
            return
        if self._service_info is not None:
            self._zeroconf.unregister_service(self._service_info)
        self._zeroconf.close()
        self._zeroconf = None
        self._service_info = None
        self._browser = None

    def registry(self) -> NetworkRegistry:
        return self._registry

    def _hostname(self) -> str:
        return self._config.hostname or socket.gethostname()

    def _resolve_address(self) -> str:
        return socket.gethostbyname(self._hostname())

    def _build_properties(self) -> Dict[bytes, bytes]:
        properties = dict(self._config.properties)
        node_id = self._config.node_id or self._hostname()
        properties.setdefault("node_id", node_id)
        properties.setdefault("hostname", self._hostname())
        return {str(key).encode(): str(value).encode() for key, value in properties.items()}

    def _service_full_name(self) -> str:
        return f"{self._config.service_name}.{self._config.service_type}"


class _ServiceListener:
    def __init__(self, registry: NetworkRegistry, service_type: str) -> None:
        self._registry = registry
        self._service_type = service_type

    def add_service(self, zeroconf: Any, service_type: str, name: str) -> None:
        self._update_service(zeroconf, name)

    def update_service(self, zeroconf: Any, service_type: str, name: str) -> None:
        self._update_service(zeroconf, name)

    def remove_service(self, zeroconf: Any, service_type: str, name: str) -> None:
        node_id = name.split(".", 1)[0]
        self._registry.remove(node_id)

    def _update_service(self, zeroconf: Any, name: str) -> None:
        info = zeroconf.get_service_info(self._service_type, name)
        if info is None or not info.addresses:
            return
        address = socket.inet_ntoa(info.addresses[0])
        properties = {key.decode(): value.decode() for key, value in info.properties.items()}
        node_id = properties.get("node_id") or name.split(".", 1)[0]
        hostname = properties.get("hostname") or node_id
        self._registry.upsert(
            node_id=node_id,
            hostname=hostname,
            address=address,
            port=info.port,
            properties=properties,
        )
