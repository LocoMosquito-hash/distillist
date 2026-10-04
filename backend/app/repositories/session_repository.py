# backend/app/repositories/session_repository.py


import secrets
from datetime import datetime, timedelta

from tortoise import timezone

from app.models.tortoise import Session, User


async def create_session(user: User, ttl_seconds: int) -> Session:
    """Create a login session with a random, unguessable id."""
    return await Session.create(
        id=secrets.token_urlsafe(32),
        user=user,
        expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
    )


async def get_valid_session(session_id: str) -> Session | None:
    """Return the session (with its user loaded) if it exists and has not expired."""
    now: datetime = timezone.now()
    return (
        await Session.filter(id=session_id, expires_at__gt=now)
        .select_related("user")
        .first()
    )


async def delete_session(session_id: str) -> None:
    await Session.filter(id=session_id).delete()
