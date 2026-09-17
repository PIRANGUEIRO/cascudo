// Cliente tipado — única borda HTTP, escalável para 100 endpoints (Sprint1: workspace)
const BASE = "";

function wsHeaders(): Record<string, string> {
  const ws = localStorage.getItem("cascudo:workspace") || "ws-demo";
  return { "X-Workspace-Id": ws };
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = { ...wsHeaders(), ...(init?.headers || {}) };
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export type PushResponse = {
  snapshot_id: string;
  job_id: string;
  status: string;
  workspace_id: string;
  stats: { files: number; symbols: number; edges: number; loc: number; duration_ms?: number };
  issues: { dead: number; cycles: number; critical: number };
  patterns: { found: number; top: Array<{ hash: string; kind: string; canonical: string; frequency: number; count?: number }> };
};

export const snapshotsApi = {
  push: (file: File, contribute = false, sync = true) => {
    const fd = new FormData();
    fd.append("file", file);
    return api<PushResponse>(`/api/push?contribute=${contribute}&ephemeral=true&sync=${sync}`, { method: "POST", body: fd });
  },
  flow: (id: string, depth = 6) => api<{ entrypoints: string[]; nodes: unknown[]; edges: unknown[] }>(`/api/snapshots/${id}/flow?depth=${depth}`),
  dead: (id: string) => api<{ dead: Array<{ qualified_name: string; file: string; line: number; confidence: string }> }>(`/api/snapshots/${id}/dead`),
  cycles: (id: string) => api<{ cycles: string[][] }>(`/api/snapshots/${id}/cycles`),
  critical: (id: string) => api<{ critical: unknown[] }>(`/api/snapshots/${id}/critical`),
  patterns: (id: string) => api<{ patterns: Array<{ hash: string; kind: string; canonical: string; count: number; frequency: number }> }>(`/api/snapshots/${id}/patterns`),
  globalPatterns: (params?: { kind?: string; min_frequency?: number; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.kind) qs.set("kind", params.kind);
    if (params?.min_frequency) qs.set("min_frequency", String(params.min_frequency));
    if (params?.limit) qs.set("limit", String(params.limit));
    return api<{ patterns: Array<{ hash: string; kind: string; canonical: string; count: number; frequency: number }>; total_snapshots: number; stats: unknown }>(`/api/patterns?${qs}`);
  },
  symbol: (id: string, qname: string) => api<{ symbol: unknown; callers: string[]; callees: string[] }>(`/api/snapshots/${id}/symbol/${encodeURIComponent(qname)}`),
  job: (id: string) => api<{ id: string; status: string; progress: number }>(`/api/jobs/${id}`),
};
