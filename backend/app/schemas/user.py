# backend/app/schemas/user.py


from pydantic import BaseModel


class UserOut(BaseModel):
    """What the API reveals about the logged-in user (never tokens)."""

    spotify_id: str
    display_name: str | None = None
