"""Upload desaturated hotel-partner logos to R2 under ``hotel-partners/``.

The logos are third-party trademarks shown as partner/venue credits. Source
files and licence provenance are recorded in the manifest that ships alongside
this script, so we can always answer "where did this logo come from".

Safe to re-run: existing keys are skipped unless --force is passed.

    uv run python scripts/upload_partner_logos.py --src /path/to/bw --dry-run
    uv run python scripts/upload_partner_logos.py --src /path/to/bw
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings

PREFIX = "hotel-partners"
# Immutable content: the filename changes if the artwork does.
CACHE_CONTROL = "public, max-age=31536000, immutable"


def build_client(settings):
    missing = [
        name
        for name, value in (
            ("endpoint url", settings.r2_endpoint_url),
            ("access key id", settings.r2_access_key_id),
            ("secret access key", settings.r2_secret_access_key),
            ("bucket name", settings.r2_bucket_name),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"Object storage is not configured: missing {', '.join(missing)}")

    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}),
    )


def exists(client, bucket: str, key: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="directory of processed .png logos")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="overwrite keys already in R2")
    args = parser.parse_args()

    src = Path(args.src)
    files = sorted(src.glob("*.png"))
    if not files:
        raise SystemExit(f"No .png files in {src}")

    settings = get_settings()
    client = build_client(settings)
    bucket = settings.r2_bucket_name
    base = (settings.r2_public_base_url or "").rstrip("/")

    uploaded, skipped, batch = 0, 0, {}
    for path in files:
        key = f"{PREFIX}/{path.name}"
        url = f"{base}/{key}"
        batch[path.stem] = {"slug": path.stem, "key": key, "url": url}

        if not args.force and not args.dry_run and exists(client, bucket, key):
            print(f"skip    {key}")
            skipped += 1
            continue
        if args.dry_run:
            print(f"WOULD   {key}  ({path.stat().st_size / 1024:.1f} KB)")
            continue

        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=path.read_bytes(),
            ContentType="image/png",
            CacheControl=CACHE_CONTROL,
        )
        print(f"upload  {key}  -> {url}")
        uploaded += 1

    out = Path(__file__).resolve().parent / "partner_logos_manifest.json"
    if not args.dry_run:
        # MERGE, never replace. Uploading a one-logo fix would otherwise wipe the
        # provenance recorded for every other logo, which is the whole point of
        # keeping this file.
        doc = json.loads(out.read_text()) if out.exists() else {}
        if isinstance(doc, list):  # tolerate the original flat-list shape
            doc = {"logos": doc}
        existing = {row["slug"]: row for row in doc.get("logos", [])}
        for slug, row in batch.items():
            existing.setdefault(slug, {}).update(row)
        doc["logos"] = [existing[slug] for slug in sorted(existing)]
        # A slug that now has a logo is no longer missing.
        doc["missing"] = [
            row for row in doc.get("missing", []) if row.get("slug") not in existing
        ]
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print(f"\nmanifest -> {out} ({len(doc['logos'])} logos recorded)")
    print(f"{uploaded} uploaded, {skipped} skipped, {len(files)} total")


if __name__ == "__main__":
    main()
