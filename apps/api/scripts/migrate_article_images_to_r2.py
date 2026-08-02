"""Move inline article images from the legacy S3 bucket to Cloudflare R2.

Article bodies still embed <img src="https://7magicwedding.s3...">, so the site
depends on the old bucket even though venue photos have moved. This copies each
distinct image into R2 and rewrites the HTML to point at the new URL.

Safe to re-run: an image already present in R2 is not re-uploaded, and HTML that
no longer contains a legacy URL is left untouched, so an interrupted run resumes
cleanly.

    uv run python scripts/migrate_article_images_to_r2.py --dry-run
    uv run python scripts/migrate_article_images_to_r2.py
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.services.storage import safe_filename

LEGACY_HOST = "7magicwedding.s3.ap-southeast-1.amazonaws.com"
IMG_SRC = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

CONTENT_TYPES = {
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
}


def content_type_for(key: str) -> str:
    for suffix, value in CONTENT_TYPES.items():
        if key.lower().endswith(suffix):
            return value
    return "application/octet-stream"


def r2_key_for(url: str) -> str:
    """Map a legacy URL to an R2 key.

    The query string (e.g. ?class=medium) selects a rendition on the old host but
    is not part of the object name, so it is dropped -- otherwise every rendition
    would land under a different key.

    Filenames run through the same sanitiser as uploads, so a legacy name with
    spaces or capitals lands as a tidy lowercase key rather than one needing
    percent-encoding every time it appears in HTML.
    """
    path = unquote(urlparse(url).path).lstrip("/")
    head, _, name = path.rpartition("/")
    tidy = f"{head}/{safe_filename(name)}" if head else safe_filename(name)
    return tidy if tidy.startswith("articles/") else f"articles/legacy/{tidy}"


def build_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        region_name="auto",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    ), settings.r2_bucket_name, settings.r2_public_base_url.rstrip("/")


def list_existing(client, bucket: str) -> set[str]:
    keys: set[str] = set()
    for page in client.get_paginator("list_objects_v2").paginate(
        Bucket=bucket, Prefix="articles/"
    ):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys


async def load_articles() -> list[tuple[int, str]]:
    async with engine.connect() as connection:
        rows = (
            await connection.execute(
                text("SELECT id, content_html FROM articles WHERE trash = false")
            )
        ).all()
    result = [(row.id, row.content_html or "") for row in rows]
    # Dispose before the loop closes: the pool binds to the running loop, and
    # reusing it from a second asyncio.run() fails with "attached to a
    # different loop".
    await engine.dispose()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report the plan, change nothing")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    client, bucket, public_base = build_client()
    articles = asyncio.run(load_articles())

    legacy_urls: set[str] = set()
    for _, html in articles:
        for src in IMG_SRC.findall(html):
            if LEGACY_HOST in src:
                legacy_urls.add(src)

    existing = list_existing(client, bucket)
    # One key can serve several URLs when only the query string differs.
    by_key: dict[str, list[str]] = {}
    for url in legacy_urls:
        by_key.setdefault(r2_key_for(url), []).append(url)

    to_copy = [key for key in by_key if key not in existing]

    affected_articles = sum(
        1 for _, html in articles if any(url in html for url in legacy_urls)
    )

    print(f"articles with legacy images : {affected_articles}")
    print(f"distinct legacy URLs        : {len(legacy_urls)}")
    print(f"distinct R2 keys            : {len(by_key)}")
    print(f"already in R2               : {len(by_key) - len(to_copy)}")
    print(f"to copy                     : {len(to_copy)}")
    print()

    if args.dry_run:
        for key in to_copy[:8]:
            print(f"  would copy  {key}")
        if len(to_copy) > 8:
            print(f"  ... and {len(to_copy) - 8} more")
        print("\nDry run -- nothing uploaded, no HTML rewritten.")
        return 0

    copied = 0
    missing = 0
    failed: list[tuple[str, str]] = []
    lock = Lock()

    def transfer(key: str) -> None:
        nonlocal copied, missing
        source = by_key[key][0]
        try:
            response = httpx.get(source, timeout=60.0, follow_redirects=True)
            if response.status_code == 404:
                with lock:
                    missing += 1
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
                done = copied + missing + len(failed)
                if done % 25 == 0 or done == len(to_copy):
                    print(f"  {done}/{len(to_copy)}  copied={copied} "
                          f"missing={missing} failed={len(failed)}", flush=True)
        except (httpx.HTTPError, ClientError) as error:
            with lock:
                failed.append((key, str(error)[:110]))

    if to_copy:
        print(f"Copying {len(to_copy)} images with {args.workers} workers...", flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(transfer, to_copy))
    else:
        print("Every referenced image is already in R2.")

    # Rewrite HTML only for images that are actually in R2 now, so a failed
    # download never leaves an article pointing at a URL that 404s.
    present = list_existing(client, bucket)
    replacements = {
        url: f"{public_base}/{key}"
        for key, urls in by_key.items()
        if key in present
        for url in urls
    }

    rewritten = 0
    updates: list[tuple[int, str]] = []
    for article_id, html in articles:
        updated = html
        for old, new in replacements.items():
            if old in updated:
                updated = updated.replace(old, new)
        if updated != html:
            updates.append((article_id, updated))

    async def persist() -> None:
        async with engine.begin() as connection:
            for article_id, html in updates:
                await connection.execute(
                    text("UPDATE articles SET content_html = :html WHERE id = :id"),
                    {"id": article_id, "html": html},
                )

    if updates:

        async def persist_and_close() -> None:
            await persist()
            await engine.dispose()

        asyncio.run(persist_and_close())
        rewritten = len(updates)

    print()
    print(f"copied            : {copied}")
    print(f"missing at source : {missing}")
    print(f"failed            : {len(failed)}")
    print(f"articles rewritten: {rewritten}")
    for key, error in failed[:8]:
        print(f"  FAILED {key}: {error}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
