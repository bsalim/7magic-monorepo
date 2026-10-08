"""Date, illustrate and publish the celebrity run-up articles of 9 October 2026.

Two couples whose weddings are close but not yet held (Song Ji Ho & Kim So Ri,
Asnawi Mangkualam & Yuriska Patricia), plus a schedule of the celebrity
weddings with a confirmed date. They go out before the weddings, while the
announcements are fresh; the wedding-day facts are added to the same articles
afterwards. Every name and date went through an independent verification pass
before import (see each article's Referensi).

Unlike the archive batches, nothing is backdated: `published_at` is the real
go-live moment, 09:00 WIB on 9 October. The site has no scheduler, so import
as drafts, run this with `--commit` (date + image, stays draft), then publish
at that hour with `--commit --publish` (a one-off systemd timer on the server).

  images  The two couple headers are the couples' own pre-wedding photos with
          the credit printed on them by credit_article_photo.py (owner's call,
          2026-10-07): AALIA Studio's press handout for Song and Kim, and Rio
          Motret's shoot as posted by @asnawi_bhr. A printed credit is not a
          licence; if either owner objects, swap the image. The schedule uses
          an openly licensed scene. All three were uploaded to R2 once; this
          only registers them.

    uv run python scripts/finish_article_2026_10_celebrity_runup.py
    uv run python scripts/finish_article_2026_10_celebrity_runup.py --commit
    uv run python scripts/finish_article_2026_10_celebrity_runup.py --commit --publish
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_editorial_calendar import PUBLISH_HOUR, WIB
from sqlalchemy import func, select

from app.models import Article, ArticleImage
from app.core.database import AsyncSessionLocal, engine

MEDIA = "https://media.7magicwedding.com"
PUBLISHED = datetime(2026, 10, 9, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)

# slug -> (storage key of the original, file size, width, height)
BATCH: dict[str, tuple[str, int, int, int]] = {
    "pernikahan-song-ji-ho-kim-so-ri": (
        "articles/2026-10/d8c41249e2a648ae8a388d54158df331-pernikahan-song-ji-ho-kim-so-ri.jpg",
        76213,
        1600,
        840,
    ),
    "pernikahan-asnawi-mangkualam-yuriska-patricia": (
        "articles/2026-10/e218123067f14f268c2e0798055cd6f5-pernikahan-asnawi-mangkualam-yuriska-patricia.jpg",
        263723,
        1600,
        840,
    ),
    # Pexels #31039957 by Đậu Photograph (Pexels License), a wedding-date
    # calendar card. Not a couple: a stock pair at the top of a celebrity list
    # would read as one of the couples in it.
    "jadwal-pernikahan-artis-2026-2027": (
        "articles/2026-10/c28b71ae4ec04d9191a2e05e7717a97f-jadwal-pernikahan-artis-2026-2027.jpg",
        68528,
        1600,
        840,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the articles")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        for slug, (key, size, width, height) in BATCH.items():
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                raise SystemExit(f"! not in database: {slug} -- run the importers first")
            print(slug)

            if article.published_at is None:
                print(f"  {would}date   {PUBLISHED:%Y-%m-%d %H:%M} UTC")
                if args.commit:
                    article.published_at = PUBLISHED

            if args.publish and article.status != "published":
                print(f"  {would}publish")
                if args.commit:
                    article.status = "published"

            has_image = await session.scalar(
                select(func.count())
                .select_from(ArticleImage)
                .where(ArticleImage.article_id == article.id)
            )
            if not has_image:
                print(f"  {would}image  {width}x{height}")
                if args.commit:
                    session.add(
                        ArticleImage(
                            article_id=article.id,
                            filename=f"{slug}.jpg",
                            file_type="jpeg",
                            file_size=size,
                            width=width,
                            height=height,
                            image=key,
                            cdn_url=f"{MEDIA}/{key.removesuffix('.jpg')}_lg_1200w.jpg",
                        )
                    )
        if args.commit:
            await session.commit()
    await engine.dispose()

    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
