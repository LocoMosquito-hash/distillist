# backend/app/services/auth_service.py


from datetime import datetime, timedelta

from tortoise import timezone

from app.config import Settings
from app.integrations.spotify.auth import exchange_code_for_token
from app.integrations.spotify.client import get_current_user
from app.models.tortoise import Session, User
from app.repositories import session_repository, user_repository
from app.security import encrypt_token


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
