# backend/app/services/spotify_service.py


from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.config import Settings
from app.integrations.spotify import client
from app.integrations.spotify.client import SpotifyApiError
from app.integrations.spotify.models import SpotifyPlaylist, SpotifyTrack
from app.models.tortoise import User
from app.schemas.spotify import NowPlayingOut, PlaylistOut, PlaylistPageOut, TrackOut
from app.services import auth_service

T = TypeVar("T")


async def _call_spotify(
    settings: Settings,
    user: User,
    call: Callable[[str], Awaitable[T]],
) -> T:
    """Run a Spotify API call with the user's token, refreshing the token when needed.

    The token is refreshed up front if it is (nearly) expired. If Spotify still answers
    401 (e.g. the token was revoked), refresh once and retry; a second 401 is reported.
    """
    access_token = await auth_service.get_valid_access_token(settings, user)
    try:
        return await call(access_token)
    except SpotifyApiError as exc:
        if exc.status_code != 401:
            raise

    access_token = await auth_service.get_valid_access_token(settings, user, force_refresh=True)
    return await call(access_token)


def _to_playlist_out(playlist: SpotifyPlaylist) -> PlaylistOut:
    return PlaylistOut(
        id=playlist.id,
        name=playlist.name,
        owner_name=(
            (playlist.owner.display_name or playlist.owner.id) if playlist.owner else None
        ),
        track_count=playlist.items.total if playlist.items else None,
        public=playlist.public,
        collaborative=playlist.collaborative,
        spotify_url=playlist.external_urls.spotify,
    )


def _to_track_out(track: SpotifyTrack) -> TrackOut:
    return TrackOut(
        id=track.id,
        name=track.name,
        artists=[artist.name for artist in track.artists],
        album=track.album.name if track.album else None,
        duration_ms=track.duration_ms,
        spotify_url=track.external_urls.spotify,
    )


async def list_playlists(
    settings: Settings, user: User, limit: int, offset: int
) -> PlaylistPageOut:
    """Fetch one page of the user's playlists live from Spotify (nothing is stored)."""
    page = await _call_spotify(
        settings, user, lambda token: client.get_playlists(token, limit, offset)
    )
    return PlaylistPageOut(
        items=[_to_playlist_out(playlist) for playlist in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


async def get_now_playing(settings: Settings, user: User) -> NowPlayingOut:
    """Fetch what the user is playing right now, live from Spotify (nothing is stored)."""
    playing = await _call_spotify(settings, user, client.get_currently_playing)

    if playing is None:
        return NowPlayingOut(is_playing=False, type="none")

    return NowPlayingOut(
        is_playing=playing.is_playing,
        progress_ms=playing.progress_ms,
        type=playing.currently_playing_type,
        track=_to_track_out(playing.item) if playing.item else None,
    )
