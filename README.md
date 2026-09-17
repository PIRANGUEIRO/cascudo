# Cascudo — Mapa Mental do Código (0 IA)

> **Peixe Cascudo limpa-fundo:** varre qualquer repo e mostra fluxograma lógico + pontos críticos + poços mortos + padrões do corpus — **100% determinístico, 0 IA, auditável via SQL.**

## Stack

- **Core:** Python 3.12 + `tree-sitter` + `networkx` (SCC, BFS, centrality)
- **API:** FastAPI + Uvicorn + Postgres (Neon/Supabase) + Redis (Upstash)
- **Web:** React 18 + Vite 6 + TypeScript 5 + Tailwind 4 + React Flow + ELK
- **CLI:** Go 1.22 `cobra` → `POST /push`
- **Design:** Mateboard Design System — `Inter + IBM Plex Mono`, tokens grafite, `cor = semântica`
- **Deploy:** Codespaces-only 0GB — Vercel (web) + Render/Fly (API) + Neon + R2 — `R$0/mês`

## Estrutura escalável

```
cascudo/
├── .devcontainer/          # Codespaces 1-click 0GB
├── cascudo_core/           # lib pura — sem I/O, 100% testável
│   ├── parsers/            # tree-sitter por linguagem (strategy pattern)
│   ├── graph/              # builder + store (networkx)
│   ├── analyzers/          # flow, dead, cycle, critical, conflict
│   └── patterns/           # miner determinístico (hash + COUNT)
├── app/
│   ├── api/                # FastAPI — thin controllers → service → core
│   └── web/                # React FSD — app/pages/widgets/features/entities/shared
├── cli/                    # Go — só POST /push
├── fixtures/               # js-todo, corpus-mini (oráculos)
└── tests/                  # pytest + playwright
```

**Princípios de escala:**
- `cascudo_core` é lib pura (sem FastAPI/DB) → reuso em worker, CLI local futuro, testes sem mock
- `app/api` é borda fina → valida input, enfileira, persiste, delega ao core
- `app/web` é FSD (Feature-Sliced Design) → cada feature é vertical fechada, escalável a 100 telas
- Design tokens centralizados → troca `dark/light/high_contrast` sem quebrar layout

## Quickstart (Codespaces 0GB)

```bash
# 1. Criar Codespace no GitHub → Code → Codespaces → Create
# 2. Dentro do Codespace (browser):
alembic upgrade head
pip install -e .[dev]
pnpm --prefix app/web install
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload &
pnpm --prefix app/web dev --host 0.0.0.0
# 3. Smoke:
curl -F file=@fixtures/js-todo.zip http://localhost:8000/api/push | jq .
```

Local com Docker apenas dentro do Codespaces (nunca no HD):
```bash
# Sem docker compose no PC. Se precisar Postgres efêmero no Codespaces:
docker compose -f .devcontainer/compose.yml up -d
```

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/push` | upload zip/git → snapshot + job |
| GET | `/api/jobs/:id` | polling progresso |
| GET | `/api/snapshots/:id/flow` | fluxograma BFS depth 6 |
| GET | `/api/snapshots/:id/dead` | dead code `in_degree==0` |
| GET | `/api/snapshots/:id/cycles` | SCC |
| GET | `/api/snapshots/:id/patterns` | padrões vs corpus |
| GET | `/api/snapshots/:id/symbol/:qname` | drill-down |

## Design System

Tokens em `app/web/src/shared/styles/tokens.css` — Mateboard:

- **Tipografia:** Inter (humano) + IBM Plex Mono (técnico)
- **Superfícies:** `#0B0D10` → `#111418` → `#181C21` → `#20252B`
- **Semântica:** `AUTOMATION #3B82F6` (ação), `INTELLIGENCE #8B5CF6` (insight), `SYSTEM #06B6D4` (infra)
- **Shell:** SaaS (Sidebar + Topbar + Content) → Workspace quando canvas domina
- **Composição:** Split (lista+detalhe) para dead/patterns, Canvas para grafo, Grid para KPIs
- **Densidade:** Analyst (L2-L3) — filtros + tabela + drill-down

Ver `9- Design/0-SISTEMA/09 VISUAL SYSTEM.md` no vault.

## 0 IA

Nenhum `openai`/`llm` no diff — CI `0-IA-check` falha se encontrar. Todo diagnóstico explica `CC>15`, `in_degree==0`, `SCC`, `COUNT(*)`.

## Licença

A definir.
