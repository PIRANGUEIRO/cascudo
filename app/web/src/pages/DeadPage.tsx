import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { snapshotsApi } from "@/shared/api/client";
import { Card } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

export function DeadPage() {
  const [params] = useSearchParams();
  const sid = params.get("snapshot");
  const [dead, setDead] = useState<Array<{ qualified_name: string; file: string; line: number; confidence: string; reason: string }>>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!sid) return;
    snapshotsApi.dead(sid).then((r) => setDead(r.dead as any)).catch((e) => setErr(String(e)));
  }, [sid]);

  if (!sid) {
    return (
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Poços Mortos</h2>
        <Card>
          <p className="mono text-xs text-text-muted">Faça upload e acesse <span className="text-intelligence">/dead?snapshot=&lt;id&gt;</span></p>
          <p className="mt-2 text-sm text-text-secondary">Todo dead mostra prova: <span className="mono">in_degree==0 (CALLS)</span> + confiança high/medium/low. Exportado = low (suspect).</p>
        </Card>
      </div>
    );
  }

  if (err) return <div className="font-mono text-danger">{err}</div>;

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Poços Mortos — {sid}</h2>
      <div className="mono text-xs text-text-muted">{dead.length} candidatos · threshold in_degree==0 · 0 IA</div>
      {dead.map((d) => (
        <Card key={d.qualified_name} className="flex items-center justify-between">
          <div>
            <div className="font-mono text-sm font-medium">{d.qualified_name}</div>
            <div className="mono text-xs text-text-secondary">{d.file}:{d.line} · {d.reason}</div>
          </div>
          <Badge variant="dead">{d.confidence.toUpperCase()}</Badge>
        </Card>
      ))}
      {!dead.length && <div className="mono text-xs text-text-muted">Nenhum morto — ou já limpo.</div>}
    </div>
  );
}
