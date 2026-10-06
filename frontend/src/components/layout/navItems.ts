// Single source of truth for the sidebar. Add a page here and it shows up in the nav.
// The matching <Route> lives in App.tsx.

export interface NavLeaf {
  id: string;
  label: string;
  path: string;
}

export interface NavGroup {
  id: string;
  label: string;
  children: NavLeaf[];
}

export type NavItem = NavLeaf | NavGroup;

export function isNavGroup(item: NavItem): item is NavGroup {
  return "children" in item;
}

export const DEFAULT_PATH: string = "/playlists/import";

export const NAV_ITEMS: NavItem[] = [
  {
    id: "playlists",
    label: "Playlists",
    children: [
      { id: "import-playlists", label: "Import playlists", path: "/playlists/import" },
      { id: "saved-playlists", label: "Saved playlists", path: "/playlists/saved" },
    ],
  },
  { id: "service-and-stats", label: "Service and stats", path: "/service-and-stats" },
];
