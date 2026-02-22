from typing import Any, Mapping

from _pytest.monkeypatch import MonkeyPatch

from ganglion import api
from ganglion.metrics import MetricsState


class FakePostgresClient:
    def __init__(self, ok: bool, error: str | None = None) -> None:
        self._ok = ok
        self._error = error

    def health_check(self) -> tuple[bool, str | None]:
        return self._ok, self._error


def test_health_returns_status() -> None:
    payload: Mapping[str, Any] = api.health()
    assert payload["status"] == "ok"
    assert payload["uptime_seconds"] >= 0


def test_readiness_ok(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(api, "_get_postgres_client", lambda: FakePostgresClient(True, None))
    payload: Mapping[str, Any] = api.readiness()
    assert payload["status"] == "ok"
    assert payload["postgres"]["ok"] is True


def test_readiness_degraded(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(api, "_get_postgres_client", lambda: FakePostgresClient(False, "down"))
    payload: Mapping[str, Any] = api.readiness()
    assert payload["status"] == "degraded"
    assert payload["postgres"]["ok"] is False


def test_metrics_snapshot(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(api, "metrics_state", MetricsState())
    api.metrics_state.record_request("/v1/health", 200, None)
    payload: Mapping[str, Any] = api.metrics()
    assert payload["request_count"] == 1
    assert payload["status_codes"][200] == 1
