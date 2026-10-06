"""Date, illustrate and publish the celebrity wedding batch (October 2026).

Twelve articles: ten on single weddings and two roundups, spread from February
2025 to September 2026. Each `published_at` follows the main wave of coverage
of its wedding at the source sites, so the archive reads as written at the
time rather than in one sitting. Every name and date in these articles went
through two independent verification passes before import; see the article
Referensi lists for the sources.

  dates     Only set when empty, so publishing later from the CMS keeps them.
  images    Pexels scene photos, never photos of the couples, uploaded once to
            R2 under `articles/2026-10/`. Credits in
            apps/web/static/img/articles/CREDITS.md.
  category  "Pernikahan Selebriti" is created by the importer without an
            English slug; this sets `celebrity-weddings` when it is empty.

Import as drafts first, then run this with `--publish`: an article created as
published is stamped with the import time.

    uv run python scripts/finish_article_batch_2026_10_celebrity.py
    uv run python scripts/finish_article_batch_2026_10_celebrity.py --commit --publish
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

from app.models import Article, ArticleCategory, ArticleImage
from app.core.database import AsyncSessionLocal, engine

MEDIA = "https://media.7magicwedding.com"
CATEGORY = ("pernikahan-selebriti", "celebrity-weddings")

# slug -> ((year, month, day), storage key of the original, file size, width, height)
BATCH: dict[str, tuple[tuple[int, int, int], str, int, int, int]] = {
    "pernikahan-angga-yunanda-shenina-cinnamon-bvlgari-bali": (
        (2025, 2, 12),
        "articles/2026-10/b799580f4438477fb93e9cd57e05deab-pernikahan-angga-yunanda-shenina-cinnamon-bvlgari-bali.jpg",
        390415,
        1880,
        1253,
    ),
    "pernikahan-al-ghazali-alyssa-daguise-st-regis-jcc": (
        (2025, 6, 21),
        "articles/2026-10/cf4d770ef6c646b9ae75df600aef3b9e-pernikahan-al-ghazali-alyssa-daguise-st-regis-jcc.jpg",
        446775,
        1880,
        1058,
    ),
    "pernikahan-luna-maya-maxime-bouttier-bali-jakarta": (
        (2025, 8, 1),
        "articles/2026-10/93a71dfe2b274162ba4ca831ba8e7512-pernikahan-luna-maya-maxime-bouttier-bali-jakarta.jpg",
        119352,
        1880,
        1253,
    ),
    "pernikahan-selena-gomez-benny-blanco-santa-barbara": (
        (2025, 10, 1),
        "articles/2026-10/2fedaefadd3c443d91c1b19a5f395c00-pernikahan-selena-gomez-benny-blanco-santa-barbara.jpg",
        348040,
        1880,
        1253,
    ),
    "pernikahan-amanda-manopo-kenny-austin-langham-jakarta": (
        (2025, 10, 12),
        "articles/2026-10/33d66d7aa38b45399c76d2481e1b3876-pernikahan-amanda-manopo-kenny-austin-langham-jakarta.jpg",
        386153,
        1880,
        1253,
    ),
    "pernikahan-brisia-jodie-jonathan-alden-katedral-jakarta": (
        (2025, 12, 8),
        "articles/2026-10/f7235883355f47b38ca4d678d9e9fe30-pernikahan-brisia-jodie-jonathan-alden-katedral-jakarta.jpg",
        361957,
        1880,
        1253,
    ),
    "pernikahan-el-rumi-syifa-hadju-raffles-jakarta": (
        (2026, 4, 28),
        "articles/2026-10/e197c9052e1040e0ad0840945bd1c290-pernikahan-el-rumi-syifa-hadju-raffles-jakarta.jpg",
        192097,
        1880,
        1253,
    ),
    "pernikahan-jennifer-coppen-justin-hubner-bali": (
        (2026, 6, 17),
        "articles/2026-10/2f52f6a9408142fbb29568432bcca70d-pernikahan-jennifer-coppen-justin-hubner-bali.jpg",
        448604,
        1880,
        1253,
    ),
    "pernikahan-dua-lipa-callum-turner-london-sicilia": (
        (2026, 6, 22),
        "articles/2026-10/1977fce94ccb43f388be897cb5e500bf-pernikahan-dua-lipa-callum-turner-london-sicilia.jpg",
        454518,
        1880,
        1253,
    ),
    "pernikahan-taylor-swift-travis-kelce-madison-square-garden": (
        (2026, 7, 6),
        "articles/2026-10/f80b78d91412407f98bf53abb87693e4-pernikahan-taylor-swift-travis-kelce-madison-square-garden.jpg",
        206934,
        1880,
        1253,
    ),
    "pernikahan-selebriti-dunia-2025-2026-ide-yang-bisa-ditiru": (
        (2026, 7, 12),
        "articles/2026-10/e3658aa632024968ba257c0857d5a930-pernikahan-selebriti-dunia-2025-2026-ide-yang-bisa-ditiru.jpg",
        358096,
        1880,
        1253,
    ),
    "pernikahan-artis-indonesia-2025-2026-tren-yang-bisa-ditiru": (
        (2026, 9, 10),
        "articles/2026-10/ce8c5a9d770046e5b798fa1e24cd9d6b-pernikahan-artis-indonesia-2025-2026-tren-yang-bisa-ditiru.jpg",
        391632,
        1880,
        1255,
    ),
}


def published_at(year: int, month: int, day: int) -> datetime:
    # apply_editorial_calendar.published_at_for is fixed to 2026; this batch
    # reaches back into 2025.
    return datetime(year, month, day, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the batch")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    missing = 0
    async with AsyncSessionLocal() as session:
        slug_id, slug_en = CATEGORY
        category = await session.scalar(
            select(ArticleCategory).where(ArticleCategory.category_slug == slug_id)
        )
        if category is None:
            print(f"  ! category {slug_id} not in database")
        elif not category.category_slug_en:
            print(f"  {would}category  {slug_id} -> {slug_en}")
            if args.commit:
                category.category_slug_en = slug_en

        for slug, ((year, month, day), key, size, width, height) in BATCH.items():
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                print(f"  ! not in database, skipped  {slug}")
                missing += 1
                continue

            if article.published_at is None:
                when = published_at(year, month, day)
                print(f"  {would}date   {when:%Y-%m-%d}  {slug}")
                if args.commit:
                    article.published_at = when

            if args.publish and article.status != "published":
                print(f"  {would}publish  {slug}")
                if args.commit:
                    article.status = "published"

            has_image = await session.scalar(
                select(func.count())
                .select_from(ArticleImage)
                .where(ArticleImage.article_id == article.id)
            )
            if not has_image:
                print(f"  {would}image  {width}x{height}  {slug}")
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

    print(f"\n{missing} missing")
    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
