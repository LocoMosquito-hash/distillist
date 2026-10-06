import { createTheme, type MantineThemeOverride } from "@mantine/core";

// Colors taken from the original App.tsx prototype.
export const palette = {
  background: "#f7f6f3",
  sidebar: "#efede8",
  titleBar: "#161614",
  titleBarText: "rgba(247, 246, 243, 0.85)",
  titleBarMuted: "rgba(247, 246, 243, 0.55)",
  menuBackground: "#1e1e1c",
  ink: "#161614",
  inkMuted: "rgba(22, 22, 20, 0.55)",
  inkFaint: "rgba(22, 22, 20, 0.45)",
  hover: "rgba(22, 22, 20, 0.05)",
  selected: "rgba(22, 22, 20, 0.08)",
  border: "rgba(22, 22, 20, 0.08)",
} as const;

export const theme: MantineThemeOverride = createTheme({
  primaryColor: "dark",
  fontFamily:
    'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  defaultRadius: "md",
});
