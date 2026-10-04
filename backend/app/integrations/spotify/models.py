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


class SpotifyExternalUrls(BaseModel):
    spotify: str | None = None


class SpotifyPlaylistOwner(BaseModel):
    id: str
    display_name: str | None = None


class SpotifyPlaylistItemsRef(BaseModel):
    """Link + size of a playlist's contents (`items`; `tracks` is deprecated)."""

    total: int


class SpotifyPlaylist(BaseModel):
    """Simplified playlist object, as returned by `GET /me/playlists`."""

    id: str
    name: str
    owner: SpotifyPlaylistOwner | None = None
    items: SpotifyPlaylistItemsRef | None = None
    public: bool | None = None
    collaborative: bool = False
    external_urls: SpotifyExternalUrls = SpotifyExternalUrls()


class SpotifyPlaylistPage(BaseModel):
    items: list[SpotifyPlaylist]
    total: int
    limit: int
    offset: int


class SpotifyArtist(BaseModel):
    name: str


class SpotifyAlbum(BaseModel):
    name: str


class SpotifyTrack(BaseModel):
    id: str | None = None  # local files have no id
    name: str
    artists: list[SpotifyArtist] = []
    album: SpotifyAlbum | None = None
    duration_ms: int = 0
    external_urls: SpotifyExternalUrls = SpotifyExternalUrls()


class SpotifyCurrentlyPlaying(BaseModel):
    """Playback state from `GET /me/player/currently-playing` (tracks only)."""

    is_playing: bool
    progress_ms: int | None = None
    currently_playing_type: str = "unknown"  # track | episode | ad | unknown
    item: SpotifyTrack | None = None
