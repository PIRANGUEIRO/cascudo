# ADR-07 — 0 IA (determinístico)

**Status:** Aceita 2026-09-16
**Decisão:** Cascudo nunca usa LLM/embedding neural. Todo diagnóstico é regra explícita auditável.

Alternativas: usar LLM/embedding para busca semântica e classificação.
Rejeitada: alucinação, custo GPU, quebra R$0, quebra auditabilidade.

Consequência: busca é trigram/regex, miner é hash+COUNT, todo PR passa `grep -r openai|llm` fail.
