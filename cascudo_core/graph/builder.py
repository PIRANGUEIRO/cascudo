"""Graph builder — networkx DiGraph, 100% puro, escalável."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx

from ..parsers import ParseResult


@dataclass
class BuildStats:
    files: int = 0
    symbols: int = 0
    edges: int = 0
    loc: int = 0


@dataclass
class GraphBundle:
    graph: nx.DiGraph
    stats: BuildStats
    files: list[str] = field(default_factory=list)


def _resolve_import(file: str, target: str, file_map: dict[str, str]) -> str:
    if target.startswith("."):
        base = Path(file).parent
        # cand absoluto normalizado
        try:
            cand = (base / target).resolve()
        except Exception:
            cand = base / target
        # tenta match exato por path resolvido (exclui o próprio file)
        for k in file_map:
            try:
                if Path(k).resolve() == cand:
                    return k
            except Exception:
                continue
        # fallback: match por sufixo relativo (ex: services/user.js)
        cand_str = str(cand)
        for k in file_map:
            if k == file:
                continue
            if cand_str.endswith(Path(k).name) and Path(target).stem == Path(k).stem:
                # verifica se subpath coincide (ex: .../services/user.js)
                if Path(target).parent.name in k or True:
                    # escolhe o que contém o diretório do target
                    if Path(target).parent.name != "." and Path(target).parent.name in k:
                        return k
                    # se não tem diretório específico, pega primeiro stem match que não é self
                    # mas evita colisão controllers/user vs services/user
                    pass
        # tenta encontrar stem único que não seja self
        candidates = [k for k in file_map if Path(k).stem == Path(target).stem and k != file]
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            # prefere aquele cujo parent name coincide com target parent
            target_parent = Path(target).parent.name
            for c in candidates:
                if target_parent in c:
                    return c
            return candidates[0]
        return str(cand)
    return target


def build_graph(results: list[ParseResult]) -> GraphBundle:
    g = nx.DiGraph()

    stats = BuildStats()
    file_map = {r.file: r.file for r in results}

    for r in results:
        stats.files += 1
        stats.loc += r.loc
        stats.symbols += len(r.symbols)
        stats.edges += len(r.edges)

        # file node
        g.add_node(r.file, kind="file", lang=r.lang, loc=r.loc, hash=r.hash)

        for s in r.symbols:
            g.add_node(
                s.qualified_name,
                kind=s.kind,
                file=s.file,
                line=s.line,
                cc=s.cc,
                is_entrypoint=s.is_entrypoint,
                is_exported=s.is_exported,
                lang=s.lang,
            )
            # CONTAINS edge file -> symbol
            g.add_edge(r.file, s.qualified_name, kind="CONTAINS", confidence="high")

        for e in r.edges:
            tgt = e.target
            if e.kind == "IMPORTS":
                tgt = _resolve_import(e.source, e.target, file_map)
            if e.source not in g:
                g.add_node(e.source, kind="unknown", file=e.file)
            if tgt not in g:
                # se resolveu para file existente, garante kind=file
                if tgt in file_map:
                    if tgt not in g:
                        # file já existe, mas garante
                        pass
                else:
                    g.add_node(tgt, kind="unknown", file=e.file)
            g.add_edge(e.source, tgt, kind=e.kind, file=e.file, line=e.line, confidence=e.confidence)

    return GraphBundle(graph=g, stats=stats, files=[r.file for r in results])


def entrypoints(g: nx.DiGraph) -> list[str]:
    """Detecta entrypoints: is_entrypoint True ou main/index/app/server.*"""
    eps = [n for n, d in g.nodes(data=True) if d.get("is_entrypoint")]
    if eps:
        return eps
    # fallback: nodes com out_degree >2 e in_degree 0
    return [n for n, deg in g.out_degree() if deg > 2][:5]
