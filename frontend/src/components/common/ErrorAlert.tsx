import { Alert, Button } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";
import type { JSX } from "react";

import { ApiError } from "@/api/client";

interface ErrorAlertProps {
  title?: string;
  error: Error;
  onRetry?: () => void;
}

/** Shows the backend's error message (and the Retry-After hint on rate limits). */
export function ErrorAlert({ title = "Something went wrong", error, onRetry }: ErrorAlertProps): JSX.Element {
  const rateLimitHint: string =
    error instanceof ApiError && error.status === 429 && error.retryAfter !== null
      ? ` Try again in ${error.retryAfter} seconds.`
      : "";

  return (
    <Alert color="red" variant="light" icon={<IconAlertCircle size={18} />} title={title}>
      {error.message}
      {rateLimitHint}
      {onRetry !== undefined && (
        <Button mt="sm" size="xs" color="dark" variant="light" onClick={onRetry}>
          Try again
        </Button>
      )}
    </Alert>
  );
}
