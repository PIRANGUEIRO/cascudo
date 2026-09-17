"""Busca estrutural F15 — trigram + regex, 0 IA, sem embedding."""

from __future__ import annotations

import re
from collections import defaultdict

import networkx as nx


def trigram_index(g: nx.DiGraph) -> dict[str, set[str]]:
    idx: dict[str, set[str]] = defaultdict(set)
    for n, d in g.nodes(data=True):
        name = d.get("name", n.split(".")[-1]).lower()
        # trigrams do nome
        padded = f"  {name} "
        for i in range(len(padded) - 2):
            tri = padded[i : i + 3]
            idx[tri].add(n)
        # também indexa qualified_name
        qn = n.lower()
        padded_qn = f"  {qn} "
        for i in range(len(padded_qn) - 2):
            tri = padded_qn[i : i + 3]
            idx[tri].add(n)
    return idx


def search_symbols(g: nx.DiGraph, query: str, limit: int = 20) -> list[dict]:
    """Busca determinística: regex + trigram, sem IA."""
    q = query.strip().lower()
    if not q:
        return []

    # tenta regex primeiro
    try:
        pat = re.compile(query, re.IGNORECASE)
        regex_hits = [(n, d) for n, d in g.nodes(data=True) if pat.search(n) or pat.search(str(d.get("name", "")))]
        if regex_hits:
            # ranqueia por centralidade + match exato
            scored = []
            for n, d in regex_hits[:limit]:
                deg = g.degree(n)
                score = deg + (10 if q in n.lower() else 0)
                scored.append((score, {"id": n, **d, "score": score, "via": "regex"}))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [s for _, s in scored][:limit]
    except re.error:
        pass

    # fallback trigram
    idx = trigram_index(g)
    padded_q = f"  {q} "
    tris = [padded_q[i : i + 3] for i in range(len(padded_q) - 2)]
    candidates: dict[str, int] = defaultdict(int)
    for tri in tris:
        for nid in idx.get(tri, set()):
            candidates[nid] += 1
    # threshold: pelo menos 1 trigram em comum
    ranked = sorted(candidates.items(), key=lambda x: x[1], reverse=True)[:limit]
    out = []
    for nid, score in ranked:
        d = g.nodes[nid]
        out.append({"id": nid, **d, "score": score, "via": "trigram"})
    return out
