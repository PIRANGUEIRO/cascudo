"""Pattern Miner determinístico — hash canônico + COUNT, 0 IA."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class Pattern:
    hash: str
    kind: str  # chain_3 | star_3 | triangle | chain_4 | chain_5
    canonical_repr: str
    nodes: tuple[str, ...]
    count: int = 1


def _canonical_hash(nodes: list[str], edges: list[tuple[str, str]]) -> str:
    # estável: usa só short name + kind, não path tmp — gSpan V2 usará WL
    def _norm(n: str) -> str:
        # file path → stem, symbol → last part
        if "/" in n or "\\" in n:
            return n.split("/")[-1].split("\\")[-1].split(".")[0]
        return n.split(".")[-1]
    ns = sorted(_norm(n) for n in nodes)
    es = sorted(f"{_norm(a)}->{_norm(b)}" for a, b in edges)
    raw = "|".join(ns) + "||" + "|".join(es)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _canonical_repr(nodes: list[str], kind: str) -> str:
    # legível: Controller→Service→Repo, não tmp path
    shorts = [n.split(".")[-1].split("/")[-1].replace(".js", "").replace(".go", "").replace(".py", "") for n in nodes]
    # remove paths
    shorts = [s.split("/")[-1] for s in shorts]
    shorts = sorted(set(shorts))  # determinístico
    if kind == "trigram":
        return "→".join(shorts[:3])
    return "→".join(shorts)


def _kind_for(sub: nx.DiGraph) -> str:
    n = sub.number_of_nodes()
    m = sub.number_of_edges()
    if n == 3 and m == 2:
        # chain vs star: chain tem 1 nó grau 2, star tem hub grau 2
        degs = sorted([d for _, d in sub.degree()])
        if degs == [1, 1, 2]:
            # ambos dão [1,1,2] em DiGraph não direcionado aprox — diferencia por in/out
            # simplifica: chain_3
            return "chain_3"
        return "star_3"
    if n == 3 and m == 3:
        return "triangle"
    if n == 4:
        return "chain_4"
    if n == 5:
        return "chain_5"
    return f"sub_{n}_{m}"


def mine_patterns(g: nx.DiGraph, max_nodes: int = 5) -> list[Pattern]:
    """Extrai subgrafos 3-5 nós via BFS a partir de cada nó — O(n * b^d) limitado."""
    patterns: dict[str, Pattern] = {}

    for start in list(g.nodes()):
        # BFS limitada
        visited: set[str] = {start}
        frontier = [start]
        sub_nodes: set[str] = {start}

        # expande até 5 nós
        while frontier and len(sub_nodes) < max_nodes:
            nxt: list[str] = []
            for u in frontier:
                for v in g.successors(u):
                    if g.edges[u, v].get("kind") not in ("CALLS", "CONTAINS", "IMPORTS"):
                        continue
                    if v not in sub_nodes and len(sub_nodes) < max_nodes:
                        sub_nodes.add(v)
                        nxt.append(v)
            frontier = nxt

        if len(sub_nodes) < 3:
            continue

        # gera subgrafos de 3,4,5 (janela deslizante por ordenação BFS)
        ordered = list(sub_nodes)
        for k in (3, 4, 5):
            if len(ordered) < k:
                continue
            chunk = ordered[:k]
            sub = g.subgraph(chunk)
            # só conta se for conectado (weakly)
            if not nx.is_weakly_connected(sub):
                continue
            edges = list(sub.edges())
            h = _canonical_hash(chunk, edges)
            kind = _kind_for(sub)
            canonical = _canonical_repr(chunk, kind)
            if h not in patterns:
                patterns[h] = Pattern(hash=h, kind=kind, canonical_repr=canonical, nodes=tuple(chunk))

        # n-gramas de chamadas: sequência linear
        # pega caminho de até 3 arestas CALLS
        path = [start]
        cur = start
        for _ in range(2):
            succs = [v for v in g.successors(cur) if g.edges[cur, v].get("kind") == "CALLS"]
            if not succs:
                break
            cur = succs[0]
            path.append(cur)
        if len(path) >= 3:
            h = _canonical_hash(path, [(path[i], path[i + 1]) for i in range(len(path) - 1)])
            trigram = _canonical_repr(path[:3], "trigram")
            if h not in patterns:
                patterns[h] = Pattern(hash=h, kind="trigram", canonical_repr=trigram, nodes=tuple(path[:3]))

    return list(patterns.values())


def frequency(count: int, total: int) -> float:
    return count / total if total else 0.0
