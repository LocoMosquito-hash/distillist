import { Anchor, Table, Text } from "@mantine/core";
import type { JSX } from "react";

import type { Playlist } from "@/api/types";

function yesNo(value: boolean | null): string {
  if (value === null) return "—";
  return value ? "Yes" : "No";
}

interface PlaylistTableProps {
  playlists: Playlist[];
}

/** Presentational table of playlists. Knows nothing about fetching. */
export function PlaylistTable({ playlists }: PlaylistTableProps): JSX.Element {
  if (playlists.length === 0) {
    return <Text c="dimmed">No playlists found.</Text>;
  }

  return (
    <Table.ScrollContainer minWidth={600}>
      <Table highlightOnHover verticalSpacing="xs">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Playlist name</Table.Th>
            <Table.Th>Owner</Table.Th>
            <Table.Th ta="right">Tracks</Table.Th>
            <Table.Th>Public</Table.Th>
            <Table.Th>Collaborative</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {playlists.map(
            (playlist: Playlist): JSX.Element => (
              <Table.Tr key={playlist.id}>
                <Table.Td>
                  {playlist.spotify_url !== null ? (
                    <Anchor
                      href={playlist.spotify_url}
                      target="_blank"
                      rel="noreferrer"
                      c="inherit"
                      underline="hover"
                    >
                      {playlist.name}
                    </Anchor>
                  ) : (
                    playlist.name
                  )}
                </Table.Td>
                <Table.Td>{playlist.owner_name ?? "—"}</Table.Td>
                <Table.Td ta="right">{playlist.track_count ?? "—"}</Table.Td>
                <Table.Td>{yesNo(playlist.public)}</Table.Td>
                <Table.Td>{yesNo(playlist.collaborative)}</Table.Td>
              </Table.Tr>
            ),
          )}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  );
}
