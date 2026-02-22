from __future__ import annotations

import os
from typing import Optional


def read_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value:
        return value
    file_path = os.getenv(f"{name}_FILE")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read().strip()
        except Exception as exc:
            raise RuntimeError(f"Secret file read failed for {name}: {exc}") from exc
        if content:
            return content
    return default


def read_profiled(name: str, profile: str, default: Optional[str] = None) -> Optional[str]:
    profile_key = f"{profile.upper()}_{name}"
    value = os.getenv(profile_key)
    if value:
        return value
    file_path = os.getenv(f"{profile_key}_FILE")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read().strip()
        except Exception as exc:
            raise RuntimeError(f"Secret file read failed for {profile_key}: {exc}") from exc
        if content:
            return content
    return read_secret(name, default)


def read_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"Boolean parse failed for value: {value}")


def read_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception as exc:
        raise RuntimeError(f"Integer parse failed for value: {value}") from exc


def read_float(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except Exception as exc:
        raise RuntimeError(f"Float parse failed for value: {value}") from exc
