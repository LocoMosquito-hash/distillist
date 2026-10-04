# backend/app/api/deps.py


from fastapi import Cookie, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.models.tortoise import User
from app.repositories import session_repository
from app.security import unsign_session_id

SESSION_COOKIE: str = "distillist_session"


async def current_user(
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    settings: Settings = Depends(get_settings),
) -> User:
    """Dependency for routes that require a logged-in user."""
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")

    if session_cookie is None:
        raise unauthorized

    session_id: str | None = unsign_session_id(settings, session_cookie)
    if session_id is None:
        raise unauthorized

    session = await session_repository.get_valid_session(session_id)
    if session is None:
        raise unauthorized

    return session.user
