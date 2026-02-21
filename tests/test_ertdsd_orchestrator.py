from __future__ import annotations

import json
from typing import Any, Dict, Mapping

from kernel.orchestration.ertdsd_graph import (
    ERTDSDConfig,
    ERTDSDOrchestrator,
    ERTDSDSentinel,
    ERTDSDSentinelConfig,
)


class FakeBus:
    def __init__(self) -> None:
        self.published: list[Dict[str, Any]] = []

    def publish_stream(self, stream: str, data: Mapping[str, Any]) -> None:
        self.published.append({"stream": stream, "data": dict(data)})


class FakeApp:
    def __init__(self, nodes: Dict[str, Any], edges: Dict[str, list[str]], entry: str, end_state: str) -> None:
        self._nodes = nodes
        self._edges = edges
        self._entry = entry
        self._end_state = end_state

    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        current = self._entry
        result = dict(state)
        while current != self._end_state:
            handler = self._nodes[current]
            result = handler(result)
            next_nodes = self._edges.get(current, [])
            if not next_nodes:
                break
            current = next_nodes[0]
        return result


class FakeGraph:
    def __init__(self, end_state: str) -> None:
        self._end_state = end_state
        self.nodes: Dict[str, Any] = {}
        self.edges: Dict[str, list[str]] = {}
        self.entry: str | None = None

    def add_node(self, name: str, func: Any) -> None:
        self.nodes[name] = func

    def add_edge(self, source: str, target: str) -> None:
        self.edges.setdefault(source, []).append(target)

    def set_entry_point(self, name: str) -> None:
        self.entry = name

    def compile(self, checkpointer: Any = None) -> FakeApp:
        return FakeApp(self.nodes, self.edges, self.entry or "", self._end_state)


def test_ertdsd_orchestrator_publishes_all_stages() -> None:
    bus = FakeBus()
    end_state = "__end__"
    config = ERTDSDConfig()

    def graph_factory() -> FakeGraph:
        return FakeGraph(end_state)

    orchestrator = ERTDSDOrchestrator(
        config,
        bus,
        decide=lambda headers, payload: {"selected": "ok"},
        graph_factory=graph_factory,
        end_state=end_state,
    )

    result = orchestrator.invoke({"headers": {"request_id": "123"}, "payload": {"task": "demo"}})

    assert result["stage"] == "deploy"
    assert result["history"] == ["meeting", "spec", "code", "test", "deploy"]
    assert len(bus.published) == 5
    last = bus.published[-1]
    payload = json.loads(last["data"]["payload"])
    assert payload["stage"] == "deploy"
    assert payload["decision"]["selected"] == "ok"


def test_ertdsd_orchestrator_uses_checkpointer_factory() -> None:
    bus = FakeBus()
    end_state = "__end__"
    config = ERTDSDConfig()
    checkpoint_calls: list[str] = []

    def graph_factory() -> FakeGraph:
        return FakeGraph(end_state)

    def checkpointer_factory(dsn: str) -> Dict[str, str]:
        checkpoint_calls.append(dsn)
        return {"dsn": dsn}

    orchestrator = ERTDSDOrchestrator(
        config,
        bus,
        graph_factory=graph_factory,
        checkpointer_factory=checkpointer_factory,
        end_state=end_state,
    )

    orchestrator.build(checkpoint_dsn="postgresql://test")

    assert checkpoint_calls == ["postgresql://test"]


def test_ertdsd_sentinel_invokes_orchestrator() -> None:
    bus = FakeBus()
    end_state = "__end__"
    config = ERTDSDConfig()

    def graph_factory() -> FakeGraph:
        return FakeGraph(end_state)

    orchestrator = ERTDSDOrchestrator(
        config,
        bus,
        graph_factory=graph_factory,
        end_state=end_state,
    )
    sentinel = ERTDSDSentinel(ERTDSDSentinelConfig(topic="SYS:ERTDSD"), orchestrator)

    headers = {"topic": "SYS:ERTDSD"}
    payload = {"task": "demo"}

    assert sentinel.sentinel_scan(headers) is True
    sentinel.handle(headers, payload)
    assert len(bus.published) == 5
