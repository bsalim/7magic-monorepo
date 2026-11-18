"""Date, illustrate and publish three Bali wedding articles together.

  18 Nov  Pemberkatan Nikah Kristen dan Katolik di Bali
          image   Pexels #36298681, a white A-frame chapel facing the sea, by
                  ZhiCheng Zhang.
  18 Nov  Akad Nikah di Bali: KUA, wali, dan venue
          image   Pexels #12900522, two Indonesian marriage books among white
                  flowers, by Rizki Koto.
  18 Nov  Waktu Terbaik Menikah di Bali 2027
          image   Pexels #17754245, a beachside wedding arch under a clear sky
                  in Bali, by Agung Pandit Wiguna.

Articles #5, #6 and #8 from docs/marketing/2026-11-bali-wedding-article-research.md.
They go out on the same day because the best-time article links to the other
two, and a link to a draft is a 404 on the live site. Staggered by an hour so
the listing shows them in a stable order.

Each image was cropped 3:2 and uploaded once to R2 under articles/2026-11/;
this only registers it. Credits are in CREDITS.md and picks.json.

Import first (import_markdown_articles.py, then import_article_translations_md.py),
then:

    uv run python scripts/finish_article_2026_11_bali.py                    # dry run
    uv run python scripts/finish_article_2026_11_bali.py --commit           # date + image, stays draft
    uv run python scripts/finish_article_2026_11_bali.py --commit --publish
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_editorial_calendar import PUBLISH_HOUR, WIB
from sqlalchemy import func, select

from app.models import Article, ArticleImage
from app.core.database import AsyncSessionLocal, engine

MEDIA = "https://media.7magicwedding.com"
WIDTH, HEIGHT = 1880, 1253


@dataclass(frozen=True)
class Finish:
    slug: str
    key: str
    size: int
    hour: int


ARTICLES = [
    Finish(
        "pemberkatan-nikah-kristen-katolik-di-bali",
        "articles/2026-11/f9ef610d317842b28193b7e5bf7f53a6-pemberkatan-nikah-kristen-katolik-di-bali.jpg",
        712285,
        PUBLISH_HOUR,
    ),
    Finish(
        "akad-nikah-di-bali-kua-wali-venue",
        "articles/2026-11/54d616c3ef6043e4b2aaaea5390571d9-akad-nikah-di-bali-kua-wali-venue.jpg",
        256492,
        PUBLISH_HOUR + 1,
    ),
    Finish(
        "waktu-terbaik-menikah-di-bali-2027",
        "articles/2026-11/ea02758a7e5a4f7ea33b42a2f4fda515-waktu-terbaik-menikah-di-bali-2027.jpg",
        295075,
        PUBLISH_HOUR + 2,
    ),
]


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the articles")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        for item in ARTICLES:
            print(item.slug)
            article = await session.scalar(select(Article).where(Article.slug == item.slug))
            if article is None:
                raise SystemExit(f"! not in database: {item.slug} -- run the importers first")

            if article.published_at is None:
                published = datetime(2026, 11, 18, item.hour, tzinfo=WIB).astimezone(timezone.utc)
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
                            filename=f"{item.slug}.jpg",
                            file_type="jpeg",
                            file_size=item.size,
                            width=WIDTH,
                            height=HEIGHT,
                            image=item.key,
                            cdn_url=f"{MEDIA}/{item.key.removesuffix('.jpg')}_lg_1200w.jpg",
                        )
                    )
        if args.commit:
            await session.commit()
    await engine.dispose()

    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
