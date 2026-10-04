# backend/app/integrations/spotify/models.py


from pydantic import BaseModel


class SpotifyToken(BaseModel):
    """Response of Spotify's token endpoint (authorization code grant)."""

    access_token: str
    token_type: str
    scope: str = ""
    expires_in: int
    refresh_token: str | None = None


class SpotifyUser(BaseModel):
    """The subset of Spotify's `/me` response that distillist uses."""

    id: str
    display_name: str | None = None
