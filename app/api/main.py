"""FastAPI entry — thin, escalável, 0 IA."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import jobs, push, snapshots

app = FastAPI(
    title="Cascudo API",
    version="0.1.0",
    description="Mapa mental 0 IA — fluxograma + dead/cycle + padrões determinísticos (Sprint1: fila + padrões + workspace)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(push.router, prefix="/api", tags=["push"])
app.include_router(snapshots.router, prefix="/api", tags=["snapshots"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "0.1.0", "ia": "0"}


@app.get("/")
async def root() -> dict:
    return {"name": "Cascudo", "docs": "/docs", "health": "/health"}
