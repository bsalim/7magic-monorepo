"""Date, illustrate and publish "Apa Itu Elopement?".

Evergreen explainer, dated 10 October 2026, the day it was written. The site
has no scheduler (the public list filters on status alone), so the article is
imported as a draft and this sets its date and image; `--publish` makes it
live. Legal points and the one vendor price in it were read from their sources
on 2026-10-10. The Go Real Escapes page gives no validity date for its prices,
so re-check them before any update.

  image   Pexels #10920298, a couple on the cliff above Kelingking, Nusa Penida,
          by Vladimir Konoplev. Logged in CREDITS.md and picks.json. Uploaded
          once to R2 at full size; this only registers the object.

Import first (import_markdown_articles.py, then import_article_translations_md.py,
then tag_article_clusters.py), then:

    uv run python scripts/finish_article_2026_10_elopement_bali.py
    uv run python scripts/finish_article_2026_10_elopement_bali.py --commit             # date + image, stays draft
    uv run python scripts/finish_article_2026_10_elopement_bali.py --commit --publish
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
SLUG = "apa-itu-elopement-menikah-berdua-di-bali"
KEY = "articles/2026-10/d6376bcf771a431cb612c510520e8175-apa-itu-elopement-menikah-berdua-di-bali.jpg"
SIZE, WIDTH, HEIGHT = 582593, 1880, 1260
PUBLISHED = datetime(2026, 10, 10, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the article")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        article = await session.scalar(select(Article).where(Article.slug == SLUG))
        if article is None:
            raise SystemExit(f"! not in database: {SLUG} -- run the importers first")

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
