import { Button, Group } from "@mantine/core";
import type { JSX } from "react";

/** Actions under the playlist table. Not wired up yet (no backend support). */
export function PlaylistToolbar(): JSX.Element {
  return (
    <Group justify="flex-end" gap="sm">
      <Button variant="default" size="xs" disabled>
        Import/update
      </Button>
      <Button variant="default" size="xs" disabled>
        Filter/sort
      </Button>
    </Group>
  );
}
