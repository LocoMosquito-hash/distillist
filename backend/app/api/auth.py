# backend/app/api/auth.py


import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.api.deps import SESSION_COOKIE, current_user
from app.config import Settings, get_settings
from app.integrations.spotify.auth import (
    SpotifyAuthError,
    build_authorize_url,
)
from app.integrations.spotify.client import SpotifyApiError
from app.models.tortoise import User
from app.schemas.user import UserOut
from app.security import sign_session_id, unsign_session_id
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE: str = "spotify_oauth_state"
STATE_COOKIE_MAX_AGE: int = 600  # seconds the user has to finish logging in


@router.get("/spotify/login")
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


@router.get("/spotify/callback", response_model=UserOut)
async def callback(
    response: Response,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    state_cookie: str | None = Cookie(default=None, alias=STATE_COOKIE),
    settings: Settings = Depends(get_settings),
) -> UserOut:
    """Spotify redirects back here after the user accepts or denies access."""
    if error is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Spotify authorization failed: {error}")

    if code is None or state is None or state_cookie is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing code or state")

    if not secrets.compare_digest(state, state_cookie):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid state")

    try:
        user, session = await auth_service.login_with_spotify(settings, code)
    except (SpotifyAuthError, SpotifyApiError) as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    response.delete_cookie(STATE_COOKIE)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=sign_session_id(settings, session.id),
        max_age=settings.session_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.environment != "dev",
    )

    return UserOut(spotify_id=user.spotify_id, display_name=user.display_name)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)) -> UserOut:
    """Return the currently logged-in user."""
    return UserOut(spotify_id=user.spotify_id, display_name=user.display_name)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    settings: Settings = Depends(get_settings),
) -> Response:
    """End the current session and clear the cookie."""
    if session_cookie is not None:
        session_id: str | None = unsign_session_id(settings, session_cookie)
        if session_id is not None:
            await auth_service.logout(session_id)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(SESSION_COOKIE)
    return response
