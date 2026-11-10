"""Date, illustrate and publish the Western zodiac compatibility and 2027 sky article.

  10 Nov  Kecocokan Zodiak Pasangan dan Tanggal Menikah 2027
          image   Pexels #7325349, a bride and groom under the Milky Way, by
                  Jonathan Borba. Logged in CREDITS.md and picks.json.
          inline  A zodiac sundial (Pexels #10217880, Chris F) and the Torre
                  dell'Orologio clock in Venice (#32488022, Linh Bo), credited
                  in their captions.

All three were cropped 3:2 and uploaded once to R2 under articles/2026-11/;
this only registers the featured image. It went out on 10 November, ahead
of the batch in finish_article_2026_11.py, whose 3-9 November pieces had not
been published yet. The Year of the Goat and pretty-dates pieces are therefore
named without links in the "Ketika kalender-kalender bertemu" section; once
they are live, link them again and push the body with refresh_article_body.py
and import_article_translations_md.py.

The 2027 dates in the body (Mercury stations, Venus ingresses, eclipses) were
computed in WIB with PyEphem and checked against NASA and almanac tables, so a
copy edit must not round them to the US dates most astrology sites publish.

Import first (import_markdown_articles.py, then import_article_translations_md.py,
then tag_article_clusters.py), then:

    uv run python scripts/finish_article_2026_11_zodiak.py                    # dry run
    uv run python scripts/finish_article_2026_11_zodiak.py --commit           # date + image, stays draft
    uv run python scripts/finish_article_2026_11_zodiak.py --commit --publish
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
SLUG = "kecocokan-zodiak-pasangan-dan-tanggal-menikah-2027"
KEY = "articles/2026-11/53a639b6ffcd4516bbae8400281b8839-kecocokan-zodiak-pasangan-dan-tanggal-menikah-2027.jpg"
SIZE, WIDTH, HEIGHT = 553447, 1880, 1253
PUBLISH_ON = datetime(2026, 11, 10, PUBLISH_HOUR, tzinfo=WIB)


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
