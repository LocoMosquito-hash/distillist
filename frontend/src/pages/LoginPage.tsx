import { Button, Center, Paper, Stack, Text, Title } from "@mantine/core";
import type { JSX } from "react";
import { Navigate } from "react-router-dom";

import { SPOTIFY_LOGIN_URL } from "@/api/auth";
import { FullPageLoader } from "@/components/common/FullPageLoader";
import { DEFAULT_PATH } from "@/components/layout/navItems";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { palette } from "@/theme";

export function LoginPage(): JSX.Element {
  const { data: user, isPending } = useCurrentUser();

  if (isPending) return <FullPageLoader />;
  if (user !== undefined) return <Navigate to={DEFAULT_PATH} replace />;

  return (
    <Center h="100vh" bg={palette.background}>
      <Paper withBorder shadow="sm" p="xl" w={360}>
        <Stack align="center" gap="md">
          <Title order={2} fw={500} style={{ letterSpacing: "0.06em" }}>
            distillist
          </Title>
          <Text size="sm" c="dimmed" ta="center">
            Log in with your Spotify account to import and manage your playlists.
          </Text>
          {/* A plain link on purpose: the browser must navigate to the backend, which redirects to Spotify. */}
          <Button component="a" href={SPOTIFY_LOGIN_URL} color="dark" fullWidth>
            Log in to Spotify
          </Button>
        </Stack>
      </Paper>
    </Center>
  );
}
