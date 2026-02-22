import json
import os
import urllib.request
from typing import Any, cast

import pytest


def _get_base_url() -> str:
    base_url = os.getenv("SMOKE_BASE_URL")
    if not base_url:
        pytest.skip("SMOKE_BASE_URL not configured")
    return base_url.rstrip("/")


def _request_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = response.read().decode("utf-8")
    return cast(dict[str, Any], json.loads(payload))


def test_smoke_health() -> None:
    base_url = _get_base_url()
    payload = _request_json(f"{base_url}/v1/health")
    assert payload["status"] == "ok"


def test_smoke_ready() -> None:
    base_url = _get_base_url()
    payload = _request_json(f"{base_url}/v1/ready")
    assert payload["status"] in {"ok", "degraded"}


def test_smoke_metrics() -> None:
    base_url = _get_base_url()
    payload = _request_json(f"{base_url}/v1/metrics")
    assert "request_count" in payload
