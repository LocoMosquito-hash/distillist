# backend/app/api/spotify.py


from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import current_user
from app.config import Settings, get_settings
from app.integrations.spotify.client import SpotifyApiError
from app.models.tortoise import User
from app.schemas.spotify import NowPlayingOut, PlaylistPageOut
from app.services import spotify_service
from app.services.spotify_service import SpotifyTokenExpiredError

router = APIRouter(prefix="/spotify", tags=["spotify"])


def _spotify_http_error(exc: SpotifyApiError | SpotifyTokenExpiredError) -> HTTPException:
    """Translate Spotify-side failures into meaningful responses for the client."""
    if isinstance(exc, SpotifyTokenExpiredError):
        return HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc))

    if exc.status_code == 401:
        return HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Spotify session expired, please log in again"
        )

    if exc.status_code == 403:
        return HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"{exc} (log in again to grant the required permissions)",
        )

    if exc.status_code == 429:
        headers: dict[str, str] | None = (
            {"Retry-After": str(exc.retry_after)} if exc.retry_after is not None else None
        )
        return HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Spotify rate limit reached, try again later",
            headers=headers,
        )

    return HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc))


@router.get("/playlists", response_model=PlaylistPageOut)
async def playlists(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0, le=100_000),
    user: User = Depends(current_user),
    settings: Settings = Depends(get_settings),
) -> PlaylistPageOut:
    """One page of the logged-in user's playlists, fetched live from Spotify."""
    try:
        return await spotify_service.list_playlists(settings, user, limit, offset)
    except (SpotifyApiError, SpotifyTokenExpiredError) as exc:
        raise _spotify_http_error(exc) from exc


@router.get("/currently-playing", response_model=NowPlayingOut)
async def currently_playing(
    user: User = Depends(current_user),
    settings: Settings = Depends(get_settings),
) -> NowPlayingOut:
    """The track the logged-in user is playing right now, fetched live from Spotify."""
    try:
        return await spotify_service.get_now_playing(settings, user)
    except (SpotifyApiError, SpotifyTokenExpiredError) as exc:
        raise _spotify_http_error(exc) from exc
