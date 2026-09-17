import { useSearchParams } from "react-router-dom";
import { PatternsList } from "@/features/patterns/PatternsList";
import { Card } from "@/shared/ui/Card";

export function PatternsPage() {
  const [params] = useSearchParams();
  const snapshotId = params.get("snapshot") || undefined;

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Padrões do Corpus</h2>
        <p className="mono text-xs text-text-muted">Hash canônico + COUNT(*) — sem LSTM, sem embedding, 100% auditável. F12: contribuir anonimamente.</p>
      </div>

      <Card>
        <div className="label">COMO FUNCIONA (0 IA)</div>
        <div className="mono mt-1 text-xs leading-relaxed text-text-secondary">
          1. extrai subgrafos 3-5 nós → 2. canonicaliza sort(nodes)+sort(edges) → SHA256 → 3. UPSERT patterns(count++) → 4. freq = count/total
        </div>
      </Card>

      <PatternsList snapshotId={snapshotId} />
    </div>
  );
}
