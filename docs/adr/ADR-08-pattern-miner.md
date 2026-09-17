# ADR-08 — Aprendizado determinístico via corpus (sem IA)

**Status:** Aceita 2026-09-16

**Decisão:** Miner extrai subgrafos 3-5 nós, canonicaliza sort(nodes)+sort(edges) → SHA256, UPSERT `patterns(count++)`, freq = `count/total`. Sem embedding, sem gradiente.

**Alternativas:** GNN/embedding neural — rejeitadas por custo GPU, alucinação, quebra auditabilidade.

**Consequência:** `GET /patterns` mostra `73% do corpus`, auditável via SQL `COUNT(*)`.
