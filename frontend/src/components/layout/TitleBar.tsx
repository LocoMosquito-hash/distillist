import { Box, Text } from "@mantine/core";
import type { JSX } from "react";

import { UserMenu } from "@/components/layout/UserMenu";
import { palette } from "@/theme";

interface TitleBarProps {
  userName: string;
}

/** Top bar: app name centered, user menu on the right. */
export function TitleBar({ userName }: TitleBarProps): JSX.Element {
  return (
    <Box
      h="100%"
      pos="relative"
      style={{ display: "flex", alignItems: "center", justifyContent: "flex-end" }}
    >
      <Text
        pos="absolute"
        left="50%"
        fw={500}
        fz={14}
        style={{
          transform: "translateX(-50%)",
          letterSpacing: "0.06em",
          color: palette.titleBarText,
          pointerEvents: "none",
        }}
      >
        distillist
      </Text>
      <UserMenu displayName={userName} />
    </Box>
  );
}
