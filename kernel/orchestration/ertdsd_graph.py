from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from kernel.bus.redis_bus import RedisBus


@dataclass(frozen=True)
class ERTDSDConfig:
    """Účel: Definuje parametry a fáze ERTDSD orchestrace.

    Vstupy/Výstupy: Inbox stream a seznam fází pro workflow.
    Vedlejší efekty: Žádné.
    """
    inbox_stream: str = "SYS:INBOX"
    stages: Tuple[str, ...] = ("meeting", "spec", "code", "test", "deploy")


class ERTDSDOrchestrator:
    """Účel: Orchestrace ERTDSD workflow přes LangGraph a Redis Streams.

    Vstupy/Výstupy: Přijímá konfiguraci a RedisBus, publikuje stavy a vrací update stavu.
    Vedlejší efekty: Publikuje do Redis streamu, volitelně používá Postgres checkpointer.
    """
    def __init__(
        self,
        config: ERTDSDConfig,
        bus: RedisBus,
        decide: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], Dict[str, Any]]] = None,
        graph_factory: Optional[Callable[[], Any]] = None,
        checkpointer_factory: Optional[Callable[[str], Any]] = None,
        end_state: Optional[Any] = None,
    ) -> None:
        self._config = config
        self._bus = bus
        self._decide = decide
        self._graph_factory = graph_factory or self._default_graph_factory
        self._checkpointer_factory = checkpointer_factory or self._default_checkpointer_factory
        self._end_state = end_state
        self._app: Any = None

    def build(self, checkpoint_dsn: Optional[str] = None) -> None:
        graph = self._graph_factory()
        self._register_nodes(graph)
        self._register_edges(graph)
        if self._end_state is None:
            raise RuntimeError("Graph end state is not configured")
        checkpointer = None
        if checkpoint_dsn is not None:
            checkpointer = self._checkpointer_factory(checkpoint_dsn)
        try:
            self._app = graph.compile(checkpointer=checkpointer)
        except Exception as exc:
            raise RuntimeError(f"LangGraph compile failed: {exc}") from exc

    def invoke(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        if self._app is None:
            self.build()
        if self._app is None:
            raise RuntimeError("ERTDSD app is not initialized")
        try:
            return dict(self._app.invoke(dict(state)))
        except Exception as exc:
            raise RuntimeError(f"ERTDSD invoke failed: {exc}") from exc

    def _register_nodes(self, graph: Any) -> None:
        for stage in self._config.stages:
            graph.add_node(stage, self._make_stage_handler(stage))

    def _register_edges(self, graph: Any) -> None:
        if not self._config.stages:
            raise RuntimeError("ERTDSD stages are not configured")
        graph.set_entry_point(self._config.stages[0])
        for index, stage in enumerate(self._config.stages):
            if index < len(self._config.stages) - 1:
                graph.add_edge(stage, self._config.stages[index + 1])
            else:
                if self._end_state is None:
                    raise RuntimeError("Graph end state is not configured")
                graph.add_edge(stage, self._end_state)

    def _make_stage_handler(self, stage: str) -> Callable[[Mapping[str, Any]], Dict[str, Any]]:
        def handler(state: Mapping[str, Any]) -> Dict[str, Any]:
            headers = dict(state.get("headers", {}))
            payload = dict(state.get("payload", {}))
            decision: Dict[str, Any] = {}
            if self._decide is not None:
                try:
                    decision = self._decide(headers, payload)
                except Exception as exc:
                    raise RuntimeError(f"ERTDSD decision failed: {exc}") from exc
            headers["topic"] = f"ERTDSD:{stage.upper()}"
            payload["stage"] = stage
            if decision:
                payload["decision"] = decision
            try:
                self._bus.publish_stream(
                    self._config.inbox_stream,
                    {"headers": json.dumps(headers), "payload": json.dumps(payload)},
                )
            except Exception as exc:
                raise RuntimeError(f"ERTDSD publish failed for {stage}: {exc}") from exc
            history = list(state.get("history", []))
            history.append(stage)
            updated = dict(state)
            updated["headers"] = headers
            updated["payload"] = payload
            updated["stage"] = stage
            updated["history"] = history
            return updated

        return handler

    def _default_graph_factory(self) -> Any:
        try:
            from langgraph.graph import END, StateGraph
        except Exception as exc:
            raise RuntimeError(f"LangGraph import failed: {exc}") from exc
        self._end_state = END
        return StateGraph(dict)

    def _default_checkpointer_factory(self, dsn: str) -> Any:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
        except Exception as exc:
            raise RuntimeError(f"LangGraph PostgresSaver import failed: {exc}") from exc
        try:
            return PostgresSaver.from_conn_string(dsn)
        except Exception as exc:
            raise RuntimeError(f"PostgresSaver initialization failed: {exc}") from exc
