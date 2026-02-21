from __future__ import annotations

from typing import Any, Callable, cast


class MCPServer:
    def __init__(self) -> None:
        try:
            from fastmcp import FastMCP
        except Exception as exc:
            raise RuntimeError(f"FastMCP import failed: {exc}") from exc
        self._server = FastMCP("longin-ego")

    def tool(self, name: str, description: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            try:
                return cast(Callable[..., Any], self._server.tool(name=name, description=description)(func))
            except Exception as exc:
                raise RuntimeError(f"Tool registration failed: {exc}") from exc

        return decorator

    def run(self) -> None:
        try:
            self._server.run()
        except Exception as exc:
            raise RuntimeError(f"MCP server run failed: {exc}") from exc
