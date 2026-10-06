import type { JSX, ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { ApiError } from "@/api/client";
import type { User } from "@/api/types";
import { ErrorAlert } from "@/components/common/ErrorAlert";
import { FullPageLoader } from "@/components/common/FullPageLoader";
import { useCurrentUser } from "@/hooks/useCurrentUser";

interface RequireAuthProps {
  children: (user: User) => ReactNode;
}

/** Renders its children only for a logged-in user; everyone else goes to /login. */
export function RequireAuth({ children }: RequireAuthProps): JSX.Element {
  const { data: user, error, isPending, refetch } = useCurrentUser();

  if (isPending) return <FullPageLoader />;

  if (error !== null) {
    if (error instanceof ApiError && error.status === 401) {
      return <Navigate to="/login" replace />;
    }
    return <ErrorAlert error={error} onRetry={() => void refetch()} />;
  }

  return <>{children(user)}</>;
}
