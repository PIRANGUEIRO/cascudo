"""Jobs — fila async compatível com Upstash/RQ, fallback asyncio."""

from __future__ import annotations

import asyncio
import uuid
from fastapi import APIRouter

router = APIRouter()

_jobs: dict[str, dict] = {}


def create_job(snapshot_id: str) -> str:
    jid = f"job-{uuid.uuid4().hex[:6]}"
    _jobs[jid] = {"id": jid, "snapshot_id": snapshot_id, "status": "queued", "progress": 0}
    return jid


def update_job(jid: str, status: str, progress: int) -> None:
    if jid in _jobs:
        _jobs[jid].update(status=status, progress=progress)


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    if job_id not in _jobs:
        return {"error": "job não encontrado"}
    return _jobs[job_id]
