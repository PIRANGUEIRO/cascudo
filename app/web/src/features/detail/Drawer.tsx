import { useEffect, useState } from "react";
import { X, Users, ArrowRight, Hash, FileCode, AlertTriangle } from "lucide-react";
import { snapshotsApi } from "@/shared/api/client";
import { Badge } from "@/shared/ui/Badge";
import { Card } from "@/shared/ui/Card";

type Props = { snapshotId: string; qname: string | null; onClose: () => void };

export function Drawer({ snapshotId, qname, onClose }: Props) {
  const [data, setData] = useState<{ symbol: any; callers: string[]; callees: string[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [patterns, setPatterns] = useState<any[]>([]);

  useEffect(() => {
    if (!qname) return;
    setLoading(true);
    Promise.all([snapshotsApi.symbol(snapshotId, qname), snapshotsApi.patterns(snapshotId).catch(() => ({ patterns: [] }))])
      .then(([sym, pat]) => {
        setData(sym as any);
        // filtra padrões que contêm o símbolo
        const related = (pat as any).patterns?.filter((p: any) => p.canonical?.includes(qname.split(".").pop() || "")) ?? [];
        setPatterns(related.slice(0, 3));
      })
      .finally(() => setLoading(false));
  }, [snapshotId, qname]);

  if (!qname) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-40 flex w-[420px] flex-col border-l bg-surface shadow-2xl">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="mono text-xs text-text-muted">DRILL-DOWN · 0 IA</div>
        <button onClick={onClose} className="rounded p-1 hover:bg-surface-2">
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="mono text-xs text-text-muted">Carregando {qname}…</div>
        ) : data ? (
          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2">
                <FileCode size={14} className="text-system" />
                <span className="font-mono text-sm font-semibold">{data.symbol.qualified_name}</span>
              </div>
              <div className="mono mt-1 text-xs text-text-secondary">{data.symbol.file}:{data.symbol.line} · {data.symbol.kind} · CC {data.symbol.cc ?? 1} · lang {data.symbol.lang}</div>
              <div className="mt-2 flex gap-2">
                {data.symbol.is_entrypoint && <Badge variant="pattern">ENTRYPOINT</Badge>}
                {data.symbol.is_exported && <Badge variant="flow">EXPORTED</Badge>}
                {data.symbol.cc > 15 && <Badge variant="critical">CC {data.symbol.cc}</Badge>}
              </div>
            </div>

            <Card>
              <div className="label flex items-center gap-1"><Users size={10} /> CALLERS ({data.callers.length})</div>
              <div className="mt-2 space-y-1">
                {data.callers.length ? data.callers.map((c) => <div key={c} className="mono rounded bg-surface-2 px-2 py-1 text-xs">{c}</div>) : <div className="mono text-xs text-text-muted">in_degree==0 → candidato a poço morto</div>}
              </div>
            </Card>

            <Card>
              <div className="label flex items-center gap-1"><ArrowRight size={10} /> CALLEES ({data.callees.length})</div>
              <div className="mt-2 space-y-1">
                {data.callees.length ? data.callees.map((c) => <div key={c} className="mono rounded bg-surface-2 px-2 py-1 text-xs">{c}</div>) : <div className="mono text-xs text-text-muted">folha — sem chamadas</div>}
              </div>
            </Card>

            <Card>
              <div className="label flex items-center gap-1"><Hash size={10} /> PADRÕES RELACIONADOS</div>
              {patterns.length ? (
                <div className="mt-2 space-y-2">
                  {patterns.map((p: any) => (
                    <div key={p.hash} className="flex items-center justify-between rounded bg-intelligence/10 px-2 py-1.5">
                      <span className="mono text-xs">{p.canonical}</span>
                      <span className="text-xs font-bold text-intelligence">{(p.frequency * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mono mt-2 text-xs text-text-muted">Sem padrão frequente — anomalia rara (2% do corpus)</div>
              )}
              <div className="mono mt-2 text-[11px] text-text-muted">Auditável: hash canônico → COUNT(*) / total</div>
            </Card>

            <Card>
              <div className="label flex items-center gap-1"><AlertTriangle size={10} /> EVIDÊNCIA 0 IA</div>
              <div className="mono mt-2 text-xs leading-relaxed text-text-secondary">
                • dead? in_degree==0 (CALLS) <br />• ciclo? SCC Kosaraju <br />• critical? CC&gt;15 ou top 1% out_degree <br />• padrão? frequência no corpus
              </div>
            </Card>

            <div className="mono rounded bg-surface-2 p-3 text-xs leading-relaxed text-text-secondary">
              // {data.symbol.file}:{data.symbol.line} — snippet em V2 via tree-sitter query.scm
              <br />
              {qname.split(".").pop()}() {"{"} … {"}"}
            </div>
          </div>
        ) : (
          <div className="mono text-xs text-danger">símbolo não encontrado</div>
        )}
      </div>
    </div>
  );
}
