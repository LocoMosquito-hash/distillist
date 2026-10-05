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
    "user-read-currently-playing",
]


class SpotifyAuthError(Exception):
    """Raised when Spotify rejects or fails an authorization request."""


class SpotifyGrantRejectedError(SpotifyAuthError):
    """Spotify rejected the code/refresh token itself (invalid, expired or revoked).

    Retrying won't help: the user has to go through the login flow again.
    """


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


async def _request_token(settings: Settings, data: dict[str, str]) -> SpotifyToken:
    """POST to Spotify's token endpoint, authenticating as the app (client id + secret)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TOKEN_URL,
                data=data,
                auth=(
                    settings.spotify_client_id,
                    settings.spotify_client_secret.get_secret_value(),
                ),
            )
    except httpx.HTTPError as exc:
        raise SpotifyAuthError("Could not reach Spotify's token endpoint") from exc

    if response.is_error:
        log.error("Spotify token request failed: %s %s", response.status_code, response.text)
        message = f"Spotify rejected the token request ({response.status_code})"
        if response.status_code in (400, 401):
            raise SpotifyGrantRejectedError(message)
        raise SpotifyAuthError(message)

    return SpotifyToken.model_validate(response.json())


async def exchange_code_for_token(settings: Settings, code: str) -> SpotifyToken:
    """Trade the one-time authorization `code` for access/refresh tokens."""
    return await _request_token(
        settings,
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.spotify_redirect_uri,
        },
    )


async def refresh_access_token(settings: Settings, refresh_token: str) -> SpotifyToken:
    """Get a new access token. Spotify may also return a new refresh token; if so, keep it."""
    return await _request_token(
        settings,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
