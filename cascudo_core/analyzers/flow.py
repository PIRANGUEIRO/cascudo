"""Flow — BFS depth 6 a partir de entrypoints, determinístico."""

from __future__ import annotations

import networkx as nx

from ..graph.builder import entrypoints


def build_flow(g: nx.DiGraph, depth: int = 6, entry: str | None = None) -> dict:
    eps = [entry] if entry and entry in g else entrypoints(g)
    if not eps:
        # fallback: maior out_degree
        eps = [max(g.nodes(), key=lambda n: g.out_degree(n))] if g.nodes else []

    visited: set[str] = set()
    frontier = list(eps)
    dist: dict[str, int] = {n: 0 for n in eps}
    flow_nodes: set[str] = set(eps)

    while frontier:
        nxt: list[str] = []
        for u in frontier:
            if dist[u] >= depth:
                continue
            for v in g.successors(u):
                if g.edges[u, v].get("kind") not in ("CALLS", "IMPORTS", "CONTAINS"):
                    continue
                if v not in visited:
                    visited.add(v)
                    dist[v] = dist[u] + 1
                    flow_nodes.add(v)
                    nxt.append(v)
        frontier = nxt

    sub = g.subgraph(flow_nodes).copy()

    nodes = [
        {
            "id": n,
            "kind": d.get("kind", "unknown"),
            "file": d.get("file"),
            "line": d.get("line"),
            "label": n.split(".")[-1],
            "depth": dist.get(n, 0),
        }
        for n, d in sub.nodes(data=True)
    ]
    edges = [
        {"source": u, "target": v, "kind": d.get("kind")}
        for u, v, d in sub.edges(data=True)
    ]

    return {"entrypoints": eps, "nodes": nodes, "edges": edges, "depth": depth}
