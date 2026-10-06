// Shapes returned by the backend. Keep in sync with backend/app/schemas/.

export interface User {
  spotify_id: string;
  display_name: string | null;
}

export interface Playlist {
  id: string;
  name: string;
  owner_name: string | null;
  track_count: number | null;
  public: boolean | null;
  collaborative: boolean;
  spotify_url: string | null;
}

export interface PlaylistPage {
  items: Playlist[];
  total: number;
  limit: number;
  offset: number;
}
