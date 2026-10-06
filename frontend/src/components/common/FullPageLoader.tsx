import { Center, Loader } from "@mantine/core";
import type { JSX } from "react";

export function FullPageLoader(): JSX.Element {
  return (
    <Center h="100vh">
      <Loader color="dark" size="sm" />
    </Center>
  );
}
