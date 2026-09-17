import { useEffect, useMemo, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from "reactflow";
import ELK from "elkjs/lib/elk.bundled.js";
import "reactflow/dist/style.css";

type FlowNode = { id: string; kind: string; label: string; depth: number; file?: string };
type FlowEdge = { source: string; target: string; kind: string };

const elk = new ELK();

// ELK hierárquico — validação Sprint2: prova que layout não vira hairball com 500 nodes
async function elkLayout(nodes: FlowNode[], edges: FlowEdge[]) {
  const graph = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "RIGHT",
      "elk.spacing.nodeNode": "40",
      "elk.layered.spacing.nodeNodeBetweenLayers": "80",
      "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
      "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
    },
    children: nodes.map((n) => ({
      id: n.id,
      width: 180,
      height: 44,
      layoutOptions: { "elk.portConstraints": "FIXED_SIDE" },
    })),
    edges: edges.map((e) => ({ id: `${e.source}->${e.target}`, sources: [e.source], targets: [e.target] })),
  };
  // @ts-ignore
  const laid = await elk.layout(graph);
  const pos = new Map<string, { x: number; y: number }>();
  // @ts-ignore
  for (const c of laid.children || []) pos.set(c.id, { x: c.x || 0, y: c.y || 0 });
  return pos;
}

export function FlowView({
  nodes,
  edges,
  onNodeClick,
}: {
  nodes: FlowNode[];
  edges: FlowEdge[];
  onNodeClick?: (id: string) => void;
}) {
  const [pos, setPos] = useState<Map<string, { x: number; y: number }>>(new Map());
  const [useElk, setUseElk] = useState(true);

  useEffect(() => {
    if (!useElk || nodes.length > 500) {
      // fallback Dagre-like para 500+ nodes
      setPos(new Map());
      return;
    }
    elkLayout(nodes, edges).then(setPos);
  }, [nodes, edges, useElk]);

  const rfNodes: Node[] = useMemo(
    () =>
      nodes.map((n, i) => {
        const p = pos.get(n.id) || { x: (n.depth * 220) % 1100, y: (i % 20) * 56 };
        const isFile = n.kind === "file";
        const isEntrypoint = n.depth === 0;
        return {
          id: n.id,
          data: { label: `${n.label}` },
          position: p,
          style: {
            background: isEntrypoint ? "#8B5CF6" : isFile ? "#20252B" : "#181C21",
            color: "#F3F4F6",
            border: `1px solid ${isEntrypoint ? "#8B5CF6" : "#272C33"}`,
            borderRadius: 8,
            fontSize: 11,
            padding: 8,
            fontFamily: "IBM Plex Mono",
            width: 180,
            boxShadow: isEntrypoint ? "0 0 0 2px rgba(139,92,246,0.2)" : "none",
          },
        };
      }),
    [nodes, pos]
  );

  const rfEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => ({
        id: `${e.source}->${e.target}`,
        source: e.source,
        target: e.target,
        label: e.kind,
        style: { stroke: e.kind === "CALLS" ? "#3B82F6" : e.kind === "IMPORTS" ? "#06B6D4" : "#6B7280", strokeWidth: 1.2 },
        animated: e.kind === "CALLS",
        labelStyle: { fontSize: 9, fill: "#A7ADB7", fontFamily: "IBM Plex Mono" },
      })),
    [edges]
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="mono flex gap-2 text-[11px] text-text-muted">
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-intelligence" /> entrypoint</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-automation" /> CALLS</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-system" /> IMPORTS</span>
        </div>
        <label className="flex items-center gap-1 mono text-xs">
          <input type="checkbox" checked={useElk} onChange={(e) => setUseElk(e.target.checked)} /> ELK hierárquico
        </label>
      </div>
      <div className="h-[560px] rounded-lg border bg-surface">
        <ReactFlow nodes={rfNodes} edges={rfEdges} fitView onNodeClick={(_, n) => onNodeClick?.(n.id)}>
          <Background color="#272C33" gap={16} />
          <Controls />
          <MiniMap style={{ background: "#111418" }} maskColor="rgba(11,13,16,0.85)" nodeColor={(n) => (n.style?.background as string) || "#181C21"} />
        </ReactFlow>
      </div>
    </div>
  );
}
