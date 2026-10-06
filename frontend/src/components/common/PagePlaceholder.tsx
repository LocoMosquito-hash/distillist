import { Stack, Text, Title } from "@mantine/core";
import type { JSX } from "react";

interface PagePlaceholderProps {
  title: string;
  description?: string;
}

/** Stand-in for pages that are not built yet. */
export function PagePlaceholder({
  title,
  description = "Coming soon.",
}: PagePlaceholderProps): JSX.Element {
  return (
    <Stack gap="xs">
      <Title order={3}>{title}</Title>
      <Text c="dimmed">{description}</Text>
    </Stack>
  );
}
