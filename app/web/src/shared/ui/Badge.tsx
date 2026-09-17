import { badgeFor } from "../config/tokens";

type Variant = keyof typeof badgeFor;

export function Badge({ variant, children }: { variant: Variant; children: React.ReactNode }) {
  const t = badgeFor[variant];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] font-semibold tracking-wide ${t.bg} ${t.text} font-mono`}>
      <span className={`h-1.5 w-1.5 rounded-full ${t.dot}`} />
      {children}
    </span>
  );
}
