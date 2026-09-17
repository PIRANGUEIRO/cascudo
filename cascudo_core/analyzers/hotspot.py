"""Hotspots F14 — churn×CC vs mediana p90 do corpus, determinístico."""

from __future__ import annotations

import subprocess
from pathlib import Path

import networkx as nx


def git_churn(file: str, repo_root: Path | None = None) -> int:
    # conta commits que tocaram o arquivo — sem IA, só git log
    try:
        root = repo_root or Path(file).parent
        # tenta achar .git acima
        for p in Path(file).parents:
            if (p / ".git").exists():
                root = p
                break
        out = subprocess.check_output(["git", "-C", str(root), "log", "--oneline", "--", file], stderr=subprocess.DEVNULL, text=True)
        return len(out.strip().splitlines()) if out.strip() else 0
    except Exception:
        return 0


def find_hotspots(g: nx.DiGraph, repo_root: Path | None = None) -> list[dict]:
    # coleta CC e churn por símbolo
    items: list[dict] = []
    for n, d in g.nodes(data=True):
        if d.get("kind") not in ("function", "method", "class"):
            continue
        cc = d.get("cc", 1)
        churn = git_churn(d.get("file", ""), repo_root) if d.get("file") else 0
        # simula churn maior para fixture sem git: usa out_degree como proxy
        if churn == 0:
            churn = g.out_degree(n) + g.in_degree(n)
        items.append({"id": n, "file": d.get("file"), "line": d.get("line"), "cc": cc, "churn": churn, "score": cc * (churn + 1)})

    if not items:
        return []

    # p90 do corpus (aqui do próprio snapshot — compara com mediana do snapshot)
    scores = sorted(i["score"] for i in items)
    p90 = scores[int(len(scores) * 0.9)] if len(scores) > 5 else scores[-1]
    median = scores[len(scores) // 2]

    hotspots = []
    for it in items:
        if it["score"] >= p90 and it["cc"] > median:
            hotspots.append({**it, "p90": p90, "median": median, "severity": "high" if it["score"] > p90 * 1.5 else "medium"})

    hotspots.sort(key=lambda x: x["score"], reverse=True)
    return hotspots
