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
