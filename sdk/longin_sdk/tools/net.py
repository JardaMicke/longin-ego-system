from __future__ import annotations

import ipaddress
from typing import Mapping, Optional
from urllib.parse import urlparse

import httpx

from longin_sdk.core.exceptions import PermissionError


class SafeHttpClient:
    """Účel: Bezpečný HTTP klient s blokací privátních sítí.

    Vstupy/Výstupy: Přijímá URL a volitelné headers, vrací text odpovědi.
    Vedlejší efekty: Síťové volání přes HTTPX.
    """
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout = timeout_seconds

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise PermissionError("Only http/https are allowed")
        host = parsed.hostname or ""
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise PermissionError("Private network access is blocked")

    def get(self, url: str, headers: Optional[Mapping[str, str]] = None) -> str:
        self._validate_url(url)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as exc:
            raise RuntimeError(f"HTTP GET failed: {exc}") from exc
