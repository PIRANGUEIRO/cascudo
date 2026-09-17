// Tokens tipados — única fonte da verdade visual
export const tokens = {
  surface: {
    bg: "#0B0D10",
    surface: "#111418",
    surface2: "#181C21",
    surface3: "#20252B",
    border: "#272C33",
  },
  text: {
    primary: "#F3F4F6",
    secondary: "#A7ADB7",
    muted: "#6B7280",
    disabled: "#454A52",
  },
  semantic: {
    automation: "#3B82F6", // ação
    intelligence: "#8B5CF6", // insight/padrão
    system: "#06B6D4", // infra
    success: "#22C55E",
    warning: "#F59E0B",
    danger: "#EF4444",
    info: "#38BDF8",
  },
  font: {
    sans: "Inter",
    mono: "IBM Plex Mono",
  },
  radius: { sm: 6, md: 8, lg: 12, xl: 16 },
  motion: { hover: 150, modal: 200 },
} as const;

// Helpers semânticos — cor = informação
export const badgeFor = {
  dead: { bg: "bg-danger/10", text: "text-danger", dot: "bg-danger", label: "DEAD" },
  cycle: { bg: "bg-warning/10", text: "text-warning", dot: "bg-warning", label: "CYCLE" },
  critical: { bg: "bg-danger/10", text: "text-danger", dot: "bg-danger", label: "CRITICAL" },
  pattern: { bg: "bg-intelligence/10", text: "text-intelligence", dot: "bg-intelligence", label: "PATTERN" },
  flow: { bg: "bg-system/10", text: "text-system", dot: "bg-system", label: "FLOW" },
} as const;
