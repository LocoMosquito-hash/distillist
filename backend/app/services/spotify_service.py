# backend/app/services/spotify_service.py


from datetime import timedelta

from cryptography.fernet import InvalidToken
from tortoise import timezone

from app.config import Settings
from app.integrations.spotify import client
from app.integrations.spotify.models import SpotifyPlaylist, SpotifyTrack
from app.models.tortoise import User
from app.schemas.spotify import NowPlayingOut, PlaylistOut, PlaylistPageOut, TrackOut
from app.security import decrypt_token

# Treat a token as expired slightly early so it doesn't lapse mid-request.
_EXPIRY_MARGIN: timedelta = timedelta(seconds=30)


class SpotifyTokenExpiredError(Exception):
    """The user's stored Spotify token can't be used; they need to log in again."""


def _get_access_token(settings: Settings, user: User) -> str:
    """Return the user's decrypted access token, or raise if it is expired/unreadable.

    Token refresh isn't implemented yet (planned for the next step).
    """
    if user.token_expires_at <= timezone.now() + _EXPIRY_MARGIN:
        raise SpotifyTokenExpiredError("Spotify session expired, please log in again")
    try:
        return decrypt_token(settings, user.access_token)
    except InvalidToken as exc:
        raise SpotifyTokenExpiredError("Stored Spotify token is unreadable, please log in again") from exc


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
    page = await client.get_playlists(_get_access_token(settings, user), limit, offset)
    return PlaylistPageOut(
        items=[_to_playlist_out(playlist) for playlist in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


async def get_now_playing(settings: Settings, user: User) -> NowPlayingOut:
    """Fetch what the user is playing right now, live from Spotify (nothing is stored)."""
    playing = await client.get_currently_playing(_get_access_token(settings, user))

    if playing is None:
        return NowPlayingOut(is_playing=False, type="none")

    return NowPlayingOut(
        is_playing=playing.is_playing,
        progress_ms=playing.progress_ms,
        type=playing.currently_playing_type,
        track=_to_track_out(playing.item) if playing.item else None,
    )
