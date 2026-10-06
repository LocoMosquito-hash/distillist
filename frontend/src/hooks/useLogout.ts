import { useMutation, useQueryClient, type UseMutationResult } from "@tanstack/react-query";

import { logout } from "@/api/auth";

/** Ends the session on the server, then forgets everything we cached about the user. */
export function useLogout(): UseMutationResult<void, Error, void> {
  const queryClient = useQueryClient();
  return useMutation<void, Error, void>({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.clear();
    },
  });
}
