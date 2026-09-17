"""Dead code — in_degree==0, determinístico."""

from __future__ import annotations

import networkx as nx


def find_dead(g: nx.DiGraph, confidence: str = "all") -> list[dict]:
    dead: list[dict] = []
    for n, d in g.nodes(data=True):
        kind = d.get("kind")
        if kind not in ("function", "method", "class", "route"):
            continue
        if d.get("is_entrypoint"):
            continue
        if d.get("is_exported"):
            # exportado pode ser usado externamente — suspect, não dead high
            conf = "low"
        else:
            # só CALLS conta; IMPORTS não conta como uso
            indeg = sum(1 for _, _, ed in g.in_edges(n, data=True) if ed.get("kind") == "CALLS")
            if indeg == 0:
                conf = "high"
            else:
                continue

        if confidence != "all" and conf != confidence:
            continue

        dead.append(
            {
                "qualified_name": n,
                "file": d.get("file"),
                "line": d.get("line"),
                "kind": kind,
                "confidence": conf,
                "reason": "in_degree==0 (CALLS)",
            }
        )
    return sorted(dead, key=lambda x: (x["confidence"], x["file"]))
