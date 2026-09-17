"""Critical nodes — god nodes + CC, determinístico."""

from __future__ import annotations

import networkx as nx


def find_critical(g: nx.DiGraph, cc_threshold: int = 15, top_percent: float = 0.01) -> list[dict]:
    nodes = []
    for n, d in g.nodes(data=True):
        if d.get("kind") not in ("function", "method", "class"):
            continue
        out_deg = g.out_degree(n)
        cc = d.get("cc", 1)
        nodes.append((n, d, out_deg, cc))

    if not nodes:
        return []

    # top 1% por out_degree = god node
    nodes.sort(key=lambda x: x[2], reverse=True)
    cutoff = max(1, int(len(nodes) * top_percent))
    god_set = {n for n, _, _, _ in nodes[:cutoff]}

    crit: list[dict] = []
    for n, d, out_deg, cc in nodes:
        reasons: list[str] = []
        if n in god_set and out_deg >= 5:
            reasons.append(f"god node top {top_percent*100:.0f}% (out_degree={out_deg})")
        if cc > cc_threshold:
            reasons.append(f"CC {cc} > {cc_threshold}")
        if reasons:
            crit.append(
                {
                    "qualified_name": n,
                    "file": d.get("file"),
                    "line": d.get("line"),
                    "cc": cc,
                    "out_degree": out_deg,
                    "reasons": reasons,
                    "severity": "high" if cc > 20 or out_deg > 20 else "medium",
                }
            )
    return crit
