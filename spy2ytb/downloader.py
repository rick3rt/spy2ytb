"""YouTube downloader using yt-dlp."""

import os
import subprocess

from .metadata import set_mp3_metadata
from .spotify import Playlist, Track
from .utils import sanitize_filename


class Downloader:
    """Downloads tracks from YouTube and applies metadata."""

    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = output_dir

    def download_playlist(self, playlist: Playlist, skip_existing: bool = True) -> None:
        """Download all tracks from a playlist."""
        playlist_dir = os.path.join(self.output_dir, sanitize_filename(playlist.name))
        os.makedirs(playlist_dir, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Playlist: {playlist.name}")
        print(f"Tracks: {len(playlist.tracks)}")
        print(f"Output: {playlist_dir}")
        print(f"{'='*60}\n")

        for i, track in enumerate(playlist.tracks, 1):
            self._download_track(track, playlist_dir, i, len(playlist.tracks), skip_existing)

        print(f"Finished playlist: {playlist.name}\n")

    def download_track(self, track: Track, output_dir: str | None = None, skip_existing: bool = True) -> None:
        """Download a single track."""
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._download_track(track, output_dir, 1, 1, skip_existing)

    def _download_track(
        self,
        track: Track,
        output_dir: str,
        index: int,
        total: int,
        skip_existing: bool,
    ) -> None:
        """Internal method to download a track."""
        print(f"[{index}/{total}] Downloading: {track.search_query}")

        output_path = os.path.join(output_dir, f"{track.filename}.%(ext)s")
        final_path = os.path.join(output_dir, f"{track.filename}.mp3")

        # Skip if already exists
        if skip_existing and os.path.exists(final_path):
            print(f"  Already exists, skipping download...")
            print(f"  Updating metadata...")
            set_mp3_metadata(final_path, track.metadata)
            print(f"  Done.")
            print()
            return

        cmd = [
            "yt-dlp",
            f'ytsearch1:"{track.search_query}"',
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "-f",
            "bestaudio/best",
            "-o",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(final_path):
            print(f"  Download complete, applying metadata...")
            set_mp3_metadata(final_path, track.metadata)
            print(f"  Done.")
        else:
            print(f"  Warning: Download may have failed or file not found")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")

        print()
