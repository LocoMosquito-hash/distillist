# backend/app/integrations/spotify/client.py


import httpx

from app.integrations.spotify.models import SpotifyUser

API_BASE_URL: str = "https://api.spotify.com/v1"


class SpotifyApiError(Exception):
    """Raised when a call to the Spotify Web API fails."""


async def get_current_user(access_token: str) -> SpotifyUser:
    """Fetch the profile of the user that owns `access_token`."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.HTTPError as exc:
        raise SpotifyApiError("Could not reach the Spotify API") from exc

    if response.is_error:
        raise SpotifyApiError(f"Spotify API returned {response.status_code} for /me")

    return SpotifyUser.model_validate(response.json())
