# backend/app/schemas/spotify.py


from pydantic import BaseModel


class PlaylistOut(BaseModel):
    id: str
    name: str
    owner_name: str | None = None
    track_count: int | None = None
    public: bool | None = None
    collaborative: bool = False
    spotify_url: str | None = None  # link back to Spotify (attribution)


class PlaylistPageOut(BaseModel):
    items: list[PlaylistOut]
    total: int
    limit: int
    offset: int


class TrackOut(BaseModel):
    id: str | None = None
    name: str
    artists: list[str]
    album: str | None = None
    duration_ms: int
    spotify_url: str | None = None  # link back to Spotify (attribution)


class NowPlayingOut(BaseModel):
    is_playing: bool
    progress_ms: int | None = None
    # track | episode | ad | unknown | none (nothing is playing)
    type: str
    track: TrackOut | None = None
