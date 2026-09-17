"""POST /api/push — Sprint1: fila async + ephemeral + workspace + corpus."""

from __future__ import annotations

import asyncio
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse

from cascudo_core.analyzers import find_critical, find_cycles, find_dead
from cascudo_core.graph.builder import build_graph
from cascudo_core.patterns.miner import mine_patterns
from cascudo_core.walker import parse_zip

from ..auth.jwt import get_workspace_id
from ..store import get_store
from .jobs import create_job, update_job

router = APIRouter()


async def _index_job(snapshot_id: str, workspace_id: str, zip_bytes: bytes, contribute: bool, ephemeral: bool, job_id: str) -> None:
    t0 = time.time()
    update_job(job_id, "indexing", 30)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "upload.zip"
        zip_path.write_bytes(zip_bytes)
        extract_to = tmp_path / "extracted"
        extract_to.mkdir()
        results = parse_zip(zip_path, extract_to)
        if not results:
            update_job(job_id, "failed", 100)
            return
        bundle = build_graph(results)
        g = bundle.graph
        dead = find_dead(g)
        cycles = find_cycles(g)
        critical = find_critical(g)
        patterns = mine_patterns(g)

        store = get_store()
        # persiste snapshot com workspace
        await store.save_snapshot(
            snapshot_id,
            workspace_id,
            g,
            {
                "stats": {
                    "files": bundle.stats.files,
                    "symbols": bundle.stats.symbols,
                    "edges": bundle.stats.edges,
                    "loc": bundle.stats.loc,
                    "duration_ms": int((time.time() - t0) * 1000),
                },
                "dead": len(dead),
                "cycles": len(cycles),
                "critical": len(critical),
                "patterns": len(patterns),
                "ephemeral": ephemeral,
            },
        )
        # corpus — só se contribute True
        if contribute:
            await store.save_patterns(
                snapshot_id, [{"hash": p.hash, "kind": p.kind, "canonical": p.canonical_repr} for p in patterns]
            )
        else:
            # ainda salva patterns do snapshot, mas sem incrementar corpus global
            store._patterns[snapshot_id] = [{"hash": p.hash, "kind": p.kind, "canonical": p.canonical_repr} for p in patterns]  # type: ignore
            # corpus não incrementa

        update_job(job_id, "ready", 100)

        # TTL ephemeral: se ephemeral True, agenda GC em 1h (R2 free)
        if ephemeral:
            # em prod: R2 delete + DB TTL; aqui só log
            pass


@router.post("/push")
async def push(
    background_tasks: BackgroundTasks,
    workspace_id: str = Depends(get_workspace_id),
    file: UploadFile | None = File(default=None),
    git_url: str | None = Query(default=None),
    contribute: bool = Query(default=False),
    ephemeral: bool = Query(default=True),
    sync: bool = Query(default=True, description="sync=true para protótipo (retorna pronto); false = fila async"),
) -> JSONResponse:
    snapshot_id = f"snap-{uuid.uuid4().hex[:8]}"
    job_id = create_job(snapshot_id)

    if file is not None:
        content = await file.read()
        if len(content) > 100 * 1024 * 1024:
            return JSONResponse({"error": "zip >100MB"}, status_code=413)
        # valida zip
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                z.testzip()
        except zipfile.BadZipFile:
            return JSONResponse({"error": "zip inválido"}, status_code=400)

        if sync:
            # Sprint0 compat: indexa inline (Codespaces preview rápido)
            await _index_job(snapshot_id, workspace_id, content, contribute, ephemeral, job_id)
            store = get_store()
            meta = store._meta.get(snapshot_id, {})  # type: ignore
            stats = meta.get("stats", {})  # type: ignore
            patterns = await store.get_patterns(snapshot_id)
            corpus, total = await store.get_corpus()  # type: ignore
            top = []
            for p in patterns[:3]:
                cnt = corpus.get(p["hash"], {}).get("count", 1)
                freq = cnt / max(1, total)
                top.append({**p, "count": cnt, "frequency": round(freq, 3)})

            return JSONResponse(
                {
                    "snapshot_id": snapshot_id,
                    "job_id": job_id,
                    "status": "ready",
                    "workspace_id": workspace_id,
                    "stats": stats,
                    "issues": {"dead": meta.get("dead"), "cycles": meta.get("cycles"), "critical": meta.get("critical")},
                    "patterns": {"found": len(patterns), "top": top},
                    "ephemeral": ephemeral,
                    "contribute": contribute,
                },
                status_code=201,
            )
        else:
            # Sprint1 async: enfileira (Upstash/RQ em prod, BackgroundTasks aqui)
            background_tasks.add_task(_index_job, snapshot_id, workspace_id, content, contribute, ephemeral, job_id)
            return JSONResponse(
                {"snapshot_id": snapshot_id, "job_id": job_id, "status": "queued", "workspace_id": workspace_id}, status_code=202
            )

    if git_url:
        return JSONResponse({"error": "git_url em Sprint2, use zip"}, status_code=501)
    return JSONResponse({"error": "envie file ou git_url"}, status_code=400)


# compat para snapshots router
import io  # noqa: E402
