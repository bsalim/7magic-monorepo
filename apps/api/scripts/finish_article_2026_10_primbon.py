"""Date, illustrate and publish the primbon week: one article a day, 20-24 October 2026.

  20  Weton Jodoh                           Pexels #11092507, by rangga ispraditya
  21  Larangan Menikah dalam Adat Jawa      Pexels #29194950, by afiful huda
  22  Hari Baik Menikah dalam Tradisi Sunda Pexels #35444559, by Hendi ht23
  23  Dewasa Ayu Pawiwahan                  Pexels #35226130, by Gede Ary
  24  Bulan Baik Menikah 2027               Pexels #6374, by Karolina Grabowska

Facts were researched and source-checked on 19 October 2026. The 2027 month
table comes from the Javanese column of Kemenag's Kalender Hijriah Indonesia
2027, the holidays from the SKB 3 Menteri for 2027. Images are cropped 3:2,
logged in CREDITS.md and picks.json, and uploaded once to R2; this only
registers them.

The site has no scheduler, so all five are imported as drafts and dated here.
Each is then published on its own morning by a one-off systemd timer that runs
this script with `--commit --publish --only <slug>`.

    uv run python scripts/finish_article_2026_10_primbon.py                 # dry run
    uv run python scripts/finish_article_2026_10_primbon.py --commit        # dates + images, all stay drafts
    uv run python scripts/finish_article_2026_10_primbon.py --commit --publish --only <slug>
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

# slug -> (R2 key, bytes, width, height, publish day in October 2026)
ARTICLES = {
    "weton-jodoh-menghitung-kecocokan-pasangan-primbon-jawa": (
        "articles/2026-10/76b2c62d3eac4d33889f223efa196399-weton-jodoh-menghitung-kecocokan-pasangan-primbon-jawa.jpg",
        281207, 1880, 1253, 20,
    ),
    "larangan-menikah-adat-jawa": (
        "articles/2026-10/a2ef393500524c29b2c8c318d12b1814-larangan-menikah-adat-jawa.jpg",
        470574, 1880, 1253, 21,
    ),
    "hari-baik-menikah-tradisi-sunda-paririmbon": (
        "articles/2026-10/6e64a4f4e17444758e42650b6df27f2f-hari-baik-menikah-tradisi-sunda-paririmbon.jpg",
        498124, 1874, 1249, 22,
    ),
    "dewasa-ayu-pawiwahan-hari-baik-menikah-bali": (
        "articles/2026-10/4b7eb62586794c13b5b8ece8b9cafcb6-dewasa-ayu-pawiwahan-hari-baik-menikah-bali.jpg",
        716855, 1880, 1253, 23,
    ),
    "bulan-baik-menikah-2027-kalender-jawa": (
        "articles/2026-10/a05fd5fe1b0d441db90c86cf99f27278-bulan-baik-menikah-2027-kalender-jawa.jpg",
        343347, 1880, 1253, 24,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the articles")
    parser.add_argument("--only", choices=sorted(ARTICLES), help="act on this article alone")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        for slug, (key, size, width, height, day) in ARTICLES.items():
            if args.only and slug != args.only:
                continue
            print(slug)
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                raise SystemExit(f"! not in database: {slug} -- run the importers first")

            if article.published_at is None:
                published = datetime(2026, 10, day, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)
                print(f"  {would}date   {published:%Y-%m-%d %H:%M} UTC")
                if args.commit:
                    article.published_at = published

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
