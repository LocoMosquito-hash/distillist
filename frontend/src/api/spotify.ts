import { apiRequest } from "@/api/client";
import type { PlaylistPage } from "@/api/types";

export function fetchPlaylists(limit: number, offset: number): Promise<PlaylistPage> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiRequest<PlaylistPage>(`/spotify/playlists?${params.toString()}`);
}
