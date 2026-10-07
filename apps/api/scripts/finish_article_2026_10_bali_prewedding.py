"""Date, illustrate and publish "Lokasi Prewedding Unik di Bali".

Evergreen, dated 8 October 2026: the day after its Singapore sibling, and the
day it goes live. The site has no scheduler (the public list filters on status
alone), so the article is imported as a draft and a one-off systemd timer on
the server runs this with `--commit --publish` at 09:00 WIB that morning. Fees
and rules in it were read from official sources on 2026-10-07; several Bali
site fees have no official page, which the article says, so re-check them
before any update.

  image   A Wikimedia Commons photo, not Pexels, so it is not in CREDITS.md
          (fetch_article_images.py --finalise rebuilds that file from Pexels
          picks alone and would drop it). Jatiluwih rice terraces by Paxson
          Woelber, CC BY-SA 4.0:
          https://commons.wikimedia.org/wiki/File:Rice_fields_at_Jatiluwih._Bali,_Indonesia.JPG
          Cropped to 1.9:1 with the credit printed on it by
          credit_article_photo.py; under CC BY-SA the crop carries the same
          licence. The article's Referensi repeats the credit with links.
          Uploaded once to R2; this only registers the object.

Import first (import_markdown_articles.py, then import_article_translations_md.py,
then tag_article_clusters.py), then:

    uv run python scripts/finish_article_2026_10_bali_prewedding.py
    uv run python scripts/finish_article_2026_10_bali_prewedding.py --commit             # date + image, stays draft
    uv run python scripts/finish_article_2026_10_bali_prewedding.py --commit --publish
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
SLUG = "lokasi-prewedding-unik-bali"
KEY = "articles/2026-10/939945c212d840c3a81cea306d635979-lokasi-prewedding-unik-bali.jpg"
SIZE, WIDTH, HEIGHT = 539612, 1600, 840
PUBLISHED = datetime(2026, 10, 8, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)


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
