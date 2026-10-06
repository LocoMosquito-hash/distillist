import { Anchor, Box, Group, Loader, Pagination, Stack, Text, Title } from "@mantine/core";
import { useState, type JSX } from "react";
import { Navigate } from "react-router-dom";

import { ApiError } from "@/api/client";
import { ErrorAlert } from "@/components/common/ErrorAlert";
import { PlaylistTable } from "@/components/playlists/PlaylistTable";
import { PlaylistToolbar } from "@/components/playlists/PlaylistToolbar";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { usePlaylists } from "@/hooks/usePlaylists";

const PAGE_SIZE: number = 20;

export function ImportPlaylistsPage(): JSX.Element {
  const [page, setPage] = useState<number>(1);
  const { data: user } = useCurrentUser();
  const { data, error, isPending, isFetching, refetch } = usePlaylists(page, PAGE_SIZE);

  // The session expired while the page was open.
  if (error instanceof ApiError && error.status === 401) {
    return <Navigate to="/login" replace />;
  }

  const ownerName: string = user?.display_name ?? user?.spotify_id ?? "Your";
  const totalPages: number = data !== undefined ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <Stack gap="md">
      <Group gap="xs">
        <Title order={4} fw={500}>
          {ownerName}'s Spotify playlists
        </Title>
        {isFetching && !isPending && <Loader size="xs" color="dark" />}
      </Group>

      {isPending && <Loader size="sm" color="dark" />}

      {error !== null && (
        <ErrorAlert title="Could not load your playlists" error={error} onRetry={() => void refetch()} />
      )}

      {data !== undefined && (
        <Box>
          <PlaylistTable playlists={data.items} />
        </Box>
      )}

      {data !== undefined && (
        <Group justify="space-between" align="center">
          <Pagination total={totalPages} value={page} onChange={setPage} size="sm" color="dark" />
          <PlaylistToolbar />
        </Group>
      )}

      <Text size="xs" c="dimmed">
        Playlist data provided by{" "}
        <Anchor href="https://www.spotify.com" target="_blank" rel="noreferrer" inherit>
          Spotify
        </Anchor>
        .
      </Text>
    </Stack>
  );
}
