import { useState } from "react";
import { Upload, FileArchive, Loader2 } from "lucide-react";
import { snapshotsApi, PushResponse } from "@/shared/api/client";
import { Button } from "@/shared/ui/Button";
import { Badge } from "@/shared/ui/Badge";
import { Card, CardHeader } from "@/shared/ui/Card";

export function UploadDrop({ onPushed }: { onPushed: (r: PushResponse) => void }) {
  const [drag, setDrag] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contribute, setContribute] = useState(false);

  async function handleFile(f: File) {
    setLoading(true);
    setError(null);
    try {
      const res = await snapshotsApi.push(f, contribute);
      onPushed(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="border-dashed">
      <CardHeader title="Upload do repositório" subtitle="ZIP até 100MB · parsing em <800ms · 0 IA" />
      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition-colors ${drag ? "border-intelligence bg-intelligence/5" : "border-border bg-surface-2"}`}
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-3">
          {loading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
        </div>
        <p className="mt-3 text-sm font-medium">Arraste o ZIP ou clique para selecionar</p>
        <p className="mono mt-1 text-xs text-text-muted">ou `cascudo push ./meu-projeto --contribute`</p>

        <label className="mt-4">
          <input type="file" accept=".zip" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} disabled={loading} />
          <span className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-automation px-4 py-2 text-sm font-medium text-white hover:bg-automation/90">
            <FileArchive size={14} /> Selecionar ZIP
          </span>
        </label>

        <label className="mt-4 flex items-center gap-2 text-xs text-text-secondary">
          <input type="checkbox" checked={contribute} onChange={(e) => setContribute(e.target.checked)} className="rounded" />
          Contribuir com padrões anonimizados (opt-in)
        </label>

        {error && <p className="mt-3 rounded bg-danger/10 px-3 py-2 font-mono text-xs text-danger">{error}</p>}
      </div>

      <div className="mono mt-3 flex gap-2 text-[11px] text-text-muted">
        <Badge variant="flow">FLOW</Badge>
        <Badge variant="dead">DEAD</Badge>
        <Badge variant="pattern">PATTERN 73%</Badge>
        <span className="ml-auto">DRAG → PUSH → SCAN &lt;800ms</span>
      </div>
    </Card>
  );
}
