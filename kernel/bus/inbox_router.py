from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, cast

from kernel.bus.redis_bus import RedisBus
from kernel.security.identity_firewall import IdentityFirewall
from workers._sentinels.registry import SentinelRegistry


@dataclass(frozen=True)
class InboxRouterConfig:
    """Účel: Konfigurace parametrů pro čtení inbox streamu.

    Vstupy/Výstupy: Stream, batch size a pravidla pro flush identity.
    Vedlejší efekty: Žádné.
    """
    stream: str = "SYS:INBOX"
    start_id: str = "0-0"
    batch_size: int = 10
    identity_flush_stream: str = "SYS:MEMORY:FLUSH"
    identity_flush_min_interval_seconds: float = 60.0


class InboxRouter:
    """Účel: Zpracovává inbox stream a deleguje na sentinely.

    Vstupy/Výstupy: Přijímá config, RedisBus a registry, vrací seznam triggerů.
    Vedlejší efekty: Čte/publikuje Redis streamy a vyvolává identity firewall.
    """
    def __init__(
        self,
        config: InboxRouterConfig,
        bus: RedisBus,
        registry: SentinelRegistry,
        identity_firewall: IdentityFirewall | None = None,
    ) -> None:
        self._config = config
        self._bus = bus
        self._registry = registry
        self._identity_firewall = identity_firewall
        self._last_id = config.start_id
        self._last_identity_flush_at: float | None = None

    def poll_once(self) -> List[Tuple[str, List[str]]]:
        entries = self._bus.read_stream(self._config.stream, self._last_id, self._config.batch_size)
        results: List[Tuple[str, List[str]]] = []
        for message_id, data in entries:
            self._last_id = message_id
            headers = self._decode_json(data.get("headers", "{}"))
            payload = self._decode_json(data.get("payload", "{}"))
            if self._identity_firewall is not None:
                try:
                    identity_hash, identity_changed = self._identity_firewall.get_identity_state()
                    headers["identity_hash"] = identity_hash
                    headers["identity_changed"] = str(identity_changed).lower()
                    if identity_changed:
                        if self._should_flush():
                            self._bus.publish_stream(
                                self._config.identity_flush_stream,
                                {"identity_hash": identity_hash},
                            )
                except Exception as exc:
                    raise RuntimeError(f"Identity state failed: {exc}") from exc
            triggered = self._registry.dispatch(headers, payload)
            results.append((message_id, triggered))
        return results

    def _decode_json(self, raw: Any) -> Dict[str, Any]:
        try:
            if isinstance(raw, str):
                return cast(Dict[str, Any], json.loads(raw))
            return cast(Dict[str, Any], dict(raw))
        except Exception as exc:
            raise RuntimeError(f"Inbox decode failed: {exc}") from exc

    def _should_flush(self) -> bool:
        now = time.monotonic()
        if self._last_identity_flush_at is None:
            self._last_identity_flush_at = now
            return True
        if now - self._last_identity_flush_at >= self._config.identity_flush_min_interval_seconds:
            self._last_identity_flush_at = now
            return True
        return False
