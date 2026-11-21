"""Date, illustrate and publish the five "after the Bali wedding" articles.

  21 Nov  Nuanu dan Tabanan setelah menikah di Bali
          image   Pexels #18144498, Tanah Lot from the air, by Patrick Gamelkoorn.
  22 Nov  Ubud dan Kintamani untuk pengantin baru dan tamu
          image   Pexels #36716820, Tegallalang rice terraces, by Tom Fisk.
  23 Nov  Aktivitas bersama tamu: Kuta, Uluwatu, Canggu
          image   Pexels #36407456, the cliffs at Uluwatu Temple, by Tom Fisk.
  24 Nov  Kafe terbaik di Bali
          image   Pexels #2736496, a cappuccino by the sea in Bali, by Content Pixie.
  25 Nov  Wisata setelah menikah di Bali (the hub)
          image   Pexels #4978461, a couple at an infinity pool, by Yan Krukau.

One a day rather than one batch, as the user asked. Each article links only to
series articles dated on or before its own day, and the hub, which links to
all four, goes last, so no live page links to a draft.

There is no scheduler, so `--publish` publishes only the articles whose date
has arrived; a daily timer on prod running `--commit --publish` releases the
next one. Each image was cropped 3:2 and uploaded once to R2 under
articles/2026-11/; this only registers it. Credits are in CREDITS.md and
picks.json.

Import first (import_markdown_articles.py, then import_article_translations_md.py),
then:

    uv run python scripts/finish_article_2026_11_after_wedding.py                    # dry run
    uv run python scripts/finish_article_2026_11_after_wedding.py --commit           # dates + images, stay draft
    uv run python scripts/finish_article_2026_11_after_wedding.py --commit --publish # publish those due
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
    day: int

    @property
    def publish_on(self) -> datetime:
        return datetime(2026, 11, self.day, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)


ARTICLES = [
    Finish(
        "wisata-nuanu-tabanan-setelah-menikah-di-bali",
        "articles/2026-11/3f7317ba317d4fe99e0a5d1473cc7f31-wisata-nuanu-tabanan-setelah-menikah-di-bali.jpg",
        401499,
        21,
    ),
    Finish(
        "ubud-kintamani-untuk-pengantin-baru-dan-tamu-pernikahan",
        "articles/2026-11/7474ab4c38344582ab8326989b9a220b-ubud-kintamani-untuk-pengantin-baru-dan-tamu-pernikahan.jpg",
        936866,
        22,
    ),
    Finish(
        "aktivitas-bersama-tamu-setelah-menikah-di-bali-kuta-uluwatu-canggu",
        "articles/2026-11/0cee2352c809472bb122ae35eb49c67f-aktivitas-bersama-tamu-setelah-menikah-di-bali-kuta-uluwatu-canggu.jpg",
        927857,
        23,
    ),
    Finish(
        "kafe-terbaik-di-bali",
        "articles/2026-11/de00c1a950b14c02b543a961dbde583a-kafe-terbaik-di-bali.jpg",
        274348,
        24,
    ),
    Finish(
        "wisata-setelah-menikah-di-bali",
        "articles/2026-11/301720e9c7714c00ba7793e869609695-wisata-setelah-menikah-di-bali.jpg",
        546228,
        25,
    ),
]


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument(
        "--publish", action="store_true", help="also publish the articles whose date has arrived"
    )
    args = parser.parse_args()
    would = "" if args.commit else "would "
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        for item in ARTICLES:
            print(item.slug)
            article = await session.scalar(select(Article).where(Article.slug == item.slug))
            if article is None:
                raise SystemExit(f"! not in database: {item.slug} -- run the importers first")

            if article.published_at is None:
                print(f"  {would}date   {item.publish_on:%Y-%m-%d %H:%M} UTC")
                if args.commit:
                    article.published_at = item.publish_on

            if args.publish and article.status != "published":
                if item.publish_on <= now:
                    print(f"  {would}publish")
                    if args.commit:
                        article.status = "published"
                else:
                    print(f"  not due until {item.publish_on:%Y-%m-%d %H:%M} UTC")

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
