import { keepPreviousData, useQuery, type UseQueryResult } from "@tanstack/react-query";

import { fetchPlaylists } from "@/api/spotify";
import type { PlaylistPage } from "@/api/types";

/** One page of the user's Spotify playlists (page is 1-based). */
export function usePlaylists(page: number, pageSize: number): UseQueryResult<PlaylistPage, Error> {
  const offset: number = (page - 1) * pageSize;
  return useQuery<PlaylistPage, Error>({
    queryKey: ["spotify", "playlists", { limit: pageSize, offset }],
    queryFn: () => fetchPlaylists(pageSize, offset),
    placeholderData: keepPreviousData, // keep showing the old page while the next one loads
  });
}
