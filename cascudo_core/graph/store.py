"""Store abstrato — permite trocar Postgres por memória sem quebrar core."""

from __future__ import annotations

from typing import Protocol
import networkx as nx


class GraphStore(Protocol):
    async def save_snapshot(self, snapshot_id: str, g: nx.DiGraph, stats: dict) -> None: ...
    async def load_graph(self, snapshot_id: str) -> nx.DiGraph: ...
    async def list_snapshots(self, workspace_id: str) -> list[dict]: ...


class InMemoryStore:
    """Para protótipo e testes — sem Postgres."""

    def __init__(self) -> None:
        self._graphs: dict[str, nx.DiGraph] = {}
        self._meta: dict[str, dict] = {}

    async def save_snapshot(self, snapshot_id: str, g: nx.DiGraph, stats: dict) -> None:
        self._graphs[snapshot_id] = g.copy()
        self._meta[snapshot_id] = stats

    async def load_graph(self, snapshot_id: str) -> nx.DiGraph:
        return self._graphs[snapshot_id].copy()

    async def list_snapshots(self, workspace_id: str) -> list[dict]:
        return [dict(id=k, **v) for k, v in self._meta.items()]
