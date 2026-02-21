from __future__ import annotations

from typing import Any, Dict, Optional, cast

import httpx


class GanglionClient:
    """Účel: HTTP klient pro komunikaci s Ganglion API.

    Vstupy/Výstupy: Přijímá base_url, vrací JSON odpovědi capabilities/spawn.
    Vedlejší efekty: Síťové požadavky přes HTTPX.
    """
    def __init__(self, base_url: str, client: Optional[httpx.Client] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=10.0)

    def capabilities(self) -> Dict[str, Any]:
        try:
            response = self._client.get(f"{self._base_url}/v1/capabilities")
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as exc:
            raise RuntimeError(f"Ganglion capabilities failed: {exc}") from exc

    def spawn(
        self,
        command: str,
        sandbox_mode: bool = True,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "command": command,
            "sandbox_mode": sandbox_mode,
            "env_vars": env_vars or {},
        }
        try:
            response = self._client.post(f"{self._base_url}/v1/spawn", json=payload)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as exc:
            raise RuntimeError(f"Ganglion spawn failed: {exc}") from exc

    def telemetry(self) -> Dict[str, Any]:
        try:
            response = self._client.get(f"{self._base_url}/v1/telemetry")
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as exc:
            raise RuntimeError(f"Ganglion telemetry failed: {exc}") from exc

    def identity_audit(
        self,
        event: Optional[str] = None,
        version: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": limit}
        if event:
            params["event"] = event
        if version:
            params["version"] = version
        try:
            response = self._client.get(f"{self._base_url}/v1/identity-audit", params=params)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as exc:
            raise RuntimeError(f"Ganglion identity audit failed: {exc}") from exc

    def identity_audit_prune(
        self,
        older_than_days: Optional[int] = None,
        keep_latest: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = {"older_than_days": older_than_days, "keep_latest": keep_latest}
        try:
            response = self._client.post(f"{self._base_url}/v1/identity-audit/prune", json=payload)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as exc:
            raise RuntimeError(f"Ganglion identity audit prune failed: {exc}") from exc

    def close(self) -> None:
        self._client.close()
