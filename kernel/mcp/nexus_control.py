from __future__ import annotations

from typing import Callable, Dict, List

from kernel.network.ganglion_client import GanglionClient
from kernel.network.registry import NetworkNode, NetworkRegistry
from longin_sdk.mcp.server import MCPServer


class NexusControlServer:
    """Účel: MCP server pro discovery Ganglion uzlů a delegaci výpočtu.

    Vstupy/Výstupy: Přijímá NetworkRegistry, vystavuje MCP nástroje.
    Vedlejší efekty: Spouští MCP server a provádí síťové volání na uzly.
    """
    def __init__(
        self,
        registry: NetworkRegistry,
        client_factory: Callable[[NetworkNode], GanglionClient] | None = None,
    ) -> None:
        self._registry = registry
        self._client_factory = client_factory or self._default_client_factory
        self._server = MCPServer()
        self._register_tools()

    def run(self) -> None:
        self._server.run()

    def _register_tools(self) -> None:
        @self._server.tool(
            name="scan_network_resources",
            description="List discovered Ganglion nodes with basic capabilities.",
        )
        def scan_network_resources() -> List[Dict[str, object]]:
            nodes = self._registry.list_nodes()
            return [
                {
                    "node_id": node.node_id,
                    "hostname": node.hostname,
                    "address": node.address,
                    "port": node.port,
                    "properties": node.properties,
                }
                for node in nodes
            ]

        @self._server.tool(
            name="delegate_computation",
            description="Execute a command on a Ganglion node.",
        )
        def delegate_computation(
            command: str,
            target_node: str,
            sandbox_mode: bool = True,
        ) -> Dict[str, object]:
            node = self._registry.get(target_node)
            if node is None:
                raise RuntimeError(f"Target node not found: {target_node}")
            client = self._client_factory(node)
            try:
                return client.spawn(command=command, sandbox_mode=sandbox_mode)
            finally:
                client.close()

    def _default_client_factory(self, node: NetworkNode) -> GanglionClient:
        base_url = f"http://{node.address}:{node.port}"
        return GanglionClient(base_url)
