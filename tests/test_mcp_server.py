import types

from longin_sdk.mcp.server import MCPServer


class FakeFastMCP:
    def __init__(self, name: str) -> None:
        self.name = name

    def tool(self, name: str, description: str):
        def decorator(func):
            return func

        return decorator

    def run(self) -> None:
        return None


def test_mcp_server_tool(monkeypatch) -> None:
    fake_module = types.SimpleNamespace(FastMCP=FakeFastMCP)
    monkeypatch.setitem(__import__("sys").modules, "fastmcp", fake_module)
    server = MCPServer()

    @server.tool(name="t", description="d")
    def sample() -> str:
        return "ok"

    assert sample() == "ok"
