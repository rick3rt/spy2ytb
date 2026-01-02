"""Spotify API client wrapper."""

import os
from dataclasses import dataclass

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .metadata import TrackMetadata, key_to_notation, key_to_camelot
from .utils import sanitize_filename


@dataclass
class Track:
    """Represents a track to download."""
    search_query: str
    filename: str
    metadata: TrackMetadata


@dataclass
class Playlist:
    """Represents a Spotify playlist."""
    name: str
    url: str
    tracks: list[Track]


class SpotifyClient:
    """Wrapper around the Spotify API."""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.getenv(
            "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
        )

        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-modify-playback-state user-read-playback-state",
            cache_path=".spotify_cache",
        )

        self._sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlist(self, playlist_url: str) -> Playlist:
        """Fetch a playlist and all its tracks."""
        playlist_data = self._sp.playlist(playlist_url)
        playlist_name = playlist_data["name"]

        # Get all tracks (handle pagination)
        results = self._sp.playlist_items(playlist_url, additional_types=["track"])
        items = results["items"]

        while results["next"]:
            results = self._sp.next(results)
            items.extend(results["items"])

        # Collect track IDs for audio features lookup
        track_ids = []
        valid_items = []
        for item in items:
            track = item["track"]
            if track is None:
                continue
            track_ids.append(track["id"])
            valid_items.append(track)

        # Fetch audio features in batches of 100
        audio_features_map = self._get_audio_features_batch(track_ids)

        tracks = []
        for track in valid_items:
            audio_features = audio_features_map.get(track["id"])
            track_obj = self._parse_track(track, audio_features)
            if track_obj:
                tracks.append(track_obj)

        return Playlist(name=playlist_name, url=playlist_url, tracks=tracks)

    def _get_audio_features_batch(self, track_ids: list[str]) -> dict:
        """Fetch audio features for multiple tracks (batched)."""
        features_map = {}
        # Spotify API allows max 100 tracks per request
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i + 100]
            try:
                features_list = self._sp.audio_features(batch)
                for features in features_list:
                    if features:
                        features_map[features["id"]] = features
            except Exception as e:
                print(f"  Warning: Could not fetch audio features: {e}")
        return features_map

    def _parse_track(self, track: dict, audio_features: dict | None = None) -> Track | None:
        """Parse a track from the Spotify API response."""
        if not track.get("artists"):
            return None

        # Extract all artists
        all_artists = ", ".join([a["name"] for a in track["artists"]])
        primary_artist = track["artists"][0]["name"]

        # Extract album info
        album = track.get("album", {})
        album_name = album.get("name", "")
        album_artist = ", ".join([a["name"] for a in album.get("artists", [])])

        # Get release date (can be YYYY, YYYY-MM, or YYYY-MM-DD)
        release_date = album.get("release_date", "")
        year = release_date[:4] if release_date else ""

        # Get album cover (highest resolution available)
        images = album.get("images", [])
        cover_url = images[0]["url"] if images else None

        # Track and disc numbers
        track_number = track.get("track_number")
        total_tracks = album.get("total_tracks")
        disc_number = track.get("disc_number")

        # Extract audio features (BPM, key)
        bpm = None
        key = ""
        camelot = ""
        if audio_features:
            bpm = audio_features.get("tempo")
            key_num = audio_features.get("key", -1)
            mode = audio_features.get("mode", 0)
            if key_num >= 0:
                key = key_to_notation(key_num, mode)
                camelot = key_to_camelot(key_num, mode)

        title = track["name"]
        search_query = f"{primary_artist} - {title}"
        safe_filename = sanitize_filename(f"{primary_artist} - {title}")

        metadata = TrackMetadata(
            title=title,
            artists=all_artists,
            album=album_name,
            album_artist=album_artist,
            year=year,
            track_number=track_number,
            total_tracks=total_tracks,
            disc_number=disc_number,
            cover_url=cover_url,
            bpm=bpm,
            key=key,
            camelot=camelot,
        )

        return Track(
            search_query=search_query,
            filename=safe_filename,
            metadata=metadata,
        )
