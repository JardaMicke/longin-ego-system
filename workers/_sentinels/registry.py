from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


class Sentinel(Protocol):
    name: str

    def sentinel_scan(self, headers: Dict[str, Any]) -> bool:
        raise NotImplementedError("sentinel_scan must be implemented")

    def handle(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> None:
        raise NotImplementedError("handle must be implemented")


@dataclass(frozen=True)
class SentinelRegistration:
    name: str
    sentinel: Sentinel


class SentinelRegistry:
    def __init__(self) -> None:
        self._sentinels: Dict[str, Sentinel] = {}

    def register(self, sentinel: Sentinel) -> None:
        if sentinel.name in self._sentinels:
            raise RuntimeError(f"Sentinel already registered: {sentinel.name}")
        self._sentinels[sentinel.name] = sentinel

    def dispatch(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
        triggered: List[str] = []
        for name, sentinel in self._sentinels.items():
            try:
                if sentinel.sentinel_scan(headers):
                    sentinel.handle(headers, payload)
                    triggered.append(name)
            except Exception as exc:
                raise RuntimeError(f"Sentinel dispatch failed for {name}: {exc}") from exc
        return triggered
