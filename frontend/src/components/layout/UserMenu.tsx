import { Menu, Text, UnstyledButton } from "@mantine/core";
import { IconChevronDown, IconLogout, IconSettings } from "@tabler/icons-react";
import { useState, type JSX } from "react";
import { useNavigate } from "react-router-dom";

import { useLogout } from "@/hooks/useLogout";
import { palette } from "@/theme";

interface UserMenuProps {
  displayName: string;
}

/** The dropdown at the right end of the title bar. */
export function UserMenu({ displayName }: UserMenuProps): JSX.Element {
  const [opened, setOpened] = useState<boolean>(false);
  const navigate = useNavigate();
  const { mutate: doLogout, isPending } = useLogout();

  const handleLogout = (): void => {
    doLogout(undefined, { onSuccess: () => navigate("/login", { replace: true }) });
  };

  return (
    <Menu opened={opened} onChange={setOpened} position="bottom-end" width={160} shadow="md">
      <Menu.Target>
        <UnstyledButton
          h="100%"
          px="md"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            color: opened ? palette.titleBarText : palette.titleBarMuted,
            backgroundColor: opened ? "rgba(247, 246, 243, 0.07)" : "transparent",
            transition: "color 150ms, background-color 150ms",
          }}
        >
          <Text size="sm" inherit>
            {displayName}
          </Text>
          <IconChevronDown
            size={14}
            style={{ transition: "transform 200ms ease", transform: opened ? "rotate(180deg)" : "none" }}
          />
        </UnstyledButton>
      </Menu.Target>

      <Menu.Dropdown>
        <Menu.Item leftSection={<IconSettings size={14} />} disabled>
          Settings
        </Menu.Item>
        <Menu.Item leftSection={<IconLogout size={14} />} onClick={handleLogout} disabled={isPending}>
          Log out
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
}
