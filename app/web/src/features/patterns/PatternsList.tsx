import { useEffect, useState } from "react";
import { snapshotsApi } from "@/shared/api/client";
import { Card, CardHeader } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

type Pat = { hash: string; kind: string; canonical: string; count: number; frequency: number };

export function PatternsList({ snapshotId }: { snapshotId?: string }) {
  const [patterns, setPatterns] = useState<Pat[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const p = snapshotId ? snapshotsApi.patterns(snapshotId) : snapshotsApi.globalPatterns({ limit: 20 });
    p.then((res) => {
      // @ts-ignore
      setPatterns(res.patterns);
      // @ts-ignore
      setTotal(res.total_snapshots ?? res.stats?.total_snapshots ?? 0);
    }).finally(() => setLoading(false));
  }, [snapshotId]);

  if (loading) return <div className="mono text-xs text-text-muted">Carregando padrões (COUNT(*) determinístico)…</div>;

  if (!patterns.length) return <div className="mono text-xs text-text-muted">Nenhum padrão — faça upload com --contribute para alimentar corpus.</div>;

  return (
    <div className="space-y-3">
      <div className="mono text-[11px] text-text-muted">CORPUS {total} snapshots · {patterns.length} padrões únicos · auditável via SQL</div>
      {patterns.map((p) => (
        <Card key={p.hash} className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="pattern">{p.kind}</Badge>
              <span className="mono text-xs text-text-muted">{p.hash.slice(0, 8)}</span>
            </div>
            <div className="mt-1 font-mono text-sm font-medium">{p.canonical}</div>
            <div className="mono text-[11px] text-text-secondary">hash {p.hash} · count {p.count}/{total}</div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-intelligence">{(p.frequency * 100).toFixed(1)}%</div>
            <div className="mono text-[11px] text-text-muted">freq no corpus</div>
          </div>
        </Card>
      ))}
    </div>
  );
}
