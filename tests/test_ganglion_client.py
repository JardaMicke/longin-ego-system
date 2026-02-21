import json

import httpx

from kernel.network.ganglion_client import GanglionClient


def test_ganglion_client_capabilities() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/capabilities":
            return httpx.Response(200, json={"hostname": "node-a"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    ganglion = GanglionClient("http://localhost:9999", client=client)
    result = ganglion.capabilities()
    assert result["hostname"] == "node-a"


def test_ganglion_client_spawn() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/spawn":
            payload = json.loads(request.content.decode())
            assert payload["command"] == "echo hi"
            return httpx.Response(200, json={"exit_code": 0, "output": "hi"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    ganglion = GanglionClient("http://localhost:9999", client=client)
    result = ganglion.spawn("echo hi", sandbox_mode=True)
    assert result["exit_code"] == 0
    assert result["output"] == "hi"


def test_ganglion_client_telemetry() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/telemetry":
            return httpx.Response(200, json={"hostname": "node-a", "timestamp": "now"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    ganglion = GanglionClient("http://localhost:9999", client=client)
    result = ganglion.telemetry()
    assert result["hostname"] == "node-a"


def test_ganglion_client_identity_audit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/identity-audit":
            assert request.url.params.get("event") == "boot"
            assert request.url.params.get("version") == "v1"
            return httpx.Response(200, json={"items": [{"event": "boot"}]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    ganglion = GanglionClient("http://localhost:9999", client=client)
    result = ganglion.identity_audit(event="boot", version="v1", limit=10)
    assert result["items"][0]["event"] == "boot"


def test_ganglion_client_identity_audit_prune() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/identity-audit/prune":
            payload = json.loads(request.content.decode())
            assert payload["older_than_days"] == 7
            assert payload["keep_latest"] == 100
            return httpx.Response(200, json={"deleted": 5})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    ganglion = GanglionClient("http://localhost:9999", client=client)
    result = ganglion.identity_audit_prune(older_than_days=7, keep_latest=100)
    assert result["deleted"] == 5
