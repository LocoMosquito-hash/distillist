# backend/app/integrations/spotify/client.py


from typing import Any

import httpx

from app.integrations.spotify.models import (
    SpotifyCurrentlyPlaying,
    SpotifyPlaylistPage,
    SpotifyUser,
)

API_BASE_URL: str = "https://api.spotify.com/v1"


class SpotifyApiError(Exception):
    """Raised when a call to the Spotify Web API fails.

    `status_code` is Spotify's HTTP status (None if Spotify was unreachable).
    `retry_after` is the number of seconds Spotify asked us to wait (429 only).
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


def _error_message(response: httpx.Response) -> str:
    """Extract Spotify's own error message, falling back to the status code."""
    try:
        message = response.json()["error"]["message"]
        if isinstance(message, str) and message:
            return message
    except (ValueError, KeyError, TypeError):
        pass
    return f"HTTP {response.status_code}"


async def _get(
    access_token: str,
    path: str,
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    """GET a Web API path with the user's token, translating failures to SpotifyApiError."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{API_BASE_URL}{path}",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
    except httpx.HTTPError as exc:
        raise SpotifyApiError("Could not reach the Spotify API") from exc

    if response.status_code == 429:
        header: str | None = response.headers.get("Retry-After")
        retry_after: int | None = int(header) if header is not None and header.isdigit() else None
        raise SpotifyApiError("Spotify rate limit reached", 429, retry_after)

    if response.is_error:
        raise SpotifyApiError(
            f"Spotify API error on {path}: {_error_message(response)}",
            response.status_code,
        )

    return response


async def get_current_user(access_token: str) -> SpotifyUser:
    """Fetch the profile of the user that owns `access_token`."""
    response = await _get(access_token, "/me")
    return SpotifyUser.model_validate(response.json())


async def get_playlists(access_token: str, limit: int, offset: int) -> SpotifyPlaylistPage:
    """Fetch one page of the playlists the user owns or follows (`GET /me/playlists`)."""
    response = await _get(
        access_token,
        "/me/playlists",
        params={"limit": limit, "offset": offset},
    )
    return SpotifyPlaylistPage.model_validate(response.json())


async def get_currently_playing(access_token: str) -> SpotifyCurrentlyPlaying | None:
    """Fetch what the user is playing, or None if nothing is (HTTP 204)."""
    response = await _get(access_token, "/me/player/currently-playing")

    if response.status_code == 204 or not response.content:
        return None

    data: dict[str, Any] = response.json()
    # Only tracks are supported for now: drop episodes/ads so they aren't parsed as tracks.
    if data.get("currently_playing_type") != "track":
        data["item"] = None

    return SpotifyCurrentlyPlaying.model_validate(data)
