import { ActionIcon, Box, ScrollArea } from "@mantine/core";
import { IconLayoutSidebarLeftCollapse, IconLayoutSidebarLeftExpand } from "@tabler/icons-react";
import type { JSX } from "react";

import { SidebarNav } from "@/components/layout/SidebarNav";
import { palette } from "@/theme";

interface SidebarProps {
  expanded: boolean;
  onToggle: () => void;
}

/** Content of the left navigation panel: a collapse toggle on top, the nav tree below. */
export function Sidebar({ expanded, onToggle }: SidebarProps): JSX.Element {
  return (
    <>
      <Box
        h={44}
        px={10}
        style={{
          display: "flex",
          alignItems: "center",
          flexShrink: 0,
          borderBottom: `1px solid ${palette.border}`,
        }}
      >
        <ActionIcon
          variant="subtle"
          color="dark"
          onClick={onToggle}
          aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
          title={expanded ? "Collapse sidebar" : "Expand sidebar"}
        >
          {expanded ? (
            <IconLayoutSidebarLeftCollapse size={18} stroke={1.75} />
          ) : (
            <IconLayoutSidebarLeftExpand size={18} stroke={1.75} />
          )}
        </ActionIcon>
      </Box>

      <ScrollArea
        style={{
          flex: 1,
          opacity: expanded ? 1 : 0,
          pointerEvents: expanded ? "auto" : "none",
          transition: "opacity 150ms ease",
        }}
      >
        <SidebarNav />
      </ScrollArea>
    </>
  );
}
