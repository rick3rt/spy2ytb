# spy2ytb

Download Spotify playlists from YouTube with full metadata (album art, artist, title, year, track numbers, etc.).

## Features

- Download entire Spotify playlists as MP3 files
- Automatically searches YouTube for matching tracks
- Embeds full metadata into MP3 files:
  - Title, Artist, Album Artist
  - Album name, Release year
  - Track number, Disc number
  - Album cover art
  - BPM (tempo)
  - Musical key (e.g., "C major (8B)" with Camelot notation)
- Organizes downloads by playlist name
- Skips already downloaded tracks
- Support for multiple playlists in one command

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (required by yt-dlp for audio conversion)
- Spotify Developer account (for API credentials)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/spy2ytb.git
   cd spy2ytb
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Or install as a package:

   ```bash
   pip install -e .
   ```

3. Install ffmpeg if not already installed:

   - **Windows**: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu)

## Configuration

### Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in and click "Create App"
3. Fill in the app details:
   - App name: `spy2ytb` (or any name)
   - Redirect URI: `http://localhost:8888/callback`
4. Once created, note your **Client ID** and **Client Secret**

### Environment Variables

Create a `.env` file in the project root:

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Alternatively, export them as environment variables:

```bash
export SPOTIFY_CLIENT_ID=your_client_id_here
export SPOTIFY_CLIENT_SECRET=your_client_secret_here
export SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

### First Run Authentication

On first run, a browser window will open asking you to authorize the app with Spotify. After authorization, you'll be redirected to localhost - copy the full URL and paste it back into the terminal. The token is cached in `.spotify_cache` for future runs.

## Usage

### Basic Usage

Download a single playlist:

```bash
python main.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Multiple Playlists

Download multiple playlists at once:

```bash
python main.py \
  https://open.spotify.com/playlist/PLAYLIST_1 \
  https://open.spotify.com/playlist/PLAYLIST_2 \
  https://open.spotify.com/playlist/PLAYLIST_3
```

### Custom Output Directory

```bash
python main.py -o ~/Music/Spotify https://open.spotify.com/playlist/...
```

### Force Re-download

By default, existing files are skipped. To re-download everything:

```bash
python main.py --no-skip https://open.spotify.com/playlist/...
```

### Help

```bash
python main.py --help
```

```
usage: spy2ytb [-h] [-V] [-o DIR] [--no-skip] URL [URL ...]

Download Spotify playlists from YouTube with full metadata.

positional arguments:
  URL                   Spotify playlist URL(s) to download

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -o DIR, --output DIR  Output directory (default: downloads)
  --no-skip             Re-download tracks even if they already exist
```

### As an Installed CLI

If installed with `pip install -e .`:

```bash
spy2ytb https://open.spotify.com/playlist/...
```

## Output Structure

Downloads are organized by playlist name:

```
downloads/
├── My Favorite Songs/
│   ├── Artist1 - Song Title.mp3
│   ├── Artist2 - Another Song.mp3
│   └── ...
└── Workout Mix/
    ├── Artist3 - Pump It Up.mp3
    └── ...
```

## DJ Features: BPM and Key

The tool automatically fetches audio analysis data from Spotify and embeds it into each MP3:

- **BPM**: Tempo in beats per minute (rounded to nearest integer)
- **Key**: Musical key in both standard notation and Camelot format

Example: A track in A minor at 128 BPM will have:
- BPM tag: `128`
- Key tag: `A minor (8A)`

The Camelot notation is useful for harmonic mixing - tracks with adjacent Camelot numbers mix well together.

## Troubleshooting

### "No module named 'spy2ytb'"

Make sure you're running from the project root directory, or install the package:

```bash
pip install -e .
```

### Authentication Error

Delete `.spotify_cache` and run again to re-authenticate:

```bash
rm .spotify_cache
python main.py ...
```

### Wrong Song Downloaded

YouTube search isn't perfect. The tool searches for `"Artist - Title"` but may occasionally find covers or wrong versions. Manual verification recommended for important playlists.

### ffmpeg Not Found

Ensure ffmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

## License

MIT
