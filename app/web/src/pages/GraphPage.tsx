import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { snapshotsApi, api } from "@/shared/api/client";
import { Card } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";

export function GraphPage() {
  const [params] = useSearchParams();
  const sid = params.get("snapshot");
  const [graph, setGraph] = useState<{ nodes: any[]; edges: any[]; total: any } | null>(null);
  const [clusters, setClusters] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [kind, setKind] = useState("all");
  const [exportFmt, setExportFmt] = useState("dot");
  const [exportContent, setExportContent] = useState<string | null>(null);

  useEffect(() => {
    if (!sid) return;
    snapshotsApi.patterns(sid).catch(() => {}); // warm corpus
    api<{ nodes: any[]; edges: any[]; total: any }>(`/api/snapshots/${sid}/graph?limit=500`).then(setGraph);
    api<{ clusters: any[] }>(`/api/snapshots/${sid}/clusters`).then((r) => setClusters(r.clusters));
  }, [sid]);

  if (!sid) {
    return (
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Grafo Total</h2>
        <Card>
          <p className="mono text-xs text-text-muted">Acesse <span className="text-intelligence">/graph?snapshot=&lt;id&gt;</span> após upload. Suporta 500 nodes com Louvain + paginação + filtros.</p>
        </Card>
      </div>
    );
  }

  if (!graph) return <div className="mono text-sm text-text-muted">Carregando grafo {sid}…</div>;

  const filteredNodes = graph.nodes.filter((n: any) => {
    if (kind !== "all" && n.kind !== kind) return false;
    if (filter && !JSON.stringify(n).toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Grafo Total — {sid} <span className="mono text-xs font-normal text-text-muted">· {graph.total.nodes} nodes · {clusters.length} clusters Louvain</span></h2>
        <div className="flex gap-2">
          <select value={kind} onChange={(e) => setKind(e.target.value)} className="rounded border bg-surface-2 px-2 py-1 text-sm">
            <option value="all">todos kinds</option>
            <option value="function">function</option>
            <option value="file">file</option>
            <option value="class">class</option>
          </select>
          <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="buscar (nome/file/lang)" className="rounded border bg-surface-2 px-3 py-1 text-sm" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <Card className="col-span-1">
          <div className="label">CLUSTERS — Louvain (hairball mitigation)</div>
          <div className="mt-2 space-y-2">
            {clusters.map((c: any) => (
              <div key={c.id} className="rounded bg-surface-2 p-2">
                <div className="text-xs font-medium">{c.label}</div>
                <div className="mono text-[11px] text-text-muted">densidade {c.density} · {c.nodes.slice(0, 3).join(", ")}</div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="col-span-3">
          <div className="label">NODES FILTRADOS — paginação 500 · colapso por módulo em V2</div>
          <div className="mt-2 max-h-[420px] overflow-auto rounded border bg-background p-2">
            <table className="w-full text-left">
              <thead className="mono sticky top-0 bg-background text-[11px] text-text-muted">
                <tr>
                  <th className="p-1">ID</th>
                  <th className="p-1">KIND</th>
                  <th className="p-1">FILE</th>
                </tr>
              </thead>
              <tbody>
                {filteredNodes.slice(0, 100).map((n: any) => (
                  <tr key={n.id} className="border-t font-mono text-xs hover:bg-surface-2">
                    <td className="p-1">{n.id}</td>
                    <td className="p-1"><Badge variant={n.kind === "function" ? "flow" : "pattern"}>{n.kind}</Badge></td>
                    <td className="p-1 text-text-secondary">{n.file?.split("/").pop()}:{n.line ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mono mt-2 text-xs text-text-muted">{filteredNodes.length}/{graph.total.nodes} após filtros · mostrando 100</div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="label">EXPORT — SVG/PNG/DOT/Mermaid (Sprint3 completa)</div>
        <div className="mt-2 flex gap-2">
          <select value={exportFmt} onChange={(e) => setExportFmt(e.target.value)} className="rounded border bg-surface-2 px-2 py-1 text-sm">
            <option value="dot">DOT</option>
            <option value="mermaid">Mermaid</option>
          </select>
          <button onClick={() => api<{ content: string }>(`/api/snapshots/${sid}/export?format=${exportFmt}`).then((r) => setExportContent(r.content as string))} className="rounded bg-automation px-3 py-1 text-sm text-white">
            Gerar {exportFmt.toUpperCase()}
          </button>
        </div>
        {exportContent && <pre className="mt-3 max-h-64 overflow-auto rounded bg-background p-3 font-mono text-xs">{exportContent.slice(0, 4000)}</pre>}
      </Card>
    </div>
  );
}
