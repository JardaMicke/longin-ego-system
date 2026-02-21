from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

from kernel.bus.redis_bus import RedisBus
from kernel.security.identity_firewall import IdentityFirewall


@dataclass(frozen=True)
class SupervisorConfig:
    inbox_stream: str = "SYS:INBOX"
    identity_flush_stream: str = "SYS:MEMORY:FLUSH"
    identity_flush_min_interval_seconds: float = 60.0


class Supervisor:
    def __init__(
        self,
        config: SupervisorConfig,
        bus: RedisBus,
        decide: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], Dict[str, Any]]] = None,
        identity_firewall: Optional[IdentityFirewall] = None,
    ) -> None:
        self._config = config
        self._bus = bus
        self._decide = decide
        self._identity_firewall = identity_firewall
        self._last_identity_flush_at: float | None = None

    def route(self, headers: Mapping[str, Any], payload: Mapping[str, Any]) -> str:
        decision: Dict[str, Any] = {}
        enriched_headers = dict(headers)
        if self._identity_firewall is not None:
            try:
                identity_hash, identity_changed = self._identity_firewall.get_identity_state()
                enriched_headers["identity_hash"] = identity_hash
                enriched_headers["identity_changed"] = str(identity_changed).lower()
                if identity_changed:
                    if self._should_flush():
                        self._bus.publish_stream(
                            self._config.identity_flush_stream,
                            {"identity_hash": identity_hash},
                        )
            except Exception as exc:
                raise RuntimeError(f"Identity state failed: {exc}") from exc
        if self._decide is not None:
            try:
                decision = self._decide(enriched_headers, payload)
            except Exception as exc:
                raise RuntimeError(f"Decision function failed: {exc}") from exc
        envelope = {
            "headers": json.dumps(enriched_headers),
            "payload": json.dumps(dict(payload)),
            "decision": json.dumps(decision),
        }
        try:
            return self._bus.publish_stream(self._config.inbox_stream, envelope)
        except Exception as exc:
            raise RuntimeError(f"Supervisor route failed: {exc}") from exc

    def _should_flush(self) -> bool:
        now = time.monotonic()
        if self._last_identity_flush_at is None:
            self._last_identity_flush_at = now
            return True
        if now - self._last_identity_flush_at >= self._config.identity_flush_min_interval_seconds:
            self._last_identity_flush_at = now
            return True
        return False
