import type { JSX } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import type { User } from "@/api/types";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { AppLayout } from "@/components/layout/AppLayout";
import { DEFAULT_PATH } from "@/components/layout/navItems";
import { ImportPlaylistsPage } from "@/pages/ImportPlaylistsPage";
import { LoginPage } from "@/pages/LoginPage";
import { SavedPlaylistsPage } from "@/pages/SavedPlaylistsPage";
import { ServiceStatsPage } from "@/pages/ServiceStatsPage";

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Everything below requires a logged-in user and is wrapped in the app layout. */}
      <Route
        element={<RequireAuth>{(user: User): JSX.Element => <AppLayout user={user} />}</RequireAuth>}
      >
        <Route path="/playlists/import" element={<ImportPlaylistsPage />} />
        <Route path="/playlists/saved" element={<SavedPlaylistsPage />} />
        <Route path="/service-and-stats" element={<ServiceStatsPage />} />
      </Route>

      <Route path="*" element={<Navigate to={DEFAULT_PATH} replace />} />
    </Routes>
  );
}
