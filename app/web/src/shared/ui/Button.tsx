import React from "react";

type Variant = "primary" | "ghost" | "danger";

export function Button({
  children,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  const base = "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50";
  const styles: Record<Variant, string> = {
    primary: "bg-automation text-white hover:bg-automation/90",
    ghost: "bg-surface-2 text-text-secondary hover:bg-surface-3 hover:text-text-primary",
    danger: "bg-danger text-white hover:bg-danger/90",
  };
  return (
    <button className={`${base} ${styles[variant]}`} {...props}>
      {children}
    </button>
  );
}
