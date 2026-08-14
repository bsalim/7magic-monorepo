"""Upload the 7Magic wordmark to R2 under ``email/`` for use in email headers.

Email clients cannot load a relative path or a data URI reliably, so the logo in
a transactional email has to be an absolute https URL on a host that will still
be serving it years from now. That is the bucket behind
``media.7magicwedding.com``.

Its own ``email/`` prefix on purpose: venue and showcase uploads are swept by
other scripts that reason about keys, and a brand asset must never be caught by
one of those.

The result goes in ``EMAIL_LOGO_URL``. Leave that unset and the header renders a
text wordmark instead -- which is also what a reader with images blocked sees,
so an unset value is a valid choice rather than a broken one.

Safe to re-run: the key is overwritten in place, so the URL never changes.

    uv run python scripts/upload_email_logo.py --dry-run
    uv run python scripts/upload_email_logo.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.services.storage import R2VenuePhotoStorage  # noqa: E402

DEFAULT_SOURCE = (
    Path(__file__).resolve().parents[3] / "apps/web/static/img/7magic-logo-t.png"
)
STORAGE_KEY = "email/7magic-logo.png"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--key", default=STORAGE_KEY)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.src.is_file():
        print(f"source not found: {args.src}", file=sys.stderr)
        return 1

    settings = get_settings()
    public_url = f"{settings.r2_public_base_url.rstrip('/')}/{args.key}"
    contents = args.src.read_bytes()

    print(f"source: {args.src} ({len(contents):,} bytes)")
    print(f"key:    {args.key}")
    print(f"url:    {public_url}")

    if args.dry_run:
        print("dry run -- nothing uploaded")
        return 0

    # Constructed here rather than imported: the only instance in the app lives
    # in the admin router, and importing that from a script drags in every
    # endpoint. The private helpers are deliberate -- the public upload methods
    # all re-encode into responsive variants, which is wrong for a logo that
    # must stay pixel-exact at one known size.
    storage = R2VenuePhotoStorage(settings)
    storage._ensure_configured()
    storage._upload_bytes(contents, args.key, "image/png")
    print("uploaded")
    print(f"\nSet this in the API environment:\n  EMAIL_LOGO_URL={public_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
