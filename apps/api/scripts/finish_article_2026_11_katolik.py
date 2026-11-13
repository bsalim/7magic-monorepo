"""Date, illustrate and publish the Catholic wedding Mass songs article.

  13 Nov  Lagu Pemberkatan Nikah Katolik per Urutan Misa
          image   Pexels #33120490, an open hymnal on a church pew, by Freek
                  Wolsink. Logged in CREDITS.md and picks.json.

Article #1 from docs/marketing/2026-11-wedding-song-keyword-research.md. It was
planned for 12 November and went out a day later. The image was cropped 3:2 and
uploaded once to R2 under articles/2026-11/; this only registers it.

The Puji Syukur numbers come from two online indexes and one choir's list, not
the printed book; Madah Bakti numbers were left out because sources disagree.
Correct a number against the book before adding more.

Import first (import_markdown_articles.py, then import_article_translations_md.py),
then:

    uv run python scripts/finish_article_2026_11_katolik.py                    # dry run
    uv run python scripts/finish_article_2026_11_katolik.py --commit           # date + image, stays draft
    uv run python scripts/finish_article_2026_11_katolik.py --commit --publish
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
SLUG = "lagu-pemberkatan-nikah-katolik-urutan-misa"
KEY = "articles/2026-11/5173347d1e4d4e77a1d4856b9759903e-lagu-pemberkatan-nikah-katolik-urutan-misa.jpg"
SIZE, WIDTH, HEIGHT = 332566, 1880, 1253
PUBLISH_ON = datetime(2026, 11, 13, PUBLISH_HOUR, tzinfo=WIB)


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
