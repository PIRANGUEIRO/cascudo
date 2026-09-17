"""Diff determinístico entre snapshots — F8, 0 IA."""

from __future__ import annotations

import networkx as nx


def diff_graphs(g1: nx.DiGraph, g2: nx.DiGraph) -> dict:
    n1 = set(g1.nodes())
    n2 = set(g2.nodes())
    e1 = set(g1.edges())
    e2 = set(g2.edges())

    added_nodes = sorted(list(n2 - n1))
    removed_nodes = sorted(list(n1 - n2))
    common = n1 & n2

    # changed = mesmo id mas attrs diferentes (ex: cc mudou)
    changed = []
    for n in common:
        if g1.nodes[n] != g2.nodes[n]:
            changed.append({"id": n, "before": dict(g1.nodes[n]), "after": dict(g2.nodes[n])})

    added_edges = sorted(list(e2 - e1))
    removed_edges = sorted(list(e1 - e2))

    # dead introduzido = dead em g2 que não existia em g1
    from .analyzers import find_dead

    dead2 = {d["qualified_name"] for d in find_dead(g2)}
    dead1 = {d["qualified_name"] for d in find_dead(g1)}
    dead_introduced = sorted(list(dead2 - dead1))
    dead_removed = sorted(list(dead1 - dead2))

    return {
        "nodes": {"added": added_nodes, "removed": removed_nodes, "changed": changed, "common": len(common)},
        "edges": {"added": added_edges, "removed": removed_edges},
        "dead": {"introduced": dead_introduced, "removed": dead_removed},
        "summary": f"+{len(added_nodes)} nodes -{len(removed_nodes)} ±{len(changed)} · +{len(added_edges)} edges · dead +{len(dead_introduced)}",
    }
