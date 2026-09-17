import { Card } from "@/shared/ui/Card";

export function GenericPage({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{title}</h2>
      {subtitle && <p className="text-sm text-text-secondary">{subtitle}</p>}
      <Card>
        <p className="mono text-xs text-text-muted">Em construção — vertical slice S1/S2. Estrutura FSD já pronta para escalar.</p>
        <p className="mt-2 text-sm text-text-secondary">
          Este placeholder segue o Shell SaaS + composição Split/Canvas. Adicionar conteúdo = criar <span className="mono text-intelligence">features/{title.toLowerCase()}</span> + rota.
        </p>
      </Card>
    </div>
  );
}
