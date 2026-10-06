import { API_BASE, apiRequest } from "@/api/client";
import type { User } from "@/api/types";

/** Full-page navigation target: the backend redirects the browser to Spotify. */
export const SPOTIFY_LOGIN_URL: string = `${API_BASE}/auth/spotify/login`;

export function fetchCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}

export function logout(): Promise<void> {
  return apiRequest<void>("/auth/logout", { method: "POST" });
}
