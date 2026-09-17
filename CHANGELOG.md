# Changelog — Cascudo

## 0.1.0 — 2026-09-17 — MVP 0 IA completo (Sprint 0-3 + polish)

- **Core:** walker + parsers JS/TS, Python, Go, Rust, Java, C/C++ (tree-sitter regex, estratégia escalável)
- **Graph:** networkx DiGraph + SCC + BFS flow depth 6 + Louvain clustering (hairball mitigation)
- **Analyzers:** dead `in_degree==0`, cycles SCC, critical CC>15 + top 1% out_degree, hotspots churn×CC p90, conflict (import quebrado)
- **Patterns:** miner 3-5 nós hash canônico SHA256 + COUNT(*) + frequência vs corpus (0 IA) + `/patterns` global
- **API:** FastAPI `/api/push?contribute&ephemeral&sync`, `/flow`, `/dead`, `/cycles`, `/critical`, `/patterns`, `/clusters`, `/hotspots`, `/search` (trigram+regex), `/export` (dot/mermaid/svg/md), `/ci` gate, `/snapshots/diff`, fila async BackgroundTasks (Upstash compat), workspace multi-tenant (X-Workspace-Id/JWT)
- **Web:** React 18 + Vite 6 + Tailwind 4 + ReactFlow + ELK hierárquico, Shell SaaS Mateboard (Inter + Plex Mono, grafite, cor=semântica), FSD escalável, Upload drag-drop, Flow com Drawer (callers/callees + badge 73%), Grafo com filtros + Louvain, Dead/Patterns/Diff/Hotspots/Search/Export
- **CLI:** Go cobra `cascudo push` + `cascudo ci --fail-on` + `cascudo patterns`
- **Infra:** Codespaces 0GB devcontainer (Python 3.12 + Node 20 + Go 1.22 + sshd), Postgres Neon, Redis Upstash, R2, Vercel + Fly/Render free, Dockerfile, GH Actions CI (ruff→pytest→0 IA check) + Deploy (docker build)
- **Testes:** 7 pytest (graph, miner, diff, export/ci, langs 6, hotspot/search, perf 500/10k) + Playwright stub
- **Docs:** 0 IA invariante (ADR-07), aprendizado determinístico (ADR-08), 0GB (ADR-09)
