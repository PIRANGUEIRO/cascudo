import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Upload, GitBranch, Bug, Layers, Search } from "lucide-react";
import { useWorkspace } from "@/shared/lib/workspace";

// Shell SaaS — Sidebar + Topbar + Content (Mateboard 01 SHELLS)
// Escalável: adicionar item = 1 linha em NAV, rota em app/router
const NAV = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/upload", label: "Upload", icon: Upload },
  { to: "/flow", label: "Fluxo", icon: GitBranch },
  { to: "/graph", label: "Grafo", icon: Layers },
  { to: "/dead", label: "Poços Mortos", icon: Bug },
  { to: "/patterns", label: "Padrões", icon: Search },
  { to: "/diff", label: "Diff", icon: Search },
  { to: "/hotspots", label: "Hotspots", icon: Bug },
  { to: "/search", label: "Busca", icon: Search },
] as const;

export function Shell() {
  const { workspaceId, setWorkspace } = useWorkspace();
  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar — SURFACE #111418 */}
      <aside className="flex w-[240px] shrink-0 flex-col border-r bg-surface">
        <div className="border-b px-5 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-intelligence text-xs font-bold text-white">≡</div>
            <div>
              <div className="text-sm font-semibold tracking-tight">CASCUDO</div>
              <div className="mono text-[10px] leading-none text-text-muted">MAPA MENTAL 0 IA</div>
            </div>
          </div>
          <div className="mono mt-2 text-[10px] text-text-muted">SYNC 22:41:08 · MODEL v0.1 · DARK</div>
          <select value={workspaceId} onChange={(e) => setWorkspace(e.target.value)} className="mono mt-2 w-full rounded border bg-surface-2 px-2 py-1 text-xs">
            <option value="ws-demo">ws-demo (sem auth)</option>
            <option value="ws-test">ws-test</option>
            <option value="ws-pro">ws-pro</option>
          </select>
          <div className="mono mt-1 text-[10px] text-text-muted">header X-Workspace-Id · JWT sprint2</div>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          <div className="label px-2 py-2">NAVEGAÇÃO</div>
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors ${isActive ? "bg-surface-2 text-text-primary" : "text-text-secondary hover:bg-surface-2 hover:text-text-primary"}`
              }
            >
              <Icon size={16} strokeWidth={1.5} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t p-3">
          <div className="rounded-md bg-surface-2 p-3">
            <div className="label">CORPUS</div>
            <div className="mt-1 text-xs text-text-secondary">Padrões aprendidos por contagem — auditável via SQL.</div>
            <div className="mono mt-2 text-[11px] text-intelligence">73% Controller→Service</div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-1 flex-col">
        {/* Topbar — Command Bar signature */}
        <header className="flex h-14 items-center justify-between border-b bg-surface/50 px-6 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-md border bg-surface-2 px-3 py-1.5 text-sm text-text-muted md:flex">
              <span className="rounded bg-surface-3 px-1.5 py-0.5 font-mono text-xs">⌘K</span>
              Buscar símbolos, padrões, arquivos...
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="mono text-xs text-text-muted">EPHEMERAL · 0 IA · AUDITÁVEL</span>
            <span className="h-2 w-2 rounded-full bg-success" title="API ok" />
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
