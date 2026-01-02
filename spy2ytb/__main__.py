"""Allow running as `python -m spy2ytb`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
