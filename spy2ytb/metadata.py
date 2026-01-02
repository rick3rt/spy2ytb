"""MP3 metadata handling using mutagen."""

import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TDRC, TRCK, TPOS, APIC, TBPM, TKEY, ID3NoHeaderError


# Spotify key numbers to musical keys
# Key: 0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
PITCH_CLASS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def key_to_notation(key: int, mode: int) -> str:
    """Convert Spotify key/mode to musical notation (e.g., 'C major', 'A minor')."""
    if key < 0 or key > 11:
        return ""
    pitch = PITCH_CLASS[key]
    mode_str = "major" if mode == 1 else "minor"
    return f"{pitch} {mode_str}"


def key_to_camelot(key: int, mode: int) -> str:
    """Convert Spotify key/mode to Camelot notation (e.g., '8B', '5A')."""
    if key < 0 or key > 11:
        return ""
    # Camelot wheel mapping
    # Major keys (B): C=8B, G=9B, D=10B, A=11B, E=12B, B=1B, F#=2B, C#=3B, G#=4B, D#=5B, A#=6B, F=7B
    # Minor keys (A): Am=8A, Em=9A, Bm=10A, F#m=11A, C#m=12A, G#m=1A, D#m=2A, A#m=3A, Fm=4A, Cm=5A, Gm=6A, Dm=7A
    camelot_major = {0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B",
                     6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B"}
    camelot_minor = {0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A",
                     6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A"}
    return camelot_major[key] if mode == 1 else camelot_minor[key]


class TrackMetadata:
    """Represents metadata for a single track."""

    def __init__(
        self,
        title: str,
        artists: str,
        album: str = "",
        album_artist: str = "",
        year: str = "",
        track_number: int | None = None,
        total_tracks: int | None = None,
        disc_number: int | None = None,
        total_discs: int | None = None,
        cover_url: str | None = None,
        bpm: float | None = None,
        key: str = "",
        camelot: str = "",
    ):
        self.title = title
        self.artists = artists
        self.album = album
        self.album_artist = album_artist
        self.year = year
        self.track_number = track_number
        self.total_tracks = total_tracks
        self.disc_number = disc_number
        self.total_discs = total_discs
        self.cover_url = cover_url
        self.bpm = bpm
        self.key = key
        self.camelot = camelot

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "artists": self.artists,
            "album": self.album,
            "album_artist": self.album_artist,
            "year": self.year,
            "track_number": self.track_number,
            "total_tracks": self.total_tracks,
            "disc_number": self.disc_number,
            "total_discs": self.total_discs,
            "cover_url": self.cover_url,
            "bpm": self.bpm,
            "key": self.key,
            "camelot": self.camelot,
        }


def set_mp3_metadata(filepath: str, metadata: TrackMetadata) -> None:
    """Set ID3 tags on an MP3 file."""
    try:
        audio = MP3(filepath, ID3=ID3)
    except ID3NoHeaderError:
        audio = MP3(filepath)
        audio.add_tags()

    # Title
    audio.tags.add(TIT2(encoding=3, text=metadata.title))

    # Artist (main artist)
    audio.tags.add(TPE1(encoding=3, text=metadata.artists))

    # Album artist
    if metadata.album_artist:
        audio.tags.add(TPE2(encoding=3, text=metadata.album_artist))

    # Album
    if metadata.album:
        audio.tags.add(TALB(encoding=3, text=metadata.album))

    # Year/Release date
    if metadata.year:
        audio.tags.add(TDRC(encoding=3, text=metadata.year))

    # Track number
    if metadata.track_number:
        track_str = str(metadata.track_number)
        if metadata.total_tracks:
            track_str += f"/{metadata.total_tracks}"
        audio.tags.add(TRCK(encoding=3, text=track_str))

    # Disc number
    if metadata.disc_number:
        disc_str = str(metadata.disc_number)
        if metadata.total_discs:
            disc_str += f"/{metadata.total_discs}"
        audio.tags.add(TPOS(encoding=3, text=disc_str))

    # BPM
    if metadata.bpm:
        audio.tags.add(TBPM(encoding=3, text=str(int(round(metadata.bpm)))))

    # Key (stored as "C major" or Camelot "8B" format in TKEY)
    if metadata.key:
        # Store both notations: "C major (8B)" for maximum compatibility
        key_str = metadata.key
        if metadata.camelot:
            key_str = f"{metadata.key} ({metadata.camelot})"
        audio.tags.add(TKEY(encoding=3, text=key_str))

    # Album cover
    if metadata.cover_url:
        try:
            response = requests.get(metadata.cover_url, timeout=10)
            if response.status_code == 200:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Front cover
                    desc='Cover',
                    data=response.content
                ))
        except Exception as e:
            print(f"  Warning: Could not download album cover: {e}")

    audio.save()
