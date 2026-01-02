import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# Spotify settings
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
)
SPOTIFY_PLAYLIST_URI = os.getenv("SPOTIFY_PLAYLIST_URI", "")
SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state"


# spotify
auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE,
    cache_path=".spotify_cache",
)

sp = spotipy.Spotify(auth_manager=auth_manager)

playlist_url = (
    "https://open.spotify.com/playlist/5jgNnhRzaBRdml8h1dF8GQ?si=649667b19854450a"
)
results = sp.playlist_items(playlist_url, additional_types=["track"])

tracks = []
for item in results["items"]:
    track = item["track"]
    if track is None:
        continue
    artist = track["artists"][0]["name"]
    title = track["name"]
    query = f"{artist} - {title}"
    tracks.append(query)


for q in tracks:
    print(f"Searching: {q}")
    cmd = [
        "yt-dlp",
        f'ytsearch1:"{q}"',
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-f",
        "bestaudio/best",
        "-o",
        "downloads/%(title)s.%(ext)s",
    ]
    print(" ".join(cmd))

    subprocess.run(cmd)
    print("\n")

print("== Done downloading all tracks. ==")
