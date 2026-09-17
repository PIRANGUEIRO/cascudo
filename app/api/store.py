"""Store escalável — InMemory para protótipo, Postgres (Neon) em prod via DATABASE_URL."""

from __future__ import annotations

import os
from typing import Protocol
import networkx as nx


class Store(Protocol):
    async def save_snapshot(self, snapshot_id: str, workspace_id: str, g: nx.DiGraph, stats: dict) -> None: ...
    async def load_graph(self, snapshot_id: str) -> nx.DiGraph: ...
    async def save_patterns(self, snapshot_id: str, patterns: list[dict]) -> None: ...
    async def get_patterns(self, snapshot_id: str) -> list[dict]: ...
    async def get_corpus_stats(self) -> dict: ...


class InMemoryStore:
    """Protótipo — sem Postgres, mas com mesma interface. Troca por PostgresStore quando DATABASE_URL set."""

    def __init__(self) -> None:
        self._graphs: dict[str, nx.DiGraph] = {}
        self._meta: dict[str, dict] = {}
        self._patterns: dict[str, list[dict]] = {}
        self._corpus: dict[str, dict] = {}  # hash -> {count, canonical, kind}
        self._total = 0
        self._workspaces: dict[str, list[str]] = {}  # workspace_id -> [snapshot_ids]

    async def save_snapshot(self, snapshot_id: str, workspace_id: str, g: nx.DiGraph, stats: dict) -> None:
        self._graphs[snapshot_id] = g.copy()
        self._meta[snapshot_id] = {"workspace_id": workspace_id, **stats}
        self._total += 1
        self._workspaces.setdefault(workspace_id, []).append(snapshot_id)

    async def load_graph(self, snapshot_id: str) -> nx.DiGraph:
        if snapshot_id not in self._graphs:
            raise KeyError(snapshot_id)
        return self._graphs[snapshot_id].copy()

    async def save_patterns(self, snapshot_id: str, patterns: list[dict]) -> None:
        self._patterns[snapshot_id] = patterns
        for p in patterns:
            h = p["hash"]
            if h not in self._corpus:
                self._corpus[h] = {"count": 0, "canonical": p["canonical"], "kind": p["kind"]}
            self._corpus[h]["count"] += 1  # type: ignore

    async def get_patterns(self, snapshot_id: str) -> list[dict]:
        return self._patterns.get(snapshot_id, [])

    async def get_corpus_stats(self) -> dict:
        # retorna p/corpus_stats materializado
        total = self._total
        per_lang: dict[str, int] = {}
        for g in self._graphs.values():
            for _, d in g.nodes(data=True):
                lang = d.get("lang")
                if lang:
                    per_lang[lang] = per_lang.get(lang, 0) + 1
        return {"total_snapshots": total, "per_lang": per_lang, "unique_patterns": len(self._corpus), "corpus": self._corpus}

    async def list_snapshots(self, workspace_id: str) -> list[dict]:
        ids = self._workspaces.get(workspace_id, [])
        return [{"id": sid, **self._meta[sid]} for sid in ids]

    # compat
    async def get_corpus(self) -> tuple[dict, int]:
        return self._corpus, self._total


# Singleton escalável — em prod, factory retorna PostgresStore se DATABASE_URL
_store: Store | None = None


def get_store() -> InMemoryStore:
    global _store
    if _store is None:
        # se DATABASE_URL presente e quiser Postgres, trocar aqui
        # if os.getenv("DATABASE_URL"): _store = PostgresStore(...)
        _store = InMemoryStore()  # type: ignore[assignment]
    return _store  # type: ignore[return-value]
