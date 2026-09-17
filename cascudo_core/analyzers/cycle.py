"""Cycles — SCC via networkx, determinístico."""

from __future__ import annotations

import networkx as nx


def find_cycles(g: nx.DiGraph) -> list[list[str]]:
    # só considera CALLS e IMPORTS
    h = nx.DiGraph()
    h.add_nodes_from(g.nodes(data=True))
    for u, v, d in g.edges(data=True):
        if d.get("kind") in ("CALLS", "IMPORTS"):
            h.add_edge(u, v)

    sccs = list(nx.strongly_connected_components(h))
    cycles = [sorted(list(c)) for c in sccs if len(c) > 1]
    # self-loop
    for n in h.nodes():
        if h.has_edge(n, n):
            cycles.append([n])

    return sorted(cycles)
