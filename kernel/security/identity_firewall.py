from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class IdentityConfig:
    soul_path: str
    redis_key: str = "SYS:SOUL:CURRENT"


class IdentityFirewall:
    def __init__(self, config: IdentityConfig, bus: RedisBus) -> None:
        self._config = config
        self._bus = bus
        self._last_hash: Optional[str] = None

    def load_identity(self) -> str:
        current_hash, _ = self.get_identity_state()
        return current_hash

    def has_changed(self) -> bool:
        _, changed = self.get_identity_state()
        return changed

    def get_identity_state(self) -> tuple[str, bool]:
        current_hash = self._compute_hash()
        if self._last_hash is None:
            self._store_hash(current_hash)
            self._last_hash = current_hash
            return current_hash, False
        if current_hash != self._last_hash:
            self._store_hash(current_hash)
            self._last_hash = current_hash
            return current_hash, True
        return current_hash, False

    def _compute_hash(self) -> str:
        try:
            with open(self._config.soul_path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except Exception as exc:
            raise RuntimeError(f"Failed to read soul file: {exc}") from exc
        try:
            current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception as exc:
            raise RuntimeError(f"Failed to hash soul file: {exc}") from exc
        return current_hash

    def _store_hash(self, current_hash: str) -> None:
        try:
            self._bus.set_key(self._config.redis_key, current_hash)
        except Exception as exc:
            raise RuntimeError(f"Failed to store soul hash: {exc}") from exc
