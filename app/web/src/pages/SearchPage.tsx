import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "@/shared/api/client";
import { Card } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

export function SearchPage() {
  const [params] = useSearchParams();
  const sid = params.get("snapshot") || "";
  const [q, setQ] = useState("oldHelper");
  const [hits, setHits] = useState<any[]>([]);
  const [via, setVia] = useState("");

  async function search() {
    if (!sid) return;
    const r = await api<{ hits: any[]; via: string }>(`/api/snapshots/${sid}/search?q=${encodeURIComponent(q)}`);
    setHits(r.hits);
    setVia(r.via);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h2 className="text-lg font-semibold">Busca Estrutural — F15</h2>
      <p className="mono text-xs text-text-muted">Regex + trigram, sem embedding. Ex: `validate.*payment` ou `oldHelper` — {via}</p>
      <div className="flex gap-2">
        <input value={sid} readOnly placeholder="snapshot id" className="mono flex-1 rounded border bg-surface-2 px-3 py-2 text-sm" />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="query regex/trigram" className="flex-1 rounded border bg-surface-2 px-3 py-2 text-sm" />
        <button onClick={search} className="rounded bg-automation px-4 py-2 text-sm text-white">Buscar</button>
      </div>
      {!sid && <Card><div className="mono text-xs text-text-muted">Cole <span className="text-intelligence">?snapshot=snap-xxx</span> na URL após upload.</div></Card>}
      {hits.map((h: any) => (
        <Card key={h.id} className="flex items-center justify-between">
          <div>
            <div className="font-mono text-sm">{h.id}</div>
            <div className="mono text-xs text-text-secondary">{h.file}:{h.line} · {h.kind} · via {h.via} · score {h.score}</div>
          </div>
          <Badge variant="flow">{h.kind}</Badge>
        </Card>
      ))}
    </div>
  );
}
