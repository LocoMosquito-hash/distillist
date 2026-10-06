import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { fetchCurrentUser } from "@/api/auth";
import type { User } from "@/api/types";

export const CURRENT_USER_KEY = ["auth", "me"] as const;

/** The logged-in user. Fails with ApiError(401) when there is no valid session. */
export function useCurrentUser(): UseQueryResult<User, Error> {
  return useQuery<User, Error>({
    queryKey: CURRENT_USER_KEY,
    queryFn: fetchCurrentUser,
    staleTime: 5 * 60 * 1000,
  });
}
