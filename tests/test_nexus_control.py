from kernel.mcp.nexus_control import NexusControlServer
from kernel.network.registry import NetworkRegistry


class FakeMCPServer:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self, name: str, description: str):
        def decorator(func):
            self.tools[name] = func
            return func

        return decorator

    def run(self) -> None:
        return None


class FakeGanglionClient:
    def __init__(self) -> None:
        self.calls = []

    def spawn(self, command: str, sandbox_mode: bool = True, env_vars=None):
        self.calls.append((command, sandbox_mode))
        return {"exit_code": 0, "output": "ok"}

    def close(self) -> None:
        return None


def test_nexus_control_tools(monkeypatch) -> None:
    monkeypatch.setattr("kernel.mcp.nexus_control.MCPServer", FakeMCPServer)
    registry = NetworkRegistry()
    registry.upsert(
        node_id="node-1",
        hostname="node-1",
        address="127.0.0.1",
        port=9999,
    )
    fake_client = FakeGanglionClient()

    def client_factory(node):
        return fake_client

    server = NexusControlServer(registry=registry, client_factory=client_factory)
    tools = server._server.tools
    result = tools["scan_network_resources"]()
    assert result[0]["node_id"] == "node-1"
    spawn_result = tools["delegate_computation"]("echo hi", "node-1", True)
    assert spawn_result["exit_code"] == 0
    assert fake_client.calls[0][0] == "echo hi"
