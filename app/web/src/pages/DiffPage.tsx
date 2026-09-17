import { useState } from "react";
import { api } from "@/shared/api/client";
import { Card } from "@/shared/ui/Card";
import { Button } from "@/shared/ui/Button";
import { Badge } from "@/shared/ui/Badge";

export function DiffPage() {
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [diff, setDiff] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await api<{ diff: any }>(`/api/snapshots/diff`, { method: "POST", body: JSON.stringify({ from, to }), headers: { "Content-Type": "application/json" } });
    setDiff(res.diff);
    setLoading(false);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <h2 className="text-lg font-semibold">Diff entre Snapshots — F8</h2>
      <p className="mono text-xs text-text-muted">Verde = added, vermelho = removed, auditável via JSON</p>
      <div className="flex gap-2">
        <input value={from} onChange={(e) => setFrom(e.target.value)} placeholder="snapshot from (snap-xxx)" className="flex-1 rounded border bg-surface-2 px-3 py-2 text-sm" />
        <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="snapshot to" className="flex-1 rounded border bg-surface-2 px-3 py-2 text-sm" />
        <Button onClick={run} disabled={loading || !from || !to}>{loading ? "…" : "Comparar"}</Button>
      </div>
      {diff && (
        <div className="space-y-3">
          <Card>
            <div className="mono text-xs">{diff.summary}</div>
            <div className="mt-2 flex gap-2">
              <Badge variant="dead">+{diff.nodes.added.length} nodes</Badge>
              <Badge variant="critical">-{diff.nodes.removed.length} nodes</Badge>
              <Badge variant="pattern">{diff.edges.added.length} edges added</Badge>
            </div>
          </Card>
          <Card>
            <div className="label">NODES ADDED (verde)</div>
            <div className="mono mt-1 text-xs text-success">{diff.nodes.added.slice(0, 20).join(", ") || "—"}</div>
          </Card>
          <Card>
            <div className="label">NODES REMOVED (vermelho)</div>
            <div className="mono mt-1 text-xs text-danger">{diff.nodes.removed.slice(0, 20).join(", ") || "—"}</div>
          </Card>
          <Card>
            <div className="label">DEAD INTRODUZIDO</div>
            <div className="mono mt-1 text-xs text-warning">{diff.dead.introduced.join(", ") || "nenhum"}</div>
          </Card>
        </div>
      )}
    </div>
  );
}
