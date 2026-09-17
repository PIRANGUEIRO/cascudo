import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { snapshotsApi } from "@/shared/api/client";
import { FlowView } from "@/features/flow/FlowView";
import { Drawer } from "@/features/detail/Drawer";
import { Card } from "@/shared/ui/Card";
import { Button } from "@/shared/ui/Button";
import { useWorkspace } from "@/shared/lib/workspace";

export function FlowPage() {
  const [params] = useSearchParams();
  const snapshotId = params.get("snapshot") || "demo";
  const { workspaceId } = useWorkspace();
  const [data, setData] = useState<{ nodes: any[]; edges: any[]; entrypoints?: string[] } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [depth, setDepth] = useState(6);
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    if (snapshotId === "demo") return;
    setErr(null);
    snapshotsApi
      .flow(snapshotId, depth)
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, [snapshotId, depth]);

  const filtered = data
    ? {
        nodes: (data.nodes as any[]).filter((n: any) => !filter || n.id.toLowerCase().includes(filter.toLowerCase()) || n.kind?.includes(filter)),
        edges: (data.edges as any[]).filter((e: any) => !filter || e.source.toLowerCase().includes(filter.toLowerCase())),
      }
    : null;

  if (snapshotId === "demo") {
    return (
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Fluxo — demo (ws: {workspaceId})</h2>
          <span className="mono text-xs text-text-muted">ELK hierárquico · clique no node → drawer</span>
        </div>
        <FlowView
          nodes={[
            { id: "index.ts", kind: "file", label: "index.ts", depth: 0 },
            { id: "app.controller", kind: "function", label: "app.controller", depth: 1 },
            { id: "user.service", kind: "function", label: "user.service", depth: 2 },
            { id: "db.repo", kind: "function", label: "db.repo", depth: 3 },
          ]}
          edges={[
            { source: "index.ts", target: "app.controller", kind: "CALLS" },
            { source: "app.controller", target: "user.service", kind: "CALLS" },
            { source: "user.service", target: "db.repo", kind: "CALLS" },
          ]}
          onNodeClick={setSelected}
        />
        <Card>
          <p className="text-sm text-text-secondary">Faça upload primeiro — depois acesse <span className="mono text-intelligence">/flow?snapshot=&lt;id&gt;</span></p>
          <Button className="mt-3" onClick={() => (window.location.href = "/upload")}>Ir para Upload</Button>
        </Card>
        {selected && <Drawer snapshotId="demo" qname={selected} onClose={() => setSelected(null)} />}
      </div>
    );
  }

  if (err) return <div className="font-mono text-sm text-danger">{err}</div>;
  if (!data) return <div className="mono text-sm text-text-muted">Carregando fluxograma {snapshotId} (depth {depth})…</div>;

  return (
    <div className="mx-auto max-w-6xl space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Fluxo — {snapshotId} <span className="mono text-xs font-normal text-text-muted">ws {workspaceId} · entrypoints {data.entrypoints?.join(", ")}</span></h2>
        <div className="flex items-center gap-2">
          <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="filtrar (kind/nome)" className="rounded border bg-surface-2 px-3 py-1.5 text-sm outline-none placeholder:text-text-muted" />
          <span className="mono text-xs text-text-muted">depth</span>
          <input type="range" min={2} max={10} value={depth} onChange={(e) => setDepth(Number(e.target.value))} />
          <span className="mono text-xs">{depth}</span>
        </div>
      </div>

      <FlowView nodes={filtered!.nodes as any} edges={filtered!.edges as any} onNodeClick={setSelected} />

      <div className="mono flex gap-2 text-[11px] text-text-muted">
        <span>{filtered!.nodes.length}/{ (data.nodes as any[]).length} nodes</span>·<span>{filtered!.edges.length} edges</span>·<span>BFS depth {depth} a partir de entrypoints</span>
      </div>

      {selected && <Drawer snapshotId={snapshotId} qname={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
