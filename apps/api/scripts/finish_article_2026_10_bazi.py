"""Date, illustrate and publish the two Ba Zi articles.

"Mengenal Ba Zi" (dated 18 October 2026) introduces the four pillars;
"Kecocokan Pasangan Menurut Ba Zi" (19 October, the day the Ba Zi calculator
launched) explains he hun. Each gets its own date, as every article does. The
site has no scheduler (the public list filters on status alone), so both are
imported as drafts and this sets their dates and images; `--publish` makes them
live. The worked example in the second article was computed with
app/domains/bazi, so it matches what the calculator shows for the same couple.

  images  Pexels #2155501, red calligraphy paper and ink, by Quang Nguyen Vinh;
          Pexels #13400410, a couple in Chinese wedding dress, by Li Yuan.
          Cropped 3:2, logged in CREDITS.md and picks.json, uploaded once to R2
          at full size; this only registers the objects.

Import first (import_markdown_articles.py, then import_article_translations_md.py,
then tag_article_clusters.py), then:

    uv run python scripts/finish_article_2026_10_bazi.py
    uv run python scripts/finish_article_2026_10_bazi.py --commit             # dates + images, stay drafts
    uv run python scripts/finish_article_2026_10_bazi.py --commit --publish
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
    "mengenal-ba-zi-empat-pilar-kelahiran": (
        "articles/2026-10/48711510d5f74620a7f722ba8e559018-mengenal-ba-zi-empat-pilar-kelahiran.jpg",
        299146, 1880, 1253, 18,
    ),
    "kecocokan-pasangan-menurut-ba-zi": (
        "articles/2026-10/9074ea06470e4e4ca96cdd9208491a04-kecocokan-pasangan-menurut-ba-zi.jpg",
        311691, 1733, 1155, 19,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the articles")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        for slug, (key, size, width, height, day) in ARTICLES.items():
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
