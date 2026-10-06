import { NavLink, Stack } from "@mantine/core";
import type { JSX } from "react";
import { Link, useLocation } from "react-router-dom";

import { isNavGroup, NAV_ITEMS, type NavItem, type NavLeaf } from "@/components/layout/navItems";
import { palette } from "@/theme";

const GROUP_LABEL_STYLE = {
  fontSize: 12,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
} as const;

interface NavLeafLinkProps {
  leaf: NavLeaf;
  pathname: string;
  uppercase?: boolean;
}

function NavLeafLink({ leaf, pathname, uppercase = false }: NavLeafLinkProps): JSX.Element {
  const active: boolean = pathname === leaf.path;
  return (
    <NavLink
      component={Link}
      to={leaf.path}
      label={leaf.label}
      active={active}
      variant="subtle"
      color="dark"
      styles={{
        root: { borderRadius: 6, height: uppercase ? 30 : 28 },
        label: uppercase
          ? { ...GROUP_LABEL_STYLE, color: active ? palette.ink : palette.inkFaint }
          : { fontSize: 13, fontWeight: active ? 500 : 400, color: active ? palette.ink : palette.inkMuted },
      }}
    />
  );
}

/** The navigation tree shown in the sidebar (built from NAV_ITEMS). */
export function SidebarNav(): JSX.Element {
  const { pathname } = useLocation();

  return (
    <Stack gap={2} px={8} py={8}>
      {NAV_ITEMS.map((item: NavItem): JSX.Element => {
        if (!isNavGroup(item)) {
          return <NavLeafLink key={item.id} leaf={item} pathname={pathname} uppercase />;
        }
        return (
          <NavLink
            key={item.id}
            label={item.label}
            defaultOpened
            childrenOffset={12}
            variant="subtle"
            color="dark"
            styles={{
              root: { borderRadius: 6, height: 30 },
              label: { ...GROUP_LABEL_STYLE, color: palette.inkFaint },
            }}
          >
            {item.children.map(
              (child: NavLeaf): JSX.Element => (
                <NavLeafLink key={child.id} leaf={child} pathname={pathname} />
              ),
            )}
          </NavLink>
        );
      })}
    </Stack>
  );
}
