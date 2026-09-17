/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      colors: {
        // Mateboard tokens — cor = semântica
        background: "#0B0D10",
        surface: "#111418",
        "surface-2": "#181C21",
        "surface-3": "#20252B",
        border: "#272C33",
        "text-primary": "#F3F4F6",
        "text-secondary": "#A7ADB7",
        "text-muted": "#6B7280",
        "text-disabled": "#454A52",
        automation: "#3B82F6", // ação
        intelligence: "#8B5CF6", // insight
        system: "#06B6D4", // infra
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
        info: "#38BDF8",
      },
      borderRadius: {
        sm: "6px",
        md: "8px",
        lg: "12px",
        xl: "16px",
      },
      animation: {
        "pulse-subtle": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
