# backend/app/repositories/user_repository.py


from datetime import datetime
from typing import Any

from app.models.tortoise import User


async def upsert_user(
    *,
    spotify_id: str,
    display_name: str | None,
    access_token_encrypted: str,
    refresh_token_encrypted: str | None,
    token_expires_at: datetime,
    scopes: str,
) -> User:
    """Create the user on first login, or refresh their stored tokens on later ones."""
    defaults: dict[str, Any] = {
        "display_name": display_name,
        "access_token": access_token_encrypted,
        "token_expires_at": token_expires_at,
        "scopes": scopes,
    }
    # Spotify may omit the refresh token; never overwrite a stored one with nothing.
    if refresh_token_encrypted is not None:
        defaults["refresh_token"] = refresh_token_encrypted

    user, _created = await User.update_or_create(defaults=defaults, spotify_id=spotify_id)
    return user


async def update_tokens(
    user: User,
    *,
    access_token_encrypted: str,
    refresh_token_encrypted: str | None,
    token_expires_at: datetime,
    scopes: str | None,
) -> User:
    """Store freshly refreshed tokens. A missing refresh token/scopes keeps the stored value."""
    user.access_token = access_token_encrypted
    user.token_expires_at = token_expires_at
    update_fields: list[str] = ["access_token", "token_expires_at", "updated_at"]

    if refresh_token_encrypted is not None:
        user.refresh_token = refresh_token_encrypted
        update_fields.append("refresh_token")

    if scopes:
        user.scopes = scopes
        update_fields.append("scopes")

    await user.save(update_fields=update_fields)
    return user
