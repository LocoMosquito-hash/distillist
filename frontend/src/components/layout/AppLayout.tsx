import { AppShell } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import type { JSX } from "react";
import { Outlet } from "react-router-dom";

import type { User } from "@/api/types";
import { Sidebar } from "@/components/layout/Sidebar";
import { TitleBar } from "@/components/layout/TitleBar";
import { palette } from "@/theme";

const SIDEBAR_EXPANDED_WIDTH: number = 220;
const SIDEBAR_COLLAPSED_WIDTH: number = 48;

interface AppLayoutProps {
  user: User;
}

/** Title bar + collapsible sidebar + the current page (rendered through <Outlet />). */
export function AppLayout({ user }: AppLayoutProps): JSX.Element {
  const [expanded, { toggle }] = useDisclosure(true);

  return (
    <AppShell
      header={{ height: 44 }}
      navbar={{
        width: expanded ? SIDEBAR_EXPANDED_WIDTH : SIDEBAR_COLLAPSED_WIDTH,
        breakpoint: 0, // never switch to the mobile (full-width) navbar mode
      }}
      padding="lg"
      styles={{
        header: { backgroundColor: palette.titleBar, borderBottom: "1px solid rgba(255, 255, 255, 0.06)" },
        navbar: {
          backgroundColor: palette.sidebar,
          borderRight: `1px solid ${palette.border}`,
          overflow: "hidden",
        },
        main: { backgroundColor: palette.background },
      }}
    >
      <AppShell.Header>
        <TitleBar userName={user.display_name ?? user.spotify_id} />
      </AppShell.Header>

      <AppShell.Navbar>
        <Sidebar expanded={expanded} onToggle={toggle} />
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
