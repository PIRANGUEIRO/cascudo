import { useState } from "react";
import { UploadDrop } from "@/features/upload/UploadDrop";
import { PushResponse } from "@/shared/api/client";
import { Card, CardHeader } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

export function UploadPage() {
  const [last, setLast] = useState<PushResponse | null>(null);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Cascudo — Mapa Mental do Código</h1>
        <p className="mt-1 text-sm text-text-secondary">Fluxograma + poços mortos + padrões · 0 IA · auditável · Codespaces 0GB</p>
        <div className="mono mt-2 flex gap-2 text-[11px] text-text-muted">
          <span>SNAPSHOT v0.1</span> · <span>DETERMINÍSTICO</span> · <span>COUNT(*)</span>
        </div>
      </div>

      <UploadDrop onPushed={setLast} />

      {last && (
        <Card>
          <CardHeader title="Snapshot criado" subtitle={last.snapshot_id} action={<Badge variant="pattern">{last.patterns.found} padrões</Badge>} />
          <div className="grid grid-cols-4 gap-3">
            <div className="rounded-md bg-surface-2 p-3">
              <div className="label">ARQUIVOS</div>
              <div className="text-xl font-bold">{last.stats.files}</div>
            </div>
            <div className="rounded-md bg-surface-2 p-3">
              <div className="label">SÍMBOLOS</div>
              <div className="text-xl font-bold">{last.stats.symbols}</div>
            </div>
            <div className="rounded-md bg-surface-2 p-3">
              <div className="label">ARESTAS</div>
              <div className="text-xl font-bold">{last.stats.edges}</div>
            </div>
            <div className="rounded-md bg-surface-2 p-3">
              <div className="label">ISSUES</div>
              <div className="mono text-sm">dead {last.issues.dead} · cycles {last.issues.cycles} · crit {last.issues.critical}</div>
            </div>
          </div>
          <div className="mono mt-3 text-xs text-text-muted">Snapshot ID: {last.snapshot_id} — use em /flow?snapshot={last.snapshot_id}</div>
        </Card>
      )}

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <div className="label">INVESTIGAÇÃO</div>
          <div className="mt-1 text-sm font-medium">SEARCH → EVIDENCE → CONCLUSION → ACTION</div>
          <p className="mt-1 text-xs text-text-secondary">Cada issue mostra regra exata: `in_degree==0`, `SCC`, `CC&gt;15`.</p>
        </Card>
        <Card>
          <div className="label">PADRÕES</div>
          <div className="mt-1 text-sm font-medium">Controller→Service aparece em 73% do corpus</div>
          <p className="mt-1 text-xs text-text-secondary">Hash canônico + COUNT, sem embedding.</p>
        </Card>
        <Card>
          <div className="label">ESCALA</div>
          <div className="mt-1 text-sm font-medium">Core puro + API fina + FSD</div>
          <p className="mt-1 text-xs text-text-secondary">Add linguagem = 1 parser + 1 registro. Add tela = 1 feature.</p>
        </Card>
      </div>
    </div>
  );
}
