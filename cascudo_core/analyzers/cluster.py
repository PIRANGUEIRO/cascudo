"""Clustering — Louvain via networkx (determinístico, sem IA)."""

from __future__ import annotations

import networkx as nx

try:
    from networkx.algorithms.community import louvain_communities  # type: ignore

    HAS_LOUVAIN = True
except Exception:
    HAS_LOUVAIN = False


def find_clusters(g: nx.DiGraph) -> list[dict]:
    # Louvain precisa de undirected
    ug = g.to_undirected()
    # filtra só CALLS/IMPORTS/CONTAINS para não criar clusters por file isolado
    # já está no grafo; usa todo o grafo mas pondera
    if HAS_LOUVAIN and ug.number_of_nodes() >= 3:
        try:
            comms = louvain_communities(ug, seed=42)
        except Exception:
            comms = list(nx.connected_components(ug))
    else:
        comms = list(nx.connected_components(ug))

    clusters = []
    for i, c in enumerate(comms):
        sub = g.subgraph(c)
        clusters.append(
            {
                "id": f"cluster-{i}",
                "size": len(c),
                "nodes": sorted(list(c))[:20],
                "density": round(nx.density(sub), 3) if len(c) > 1 else 0,
                "label": f"Cluster {i} ({len(c)} nodes)",
            }
        )
    # ordena por tamanho desc — hairball mitigation
    clusters.sort(key=lambda x: x["size"], reverse=True)
    return clusters
