"""Command-line interface for spy2ytb."""

import argparse
import sys

from dotenv import load_dotenv

from . import __version__
from .downloader import Downloader
from .spotify import SpotifyClient


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="spy2ytb",
        description="Download Spotify playlists from YouTube with full metadata.",
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "playlists",
        nargs="+",
        metavar="URL",
        help="Spotify playlist URL(s) to download",
    )

    parser.add_argument(
        "-o", "--output",
        default="downloads",
        metavar="DIR",
        help="Output directory (default: downloads)",
    )

    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Re-download tracks even if they already exist",
    )

    args = parser.parse_args(argv)

    try:
        spotify = SpotifyClient()
        downloader = Downloader(output_dir=args.output)

        for url in args.playlists:
            print(f"Fetching playlist: {url}")
            playlist = spotify.get_playlist(url)
            downloader.download_playlist(playlist, skip_existing=not args.no_skip)

        print("== Done downloading all playlists. ==")
        return 0

    except KeyboardInterrupt:
        print("\nAborted.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
