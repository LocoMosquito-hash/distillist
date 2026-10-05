# backend/app/services/auth_service.py


import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from cryptography.fernet import InvalidToken
from tortoise import timezone

from app.config import Settings
from app.integrations.spotify.auth import (
    SpotifyGrantRejectedError,
    exchange_code_for_token,
    refresh_access_token,
)
from app.integrations.spotify.client import get_current_user
from app.models.tortoise import Session, User
from app.repositories import session_repository, user_repository
from app.security import decrypt_token, encrypt_token

# Treat a token as expired slightly early so it doesn't lapse mid-request.
_EXPIRY_MARGIN: timedelta = timedelta(seconds=30)

# One lock per user, so simultaneous requests don't all refresh the same token.
# In-process only: fine for a single uvicorn worker (what compose runs today).
_refresh_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


class SpotifyTokenExpiredError(Exception):
    """The user's Spotify credentials can't be used any more; they must log in again."""


async def login_with_spotify(settings: Settings, code: str) -> tuple[User, Session]:
    """Complete a Spotify login: fetch tokens + profile, save the user, open a session.

    May raise SpotifyAuthError / SpotifyApiError; the caller decides how to report them.
    """
    token = await exchange_code_for_token(settings, code)
    spotify_user = await get_current_user(token.access_token)

    expires_at: datetime = timezone.now() + timedelta(seconds=token.expires_in)
    user: User = await user_repository.upsert_user(
        spotify_id=spotify_user.id,
        display_name=spotify_user.display_name,
        access_token_encrypted=encrypt_token(settings, token.access_token),
        refresh_token_encrypted=(
            encrypt_token(settings, token.refresh_token)
            if token.refresh_token is not None
            else None
        ),
        token_expires_at=expires_at,
        scopes=token.scope,
    )
    session: Session = await session_repository.create_session(user, settings.session_ttl_seconds)
    return user, session


async def logout(session_id: str) -> None:
    await session_repository.delete_session(session_id)


def _is_fresh(user: User) -> bool:
    return user.token_expires_at > timezone.now() + _EXPIRY_MARGIN


def _decrypt(settings: Settings, ciphertext: str) -> str:
    try:
        return decrypt_token(settings, ciphertext)
    except InvalidToken as exc:
        raise SpotifyTokenExpiredError(
            "Stored Spotify token is unreadable, please log in again"
        ) from exc


async def get_valid_access_token(
    settings: Settings, user: User, *, force_refresh: bool = False
) -> str:
    """Return a usable (decrypted) access token, refreshing it with Spotify if needed.

    `force_refresh` skips the expiry check; use it when Spotify rejected a token
    that looked valid. Raises SpotifyTokenExpiredError when the user must log in
    again, and SpotifyAuthError if Spotify itself fails during the refresh.
    """
    if not force_refresh and _is_fresh(user):
        return _decrypt(settings, user.access_token)

    async with _refresh_locks[user.id]:
        # Another request may have refreshed while we waited for the lock.
        await user.refresh_from_db()
        if not force_refresh and _is_fresh(user):
            return _decrypt(settings, user.access_token)

        if user.refresh_token is None:
            raise SpotifyTokenExpiredError("Spotify session expired, please log in again")

        try:
            token = await refresh_access_token(settings, _decrypt(settings, user.refresh_token))
        except SpotifyGrantRejectedError as exc:
            raise SpotifyTokenExpiredError(
                "Spotify session expired, please log in again"
            ) from exc

        await user_repository.update_tokens(
            user,
            access_token_encrypted=encrypt_token(settings, token.access_token),
            refresh_token_encrypted=(
                encrypt_token(settings, token.refresh_token)
                if token.refresh_token is not None
                else None
            ),
            token_expires_at=timezone.now() + timedelta(seconds=token.expires_in),
            scopes=token.scope,
        )
        return token.access_token
