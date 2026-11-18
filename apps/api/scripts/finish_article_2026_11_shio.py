"""Date, illustrate and publish the 12-shio compatibility article.

  18 Nov  Kecocokan 12 Shio untuk Menikah
          image   Pexels #16762914, a bride in red Chinese wedding dress under
                  double-happiness lanterns, by 木莲 杨.
          inline  Zodiac statues in Incheon (Pexels #37652651, Nurlan Hasanov)
                  and zodiac lanterns (Pexels #14812073, Ivan Cuesta), already
                  in the body as figures.

All three images were cropped 3:2 and uploaded once to R2 under
articles/2026-11/; this only registers the featured one. Credits are in
CREDITS.md and picks.json.

Import first (import_markdown_articles.py, then import_article_translations_md.py),
then:

    uv run python scripts/finish_article_2026_11_shio.py                    # dry run
    uv run python scripts/finish_article_2026_11_shio.py --commit           # date + image, stays draft
    uv run python scripts/finish_article_2026_11_shio.py --commit --publish
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
SLUG = "kecocokan-12-shio-jodoh-untuk-menikah"
KEY = "articles/2026-11/a4631283505b49b7a1d17a93edc13c32-kecocokan-12-shio-jodoh-untuk-menikah.jpg"
SIZE, WIDTH, HEIGHT = 331040, 1880, 1253
PUBLISH_ON = datetime(2026, 11, 18, PUBLISH_HOUR + 3, tzinfo=WIB)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the article")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        print(SLUG)
        article = await session.scalar(select(Article).where(Article.slug == SLUG))
        if article is None:
            raise SystemExit(f"! not in database: {SLUG} -- run the importers first")

        if article.published_at is None:
            published = PUBLISH_ON.astimezone(timezone.utc)
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
            print(f"  {would}image  {WIDTH}x{HEIGHT}")
            if args.commit:
                session.add(
                    ArticleImage(
                        article_id=article.id,
                        filename=f"{SLUG}.jpg",
                        file_type="jpeg",
                        file_size=SIZE,
                        width=WIDTH,
                        height=HEIGHT,
                        image=KEY,
                        cdn_url=f"{MEDIA}/{KEY.removesuffix('.jpg')}_lg_1200w.jpg",
                    )
                )
        if args.commit:
            await session.commit()
    await engine.dispose()

    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
