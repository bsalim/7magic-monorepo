"""Upload the home-page slider banners to R2 under ``banners/home/``.

The banners are finished marketing posters -- price, offer and logos baked into
the artwork -- so they go up byte-for-byte, not through the responsive-variant
pipeline, whose re-encode would soften the lettering.

Keys are the source file names, so a re-run overwrites in place and the URLs in
``apps/web/src/lib/components/HeroVenueSearch.svelte`` keep working. A new
banner gets a new file name, and then a new line in that list.

Its own prefix for the same reason as ``email/``: venue and showcase uploads are
swept by scripts that reason about keys, and brand art must not be caught.

    uv run python scripts/upload_home_banners.py --dry-run ~/Downloads/weddingslider/*.jpg
    uv run python scripts/upload_home_banners.py ~/Downloads/weddingslider/*.jpg
"""

from __future__ import annotations

import argparse
import mimetypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.services.storage import R2VenuePhotoStorage  # noqa: E402

PREFIX = "banners/home"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    missing = [path for path in args.files if not path.is_file()]
    if missing:
        for path in missing:
            print(f"source not found: {path}", file=sys.stderr)
        return 1

    settings = get_settings()
    base = settings.r2_public_base_url.rstrip("/")
    storage = R2VenuePhotoStorage(settings)
    if not args.dry_run:
        storage._ensure_configured()

    for path in args.files:
        key = f"{PREFIX}/{path.name}"
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        contents = path.read_bytes()
        print(f"{path.name} ({len(contents):,} bytes) -> {base}/{key}")
        if not args.dry_run:
            # The private helper on purpose; see the module docstring.
            storage._upload_bytes(contents, key, content_type)

    print("dry run -- nothing uploaded" if args.dry_run else "uploaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
