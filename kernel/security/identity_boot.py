from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

from kernel.bus.redis_bus import RedisBus
from memory.postgres.client import PostgresClient


@dataclass(frozen=True)
class IdentityBootConfig:
    """Účel: Konfiguruje načtení identity ze soul souboru.

    Vstupy/Výstupy: Cesta k soul.md a klíče pro Redis.
    Vedlejší efekty: Žádné.
    """
    soul_path: str
    redis_hash_key: str = "SYS:SOUL:CURRENT"
    redis_version_key: str = "SYS:SOUL:VERSION"
    redis_directives_key: str = "SYS:SOUL:DIRECTIVES"


class IdentityBootLoader:
    """Účel: Načte identitu ze soul souboru a uloží ji do Redis/Postgres.

    Vstupy/Výstupy: Přijímá RedisBus a PostgresClient, vrací payload direktiv a verze.
    Vedlejší efekty: Čte soubor a zapisuje do Redis/Postgres.
    """
    def __init__(self, config: IdentityBootConfig) -> None:
        self._config = config

    def boot(self, bus: RedisBus, postgres: PostgresClient) -> Dict[str, object]:
        content = self._read_soul()
        soul_hash = self._hash_content(content)
        version, directives = self._parse_directives(content)
        payload: Dict[str, object] = dict(directives)
        payload["version"] = version
        try:
            bus.set_key(self._config.redis_hash_key, soul_hash)
            bus.set_key(self._config.redis_version_key, version)
            bus.set_key(self._config.redis_directives_key, json.dumps(payload))
        except Exception as exc:
            raise RuntimeError(f"Identity boot redis failed: {exc}") from exc
        try:
            postgres.insert_identity(version=version, soul_hash=soul_hash, directives=payload)
        except Exception as exc:
            raise RuntimeError(f"Identity boot postgres failed: {exc}") from exc
        return payload

    def _read_soul(self) -> str:
        try:
            with open(self._config.soul_path, "r", encoding="utf-8") as handle:
                return handle.read()
        except Exception as exc:
            raise RuntimeError(f"Failed to read soul file: {exc}") from exc

    def _hash_content(self, content: str) -> str:
        try:
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception as exc:
            raise RuntimeError(f"Failed to hash soul file: {exc}") from exc

    def _parse_directives(self, content: str) -> Tuple[str, Dict[str, List[str]]]:
        sections: Dict[str, List[str]] = {"who_am_i": [], "prime_directives": [], "tone_of_voice": []}
        version = "v1"
        current: str | None = None
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lowered = stripped.lower()
            if lowered.startswith("version:"):
                version = stripped.split(":", 1)[1].strip() or version
                current = None
                continue
            if stripped.startswith("#"):
                title = stripped.lstrip("#").strip().upper()
                if title == "WHO AM I":
                    current = "who_am_i"
                elif title == "PRIME DIRECTIVES":
                    current = "prime_directives"
                elif title == "TONE OF VOICE":
                    current = "tone_of_voice"
                elif title == "VERSION":
                    current = "version"
                else:
                    current = None
                continue
            if current == "version":
                version = stripped or version
                continue
            if current in sections:
                sections[current].append(self._normalize_line(stripped))
        return version, sections

    def _normalize_line(self, line: str) -> str:
        if line.startswith(("- ", "* ")):
            return line[2:].strip()
        return line
