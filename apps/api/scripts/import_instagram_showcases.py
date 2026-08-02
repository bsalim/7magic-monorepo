"""Import the scraped Instagram grid into `showcases`, with images on R2.

Source is apps/web/static/img/ig/ -- 435 JPEGs plus 7magic-ig-index.csv, pulled
from @7magicorganizer. Every row lands as a draft: the grid mixes real wedding
photos with promo flyers and reel thumbnails, and nothing in the post metadata
separates them reliably, so curation happens in the CMS.

Dates: Instagram only puts a caption in the alt attribute sometimes, so 240 of
435 rows carry a parseable date and 195 do not. The CSV is in grid order, which
is reverse-chronological, so an undated row inherits the date of the nearest
preceding dated row. That is an approximation and it is why these are drafts.

Images are re-keyed by slug rather than the uuid scheme upload_image() uses, so
R2 holds showcases/<slug>.jpg next to its responsive variants.

    uv run python scripts/import_instagram_showcases.py --dry-run
    uv run python scripts/import_instagram_showcases.py
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boto3
from botocore.config import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import get_settings
from app.core.database import engine
from app.models import Showcase
from app.services.images import render_variants, srcset_from

ASSET_DIR = Path(__file__).resolve().parents[3] / "apps/web/static/img/ig"
CSV_PATH = ASSET_DIR / "7magic-ig-index.csv"

DATE_IN_ALT = re.compile(r"on ([A-Z][a-z]+ \d{1,2}, \d{4})")

ID_MONTHS = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}
EN_MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}


def parse_alt_date(alt: str) -> date | None:
    match = DATE_IN_ALT.search(alt or "")
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%B %d, %Y").date()
    except ValueError:
        return None


def build_client():
    settings = get_settings()
    missing = [
        name
        for name, value in (
            ("R2_ENDPOINT_URL", settings.r2_endpoint_url),
            ("R2_ACCESS_KEY_ID", settings.r2_access_key_id),
            ("R2_SECRET_ACCESS_KEY", settings.r2_secret_access_key),
            ("R2_BUCKET_NAME", settings.r2_bucket_name),
            ("R2_PUBLIC_BASE_URL", settings.r2_public_base_url),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"R2 is not configured -- missing: {', '.join(missing)}")

    client = boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        region_name="auto",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )
    return client, settings.r2_bucket_name, settings.r2_public_base_url.rstrip("/")


def plan_rows() -> list[dict]:
    """CSV rows enriched with an inherited date and a unique slug."""
    with CSV_PATH.open() as handle:
        rows = list(csv.DictReader(handle))

    carried: date | None = None
    used: dict[str, int] = {}
    planned: list[dict] = []

    for row in rows:
        parsed = parse_alt_date(row.get("caption_or_alt") or "")
        if parsed:
            carried = parsed
        effective = parsed or carried

        stem = (
            f"wedding-showcase-{effective.isoformat()}"
            if effective
            else "wedding-showcase-undated"
        )
        used[stem] = used.get(stem, 0) + 1
        slug = stem if used[stem] == 1 else f"{stem}-{used[stem]}"

        if effective:
            title_id = f"Wedding Showcase — {effective.day} {ID_MONTHS[effective.month]} {effective.year}"
            title_en = f"Wedding Showcase — {effective.day} {EN_MONTHS[effective.month]} {effective.year}"
        else:
            title_id = title_en = "Wedding Showcase"

        planned.append(
            {
                "filename": row["filename"],
                "slug": slug,
                "title_id": title_id,
                "title_en": title_en,
                "showcase_date": effective,
                "date_exact": parsed is not None,
                "source_ref": f"ig:{row['shortcode']}",
                "post_url": row["post_url"],
                "media_type": row["media_type"],
                "category": row.get("category", ""),
            }
        )
    return planned


def upload_image(client, bucket: str, public_base: str, *, path: Path, slug: str) -> dict:
    """Store the original plus responsive variants under showcases/<slug>."""
    contents = path.read_bytes()
    key = f"showcases/{slug}.jpg"

    client.put_object(Bucket=bucket, Key=key, Body=contents, ContentType="image/jpeg")
    url = f"{public_base}/{key}"

    rendered = render_variants(contents)
    if rendered is None:
        return {"url": url, "storage_key": key, "variants": {"original": url}}

    variants, metadata = rendered
    webp: list[dict] = []
    jpeg: list[dict] = []
    for variant in variants:
        variant_key = f"showcases/{slug}{variant.key_suffix}"
        client.put_object(
            Bucket=bucket,
            Key=variant_key,
            Body=variant.content,
            ContentType=variant.content_type,
        )
        entry = {"cdn_url": f"{public_base}/{variant_key}", "width": variant.width}
        (webp if variant.fmt == "webp" else jpeg).append(entry)

    return {
        # Point the row at the largest jpeg, matching what upload_image() does.
        "url": jpeg[-1]["cdn_url"] if jpeg else url,
        "storage_key": key,
        "variants": {
            "original": url,
            "webp_srcset": srcset_from(webp) if webp else None,
            "jpeg_srcset": srcset_from(jpeg) if jpeg else None,
            "sizes": metadata["sizes_attribute"],
        },
    }


async def existing_refs() -> set[str]:
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        rows = await session.scalars(select(Showcase.source_ref))
        return {ref for ref in rows.all() if ref}


async def insert_rows(records: list[dict]) -> int:
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        for record in records:
            session.add(
                Showcase(
                    public_id=uuid.uuid4(),
                    slug=record["slug"],
                    title_id=record["title_id"],
                    title_en=record["title_en"],
                    body_id=None,
                    body_en=None,
                    showcase_date=record["showcase_date"],
                    status="draft",
                    image_url=record["image_url"],
                    image_storage_key=record["image_storage_key"],
                    image_variants=record["image_variants"],
                    source_ref=record["source_ref"],
                )
            )
        await session.commit()
        return len(records)


async def amain(args) -> int:
    """One event loop for the whole run.

    asyncpg binds its pool to the loop that created it, so separate
    asyncio.run() calls for the read and the write phases blow up with
    "attached to a different loop". The boto3 uploads in between are sync and
    simply block this loop, which is fine for a one-shot script.
    """
    if not CSV_PATH.exists():
        raise SystemExit(f"Index not found: {CSV_PATH}")

    planned = plan_rows()
    already = await existing_refs()
    todo = [row for row in planned if row["source_ref"] not in already]
    if args.limit:
        todo = todo[: args.limit]

    exact = sum(1 for row in todo if row["date_exact"])
    print()
    print(f"  rows in index    : {len(planned)}")
    print(f"  already imported : {len(planned) - len([r for r in planned if r['source_ref'] not in already])}")
    print(f"  to import        : {len(todo)}  ({exact} exact dates, {len(todo) - exact} inherited)")
    print()

    if args.dry_run:
        for row in todo[:8]:
            mark = " " if row["date_exact"] else "~"
            print(f"  {mark} {row['filename']}  ->  showcases/{row['slug']}.jpg")
        if len(todo) > 8:
            print(f"  ... and {len(todo) - 8} more")
        print()
        print("  ~ = date inherited from the nearest preceding dated post")
        return 0

    if not todo:
        print("Nothing to do -- every post is already imported.")
        return 0

    client, bucket, public_base = build_client()

    records: list[dict] = []
    failed: list[tuple[str, str]] = []
    for index, row in enumerate(todo, start=1):
        path = ASSET_DIR / row["filename"]
        if not path.exists():
            failed.append((row["filename"], "file missing"))
            continue
        try:
            result = upload_image(client, bucket, public_base, path=path, slug=row["slug"])
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed.append((row["filename"], str(exc)[:90]))
            continue

        records.append(
            {
                **row,
                "image_url": result["url"],
                "image_storage_key": result["storage_key"],
                "image_variants": result["variants"],
            }
        )
        if index % 25 == 0 or index == len(todo):
            print(f"  uploaded {index}/{len(todo)}", flush=True)

    inserted = await insert_rows(records) if records else 0

    print()
    print(f"  uploaded to R2 : {len(records)}")
    print(f"  rows inserted  : {inserted}")
    if failed:
        print(f"  failed         : {len(failed)}")
        for name, reason in failed[:10]:
            print(f"    {name}: {reason}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report the plan, upload nothing")
    parser.add_argument("--limit", type=int, default=0, help="stop after N rows (0 = all)")
    args = parser.parse_args()

    async def runner() -> int:
        try:
            return await amain(args)
        finally:
            await engine.dispose()

    return asyncio.run(runner())


if __name__ == "__main__":
    raise SystemExit(main())
