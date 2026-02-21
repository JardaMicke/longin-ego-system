from kernel.network.registry import NetworkRegistry


def test_network_registry_upsert_and_get() -> None:
    registry = NetworkRegistry(ttl_seconds=120.0)
    registry.upsert(
        node_id="node-1",
        hostname="host",
        address="127.0.0.1",
        port=8765,
        properties={"role": "ganglion"},
    )
    node = registry.get("node-1")
    assert node is not None
    assert node.node_id == "node-1"
    assert node.hostname == "host"
    assert node.address == "127.0.0.1"
    assert node.port == 8765
    assert node.properties["role"] == "ganglion"


def test_network_registry_purges_expired() -> None:
    registry = NetworkRegistry(ttl_seconds=1.0)
    registry.upsert(
        node_id="node-2",
        hostname="host",
        address="127.0.0.1",
        port=8765,
    )
    registry._nodes["node-2"].last_seen -= 10
    assert registry.get("node-2") is None
    assert registry.list_nodes() == []
