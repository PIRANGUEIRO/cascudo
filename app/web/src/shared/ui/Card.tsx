import React from "react";

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-lg border bg-surface p-4 ${className}`}>{children}</div>;
}

export function CardHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="mb-3 flex items-start justify-between">
      <div>
        <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        {subtitle && <p className="mono text-[11px] text-text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
