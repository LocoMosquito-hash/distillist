# backend/app/integrations/spotify/auth.py


import logging
from urllib.parse import urlencode

import httpx

from app.config import Settings
from app.integrations.spotify.models import SpotifyToken

log = logging.getLogger("uvicorn")

AUTHORIZE_URL: str = "https://accounts.spotify.com/authorize"
TOKEN_URL: str = "https://accounts.spotify.com/api/token"

SCOPES: list[str] = [
    "playlist-read-private",
    "playlist-read-collaborative",
]


class SpotifyAuthError(Exception):
    """Raised when Spotify rejects or fails an authorization request."""


def build_authorize_url(settings: Settings, state: str) -> str:
    """Build the Spotify URL the user's browser is sent to in order to log in."""
    params: dict[str, str] = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_token(settings: Settings, code: str) -> SpotifyToken:
    """Trade the one-time authorization `code` for access/refresh tokens."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.spotify_redirect_uri,
                },
                auth=(
                    settings.spotify_client_id,
                    settings.spotify_client_secret.get_secret_value(),
                ),
            )
    except httpx.HTTPError as exc:
        raise SpotifyAuthError("Could not reach Spotify's token endpoint") from exc

    if response.is_error:
        log.error("Spotify token exchange failed: %s %s", response.status_code, response.text)
        raise SpotifyAuthError(f"Spotify rejected the token request ({response.status_code})")

    return SpotifyToken.model_validate(response.json())
