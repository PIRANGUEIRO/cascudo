"""GET /api/snapshots/* + /api/patterns — Sprint1 com workspace + corpus."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from cascudo_core.analyzers import build_flow, find_clusters, find_critical, find_cycles, find_dead, find_hotspots
from cascudo_core.diff import diff_graphs
from cascudo_core.patterns.miner import mine_patterns
from cascudo_core.search import search_symbols

from ..auth.jwt import get_workspace_id
from ..store import get_store

router = APIRouter()


@router.get("/snapshots/{snapshot_id}/flow")
async def flow(
    snapshot_id: str,
    workspace_id: str = Depends(get_workspace_id),
    depth: int = Query(default=6, ge=1, le=10),
    entrypoint: str | None = None,
) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, f"snapshot {snapshot_id} não encontrado")
    # workspace check (se snapshot não for do workspace, 404 para não vazar)
    meta = store._meta.get(snapshot_id, {})  # type: ignore
    if meta.get("workspace_id") and meta["workspace_id"] != workspace_id and workspace_id != "ws-demo":
        raise HTTPException(403, "snapshot pertence a outro workspace")
    return build_flow(g, depth=depth, entry=entrypoint)


@router.get("/snapshots/{snapshot_id}/dead")
async def dead(snapshot_id: str, workspace_id: str = Depends(get_workspace_id), confidence_min: str = Query(default="all")) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    return {"dead": find_dead(g, confidence=confidence_min), "workspace_id": workspace_id}


@router.get("/snapshots/{snapshot_id}/cycles")
async def cycles(snapshot_id: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    return {"cycles": find_cycles(g)}


@router.get("/snapshots/{snapshot_id}/critical")
async def critical(snapshot_id: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    return {"critical": find_critical(g)}


@router.get("/snapshots/{snapshot_id}/patterns")
async def patterns(snapshot_id: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    # tenta pegar do store (persistido), senão minera ao vivo
    stored = await store.get_patterns(snapshot_id)
    corpus, total = await store.get_corpus()  # type: ignore
    if not stored:
        pats = mine_patterns(g)
        stored = [{"hash": p.hash, "kind": p.kind, "canonical": p.canonical_repr} for p in pats]
    out = []
    for p in stored:
        cnt = corpus.get(p["hash"], {}).get("count", 1)
        freq = cnt / max(1, total)
        out.append({**p, "count": cnt, "frequency": round(freq, 3), "total_snapshots": total})
    out.sort(key=lambda x: x["frequency"], reverse=True)  # type: ignore
    return {"patterns": out, "total_snapshots": total, "workspace_id": workspace_id}


@router.get("/patterns")
async def global_patterns(
    workspace_id: str = Depends(get_workspace_id),
    kind: str | None = None,
    min_frequency: float = 0.0,
    limit: int = 20,
) -> dict:
    store = get_store()
    corpus, total = await store.get_corpus()  # type: ignore
    stats = await store.get_corpus_stats()
    items = []
    for h, v in corpus.items():
        freq = v["count"] / max(1, total)
        if kind and v["kind"] != kind:
            continue
        if freq < min_frequency:
            continue
        items.append({"hash": h, "kind": v["kind"], "canonical": v["canonical"], "count": v["count"], "frequency": round(freq, 3)})
    items.sort(key=lambda x: x["frequency"], reverse=True)  # type: ignore
    return {"patterns": items[:limit], "total_snapshots": total, "stats": stats, "workspace_id": workspace_id}


@router.get("/snapshots/{snapshot_id}/symbol/{qname:path}")
async def symbol_detail(snapshot_id: str, qname: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    if qname not in g:
        raise HTTPException(404, f"symbol {qname} não encontrado")
    data = g.nodes[qname]
    callers = [u for u, _, d in g.in_edges(qname, data=True) if d.get("kind") == "CALLS"]
    callees = [v for _, v, d in g.out_edges(qname, data=True) if d.get("kind") == "CALLS"]
    return {"symbol": {"qualified_name": qname, **data}, "callers": callers, "callees": callees, "snippet": f"// {data.get('file')}:{data.get('line')} — snippet via tree-sitter em V2"}


@router.get("/snapshots/{snapshot_id}/graph")
async def graph(snapshot_id: str, workspace_id: str = Depends(get_workspace_id), limit: int = 100, offset: int = 0) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    nodes = list(g.nodes(data=True))[offset : offset + limit]
    edges = list(g.edges(data=True))[offset : offset + limit]
    return {"nodes": [{"id": n, **d} for n, d in nodes], "edges": [{"source": u, "target": v, **d} for u, v, d in edges], "total": {"nodes": g.number_of_nodes(), "edges": g.number_of_edges()}}


@router.get("/snapshots/{snapshot_id}/clusters")
async def clusters_view(snapshot_id: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    return {"clusters": find_clusters(g), "count": len(find_clusters(g))}


@router.get("/snapshots/{snapshot_id}/hotspots")
async def hotspots_view(snapshot_id: str, workspace_id: str = Depends(get_workspace_id)) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    return {"hotspots": find_hotspots(g), "explain": "score=churn×CC, p90 vs mediana — sem IA, só git log + CC"}


@router.get("/snapshots/{snapshot_id}/search")
async def search_view(snapshot_id: str, q: str = "", workspace_id: str = Depends(get_workspace_id), limit: int = 20) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    hits = search_symbols(g, q, limit=limit)
    return {"query": q, "hits": hits, "count": len(hits), "via": "regex+trigram, 0 IA"}


@router.get("/snapshots/{snapshot_id}/export")
async def export_graph(
    snapshot_id: str, workspace_id: str = Depends(get_workspace_id), format: str = Query(default="dot", pattern="^(dot|mermaid|json|svg|md)$")
) -> dict:
    store = get_store()
    try:
        g = await store.load_graph(snapshot_id)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    if format == "dot":
        lines = ["digraph G {"]
        for u, v, d in g.edges(data=True):
            label = d.get("kind", "")
            lines.append(f'  "{u}" -> "{v}" [label="{label}"];')
        lines.append("}")
        return {"format": "dot", "content": "\n".join(lines)}
    if format == "mermaid":
        lines = ["graph TD"]
        for u, v, d in g.edges(data=True):
            uid = u.replace("/", "_").replace(".", "_").replace("-", "_").replace(":", "_")
            vid = v.replace("/", "_").replace(".", "_").replace("-", "_").replace(":", "_")
            lines.append(f"  {uid} -->|{d.get('kind','')}| {vid}")
        return {"format": "mermaid", "content": "\n".join(lines)}
    if format == "svg":
        # SVG minimalista determinístico (ELK no frontend gera SVG melhor; aqui stub auditável)
        w, h = 800, 600
        nodes = list(g.nodes())[:50]
        svg = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#0B0D10"/>']
        for i, n in enumerate(nodes):
            x, y = (i % 10) * 80 + 20, (i // 10) * 60 + 20
            color = "#8B5CF6" if g.nodes[n].get("is_entrypoint") else "#3B82F6"
            svg.append(f'<g><rect x="{x}" y="{y}" width="70" height="28" rx="6" fill="#181C21" stroke="{color}"/><text x="{x+35}" y="{y+17}" text-anchor="middle" fill="#F3F4F6" font-family="IBM Plex Mono" font-size="8">{n.split(".")[-1][:10]}</text></g>')
        svg.append("</svg>")
        return {"format": "svg", "content": "\n".join(svg)}
    if format == "md":
        dead = __import__("cascudo_core.analyzers", fromlist=["find_dead"]).find_dead(g)
        cycles = __import__("cascudo_core.analyzers", fromlist=["find_cycles"]).find_cycles(g)
        lines = [f"# Cascudo Report — {snapshot_id}", f"- Nodes: {g.number_of_nodes()} Edges: {g.number_of_edges()}", f"- Dead: {len(dead)}", f"- Cycles: {len(cycles)}", "", "## Dead", ""]
        for d in dead:
            lines.append(f"- `{d['qualified_name']}` {d['file']}:{d['line']} — {d['confidence']}")
        lines += ["", "## Cycles", ""]
        for c in cycles:
            lines.append(f"- {' → '.join(c)}")
        return {"format": "md", "content": "\n".join(lines)}
    return {"format": "json", "content": {"nodes": list(g.nodes(data=True)), "edges": list(g.edges(data=True))}}


@router.post("/snapshots/diff")
async def diff_snapshots(payload: dict, workspace_id: str = Depends(get_workspace_id)) -> dict:
    frm = payload.get("from")
    to = payload.get("to")
    if not frm or not to:
        raise HTTPException(400, "payload precisa de {from, to}")
    store = get_store()
    try:
        g1 = await store.load_graph(frm)
        g2 = await store.load_graph(to)
    except KeyError as e:
        raise HTTPException(404, f"snapshot não encontrado: {e}")
    diff = diff_graphs(g1, g2)
    return {"from": frm, "to": to, "diff": diff, "workspace_id": workspace_id}


@router.post("/ci")
async def ci_gate(payload: dict, workspace_id: str = Depends(get_workspace_id)) -> dict:
    sid = payload.get("snapshot_id")
    fail_on = payload.get("fail_on", [])  # ["cycle","dead","critical"]
    max_cc = payload.get("max_cc", 15)
    if not sid:
        raise HTTPException(400, "snapshot_id obrigatório")
    store = get_store()
    try:
        g = await store.load_graph(sid)
    except KeyError:
        raise HTTPException(404, "snapshot não encontrado")
    issues = {}
    passed = True
    report = []
    if "cycle" in fail_on:
        cycles = find_cycles(g)
        issues["cycles"] = cycles
        if cycles:
            passed = False
            report.append(f"FAIL cycle: {len(cycles)} ciclo(s) — A→B→A")
        else:
            report.append("PASS cycle")
    if "dead" in fail_on or "deadcode" in fail_on:
        dead = find_dead(g)
        issues["dead"] = dead
        if dead:
            passed = False
            report.append(f"FAIL dead: {len(dead)} poço(s) morto(s)")
        else:
            report.append("PASS dead")
    if "critical" in fail_on or max_cc:
        crit = find_critical(g, cc_threshold=max_cc)
        issues["critical"] = crit
        if crit:
            # só falha se high severity
            highs = [c for c in crit if c["severity"] == "high"]
            if highs:
                passed = False
                report.append(f"FAIL critical: CC>{max_cc} em {len(highs)} símbolo(s)")
            else:
                report.append(f"PASS critical (medium {len(crit)})")
        else:
            report.append("PASS critical")
    return {"passed": passed, "issues": issues, "report": "\n".join(report), "snapshot_id": sid, "workspace_id": workspace_id}


@router.get("/workspaces/{workspace_id}/snapshots")
async def list_snapshots(workspace_id: str, caller_ws: str = Depends(get_workspace_id)) -> dict:
    # só lista se caller == workspace ou ws-demo
    if workspace_id != caller_ws and caller_ws != "ws-demo":
        raise HTTPException(403, "acesso negado ao workspace")
    store = get_store()
    snaps = await store.list_snapshots(workspace_id)  # type: ignore
    return {"snapshots": snaps, "workspace_id": workspace_id}
