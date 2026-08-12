"""Repair the featured images that articles advertise to Google.

`_article_image_url` in app/services/articles.py picks the lowest-id image row for
an article and falls back to a shared 768px placeholder. That feeds the Article
JSON-LD, where Google wants an image at least 1200 pixels wide. Three separate
things were wrong, so this does three passes rather than three scripts:

  migrate  Featured images still live on the legacy S3 bucket, which
           migrate_article_images_to_r2.py never touched -- that script rewrites
           <img> tags inside article bodies, a different surface. Copies each into
           R2 under a sanitised key, which also permanently fixes the URLs whose
           filenames contain spaces and commas -- article 6 advertised a PNG whose
           URL held raw spaces, and re-keying it is the whole fix. Deliberately no
           pass reorders an article's image rows: `_article_image_url` takes the
           lowest id, and promoting a wider sibling would silently change the
           featured image on 15 articles, which is an editorial call and not a
           repair.

  adopt    Creates image rows for articles that have none but do have a
           slug-named file in apps/web/static/img/articles -- the output of
           `fetch_article_images.py --finalise`. This is the step that turns a
           sourced image into something the site actually serves, and it records
           width and height so the report below can tell the truth.

  report   Lists every published article whose featured image is missing or under
           1200px, and writes that list where `fetch_article_images.py --stage`
           can pick it up. No image is invented here: 31 articles have no image in
           the database, on disk or in picks.json, and the honest output is a
           worklist rather than a placeholder.

Safe to re-run. Every pass skips work already done, so an interrupted run resumes.

    uv run python scripts/backfill_article_featured_images.py --dry-run
    uv run python scripts/backfill_article_featured_images.py
    uv run python scripts/backfill_article_featured_images.py --only report
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import ClientError
from PIL import Image
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.services.storage import safe_filename

LEGACY_HOST = "7magicwedding.s3.ap-southeast-1.amazonaws.com"

# Google's Article guidance: images should be at least 1200 pixels wide. Anything
# narrower is reported as unusable rather than merely suboptimal.
MIN_WIDTH = 1200

STATIC_ARTICLES = Path(__file__).resolve().parents[3] / "apps/web/static/img/articles"
WORKLIST = Path(__file__).resolve().parents[3] / "docs/marketing/article-images/needed.json"

CONTENT_TYPES = {
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
}

PASSES = ("migrate", "adopt", "report")


def content_type_for(key: str) -> str:
    for suffix, value in CONTENT_TYPES.items():
        if key.lower().endswith(suffix):
            return value
    return "application/octet-stream"


def r2_key_for(url: str) -> str:
    """Map a legacy URL to an R2 key, matching migrate_article_images_to_r2.py.

    The filename runs through the upload sanitiser, so a legacy name with spaces
    or capitals lands as a tidy key that never needs percent-encoding again --
    which is what was breaking the three URLs containing spaces and commas.
    """
    path = unquote(urlparse(url).path).lstrip("/")
    head, _, name = path.rpartition("/")
    tidy = f"{head}/{safe_filename(name)}" if head else safe_filename(name)
    return tidy if tidy.startswith("articles/") else f"articles/legacy/{tidy}"


def build_client():
    settings = get_settings()
    if not settings.r2_bucket_name or not settings.r2_public_base_url:
        raise SystemExit("R2 is not configured; set R2_* in apps/api/.env before migrating.")
    client = boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        region_name="auto",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )
    return client, settings.r2_bucket_name, settings.r2_public_base_url.rstrip("/")


def existing_keys(client, bucket: str) -> set[str]:
    keys: set[str] = set()
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix="articles/"):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys


def usable(url: str | None) -> bool:
    """Whether a stored value is something a browser can actually fetch."""
    return bool(url) and (url.startswith(("http://", "https://")) or url.startswith("/"))


def encoded(url: str) -> str:
    """A legacy URL made fetchable. The stored values contain raw spaces and
    commas, which no client will request as-is."""
    parts = urlparse(url)
    return parts._replace(path=quote(parts.path)).geturl()


# --------------------------------------------------------------------------- DB


async def fetch_rows() -> list[dict]:
    async with engine.connect() as connection:
        rows = (
            await connection.execute(
                text(
                    """
                    SELECT i.id, i.article_id, i.filename, i.file_type, i.image,
                           i.cdn_url, i.width, i.height, a.slug
                    FROM article_images i
                    JOIN articles a ON a.id = i.article_id
                    WHERE a.status = 'published'
                    ORDER BY i.article_id, i.id
                    """
                )
            )
        ).mappings().all()
    result = [dict(row) for row in rows]
    # Disposed before the loop closes: the pool binds to the running loop, and
    # reusing it from a later asyncio.run() fails with "attached to a different
    # loop".
    await engine.dispose()
    return result


async def fetch_imageless() -> list[dict]:
    async with engine.connect() as connection:
        rows = (
            await connection.execute(
                text(
                    """
                    SELECT a.id, a.slug, a.title_id
                    FROM articles a
                    WHERE a.status = 'published'
                      AND NOT EXISTS (SELECT 1 FROM article_images i WHERE i.article_id = a.id)
                    ORDER BY a.id
                    """
                )
            )
        ).mappings().all()
    result = [dict(row) for row in rows]
    await engine.dispose()
    return result


async def apply_statements(statements: list[tuple[str, dict]]) -> None:
    async with engine.begin() as connection:
        for sql, params in statements:
            await connection.execute(text(sql), params)
    await engine.dispose()


# ------------------------------------------------------------------------ passes


def run_migrate(rows: list[dict], *, dry_run: bool) -> list[tuple[str, dict]]:
    legacy = [row for row in rows if LEGACY_HOST in (row["cdn_url"] or row["image"] or "")]
    if not legacy:
        print("  migrate no featured images left on the legacy bucket")
        return []

    client, bucket, public_base = build_client()
    present = existing_keys(client, bucket)
    statements: list[tuple[str, dict]] = []

    with httpx.Client(timeout=60, follow_redirects=True) as http:
        for row in legacy:
            source = row["cdn_url"] or row["image"]
            key = r2_key_for(source)
            target = f"{public_base}/{key}"

            if key not in present:
                if dry_run:
                    # Recorded even in a dry run: several rows share one image, and
                    # printing it once per row would report four uploads for one
                    # object.
                    present.add(key)
                    print(f"  migrate would upload {key}")
                else:
                    try:
                        response = http.get(encoded(source))
                        response.raise_for_status()
                    except httpx.HTTPError as error:
                        # Reported rather than raised: one unreachable legacy
                        # object must not strand the rest of the batch.
                        print(f"  migrate SKIP  {key}: source unreachable ({error})")
                        continue
                    try:
                        client.put_object(
                            Bucket=bucket,
                            Key=key,
                            Body=response.content,
                            ContentType=content_type_for(key),
                            CacheControl="public, max-age=31536000, immutable",
                        )
                    except ClientError as error:
                        print(f"  migrate SKIP  {key}: upload failed ({error})")
                        continue
                    present.add(key)
                    print(f"  migrate uploaded {key}")

            statements.append(
                (
                    "UPDATE article_images SET cdn_url = :url, image = :key WHERE id = :id",
                    {"url": target, "key": key, "id": row["id"]},
                )
            )
    return statements


def run_adopt(imageless: list[dict], *, dry_run: bool) -> list[tuple[str, dict]]:
    """Wire a sourced file on disk into a row, the shape the working 47 already use."""
    statements: list[tuple[str, dict]] = []
    for article in imageless:
        candidates = sorted(STATIC_ARTICLES.glob(f"{article['slug']}.*"))
        found = next((path for path in candidates if path.suffix.lower() in CONTENT_TYPES), None)
        if found is None:
            continue

        try:
            with Image.open(found) as handle:
                width, height = handle.size
        except OSError as error:
            print(f"  adopt   SKIP  {found.name}: unreadable ({error})")
            continue

        served = f"/img/articles/{found.name}"
        if width < MIN_WIDTH:
            print(f"  adopt   WARN  {found.name} is {width}px, under Google's {MIN_WIDTH}px")

        if dry_run:
            print(f"  adopt   would wire {served} to article {article['id']}")
        else:
            print(f"  adopt   wired {served} to article {article['id']}")

        statements.append(
            (
                """
                INSERT INTO article_images
                    (article_id, filename, file_type, image, cdn_url, width, height)
                VALUES (:article_id, :filename, :file_type, :image, :cdn_url, :width, :height)
                """,
                {
                    "article_id": article["id"],
                    "filename": found.name,
                    "file_type": found.suffix.lstrip("."),
                    "image": served,
                    "cdn_url": served,
                    "width": width,
                    "height": height,
                },
            )
        )
    return statements


def run_report(rows: list[dict], imageless: list[dict], *, dry_run: bool) -> None:
    """Name what still needs a human to choose an image."""
    featured: dict[int, dict] = {}
    for row in rows:
        if row["article_id"] not in featured and (usable(row["cdn_url"]) or usable(row["image"])):
            featured[row["article_id"]] = row

    too_small = [
        {"id": row["article_id"], "slug": row["slug"], "reason": f"{row['width']}px wide"}
        for row in featured.values()
        if row["width"] is not None and row["width"] < MIN_WIDTH
    ]
    missing = [
        {"id": article["id"], "slug": article["slug"], "reason": "no image"}
        for article in imageless
    ]
    needed = sorted(missing + too_small, key=lambda item: item["id"])

    print(f"  report  {len(missing)} articles with no featured image")
    print(f"  report  {len(too_small)} with one narrower than {MIN_WIDTH}px")
    if dry_run:
        # --dry-run promises to change nothing, and the worklist is a file.
        print(f"  report  would write {len(needed)} entries to {WORKLIST.name}")
        return
    WORKLIST.parent.mkdir(parents=True, exist_ok=True)
    WORKLIST.write_text(json.dumps(needed, indent=2) + "\n")
    print(f"  report  wrote {WORKLIST.name} ({len(needed)} entries)")
    print("  report  source them with: uv run python scripts/fetch_article_images.py --stage")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report the plan, change nothing")
    parser.add_argument(
        "--only",
        choices=PASSES,
        action="append",
        help="run only these passes (repeatable); defaults to all four",
    )
    args = parser.parse_args()
    passes = tuple(args.only) if args.only else PASSES

    rows = asyncio.run(fetch_rows())
    imageless = asyncio.run(fetch_imageless())
    print(f"published articles: {len({row['article_id'] for row in rows}) + len(imageless)}")

    statements: list[tuple[str, dict]] = []
    if "migrate" in passes:
        statements += run_migrate(rows, dry_run=args.dry_run)
    if "adopt" in passes:
        statements += run_adopt(imageless, dry_run=args.dry_run)

    if statements and not args.dry_run:
        asyncio.run(apply_statements(statements))
        print(f"applied {len(statements)} statements")
    elif statements:
        print(f"dry run: {len(statements)} statements withheld")
    else:
        print("nothing to change")

    if "report" in passes:
        # Re-read so the report reflects the passes above rather than the state
        # they started from.
        run_report(asyncio.run(fetch_rows()), asyncio.run(fetch_imageless()), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
