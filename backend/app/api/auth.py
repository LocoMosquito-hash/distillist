# backend/app/api/auth.py


import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.config import Settings, get_settings
from app.integrations.spotify.auth import (
    SpotifyAuthError,
    build_authorize_url,
    exchange_code_for_token,
)
from app.integrations.spotify.client import SpotifyApiError, get_current_user

router = APIRouter(prefix="/auth/spotify", tags=["auth"])

STATE_COOKIE: str = "spotify_oauth_state"
STATE_COOKIE_MAX_AGE: int = 600  # seconds the user has to finish logging in


@router.get("/login")
async def login(settings: Settings = Depends(get_settings)) -> RedirectResponse:
    """Send the browser to Spotify's login/consent page."""
    state: str = secrets.token_urlsafe(32)
    response = RedirectResponse(
        url=build_authorize_url(settings, state),
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        key=STATE_COOKIE,
        value=state,
        max_age=STATE_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/callback")
async def callback(
    response: Response,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    state_cookie: str | None = Cookie(default=None, alias=STATE_COOKIE),
    settings: Settings = Depends(get_settings),
) -> dict[str, str | None]:
    """Spotify redirects back here after the user accepts or denies access."""
    if error is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Spotify authorization failed: {error}")

    if code is None or state is None or state_cookie is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing code or state")

    if not secrets.compare_digest(state, state_cookie):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid state")

    try:
        token = await exchange_code_for_token(settings, code)
        user = await get_current_user(token.access_token)
    except (SpotifyAuthError, SpotifyApiError) as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    response.delete_cookie(STATE_COOKIE)

    # Tokens are intentionally not returned or stored yet (that's the next step).
    return {"spotify_id": user.id, "display_name": user.display_name}
