import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "@/shared/api/client";
import { Card } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

export function HotspotsPage() {
  const [params] = useSearchParams();
  const sid = params.get("snapshot");
  const [hot, setHot] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!sid) return;
    api<{ hotspots: any[] }>(`/api/snapshots/${sid}/hotspots`).then((r) => setHot(r.hotspots)).catch((e) => setErr(String(e)));
  }, [sid]);

  if (!sid) return <div className="space-y-3"><h2 className="text-lg font-semibold">Hotspots vs Corpus — F14</h2><Card><p className="mono text-xs text-text-muted">Acesse <span className="text-intelligence">/hotspots?snapshot=&lt;id&gt;</span> — score = churn × CC, p90 vs mediana, sem IA.</p></Card></div>;
  if (err) return <div className="font-mono text-danger">{err}</div>;

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Hotspots — {sid} <span className="mono text-xs font-normal text-text-muted">· p90 roxo pulsante se churn+CC acima do corpus</span></h2>
      {!hot.length ? <Card><div className="mono text-xs text-text-muted">Nenhum hotspot acima do p90 — código saudável. p90 = score do top 10%.</div></Card> : hot.map((h: any) => (
        <Card key={h.id} className="flex items-center justify-between border-intelligence/30 bg-intelligence/5">
          <div>
            <div className="font-mono text-sm font-medium">{h.id}</div>
            <div className="mono text-xs text-text-secondary">{h.file}:{h.line} · CC {h.cc} · churn {h.churn} · score {h.score} (p90 {h.p90})</div>
          </div>
          <Badge variant="pattern">{h.severity.toUpperCase()}</Badge>
        </Card>
      ))}
    </div>
  );
}
