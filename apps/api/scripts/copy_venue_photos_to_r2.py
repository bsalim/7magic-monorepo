"""Copy venue photo files from the legacy S3 bucket into Cloudflare R2.

Migration e5f6a7b8c9d0 rewrote every venue photo URL from the S3 host to the R2
host, but the files themselves were never copied -- only ~20 of 1143 photos
exist in R2, so the rest 404 and the site falls back to a placeholder image.
This script closes that gap.

It is safe to re-run: keys already present in R2 are skipped, so an interrupted
run resumes where it left off.

    uv run python scripts/copy_venue_photos_to_r2.py --dry-run
    uv run python scripts/copy_venue_photos_to_r2.py
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine

SOURCE_BASE = "https://7magicwedding.s3.ap-southeast-1.amazonaws.com"

CONTENT_TYPES = {
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def content_type_for(key: str) -> str:
    for suffix, value in CONTENT_TYPES.items():
        if key.lower().endswith(suffix):
            return value
    return "application/octet-stream"


def build_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        region_name="auto",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        # Retries matter here: 9k sequential uploads will hit transient errors.
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    ), settings.r2_bucket_name


def list_existing_keys(client, bucket: str) -> set[str]:
    keys: set[str] = set()
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys


async def referenced_keys() -> set[str]:
    """Every object key the database expects to exist, across both variant sets."""
    async with engine.connect() as connection:
        rows = await connection.execute(
            text("SELECT webp_variants, jpeg_variants FROM venue_photos")
        )
        keys: set[str] = set()
        for row in rows:
            for column in (row.webp_variants, row.jpeg_variants):
                for variant in column or []:
                    key = variant.get("key")
                    if key:
                        keys.add(key)
        return keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report the plan, copy nothing")
    parser.add_argument("--workers", type=int, default=8, help="parallel transfers (default 8)")
    parser.add_argument("--limit", type=int, default=0, help="stop after N objects (0 = all)")
    args = parser.parse_args()

    client, bucket = build_client()

    print("Listing objects already in R2...", flush=True)
    existing = list_existing_keys(client, bucket)

    print("Reading keys referenced by the database...", flush=True)
    wanted = asyncio.run(referenced_keys())

    todo = sorted(wanted - existing)
    if args.limit:
        todo = todo[: args.limit]

    print()
    print(f"  referenced by DB : {len(wanted)}")
    print(f"  already in R2    : {len(wanted & existing)}")
    print(f"  to copy          : {len(todo)}")
    print()

    if args.dry_run:
        for key in todo[:10]:
            print(f"  would copy  {key}")
        if len(todo) > 10:
            print(f"  ... and {len(todo) - 10} more")
        return 0

    if not todo:
        print("Nothing to do -- R2 already has every referenced object.")
        return 0

    copied = 0
    missing_at_source = 0
    failed: list[tuple[str, str]] = []
    lock = Lock()

    def transfer(key: str) -> None:
        nonlocal copied, missing_at_source
        url = f"{SOURCE_BASE}/{key}"
        try:
            response = httpx.get(url, timeout=60.0, follow_redirects=True)
            if response.status_code == 404:
                with lock:
                    missing_at_source += 1
                return
            response.raise_for_status()

            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=response.content,
                ContentType=content_type_for(key),
            )
            with lock:
                copied += 1
                done = copied + missing_at_source + len(failed)
                if done % 100 == 0 or done == len(todo):
                    print(f"  {done}/{len(todo)}  copied={copied}  "
                          f"missing_at_source={missing_at_source}  failed={len(failed)}",
                          flush=True)
        except (httpx.HTTPError, ClientError) as error:
            with lock:
                failed.append((key, str(error)[:120]))

    print(f"Copying with {args.workers} workers...", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(transfer, todo))

    print()
    print(f"copied            : {copied}")
    print(f"missing at source : {missing_at_source}")
    print(f"failed            : {len(failed)}")
    for key, error in failed[:10]:
        print(f"  FAILED {key}: {error}")
    if len(failed) > 10:
        print(f"  ... and {len(failed) - 10} more failures")

    # Re-run to retry failures; a non-zero exit makes that visible to CI/callers.
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
