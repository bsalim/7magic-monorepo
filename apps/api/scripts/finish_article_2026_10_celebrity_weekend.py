"""Date, illustrate and publish the celebrity weddings of 16-18 October 2026.

Five weddings held between 20 September and 11 October: Andre Taulany &
Amanda Rigby, Mario Caesar & Givina Lukita, Jerry Andrean & Stefani Horison,
Jang Dong Yoon & Kim Seung Yoon, and Kim Yong Ji. Every name, date and vendor
passed two independent verification passes (brief, then finished ID + EN
drafts); anything resting on one outlet was dropped, not hedged.

They go out one at a time across the weekend instead of together, so each
gets its own moment on the home page and in Discover. `published_at` is the
real go-live time, never backdated. The site has no scheduler: import as
drafts, run this with `--commit` (dates + images, stays draft), then run
`--commit --publish` at each slot. `--publish` only publishes articles whose
slot has passed, so the same command works for every timer and a late or
repeated run is harmless.

  images  Each header is the couple's own wedding photo with the credit
          printed on it by credit_article_photo.py (owner's call,
          2026-10-07). A printed credit is not a licence; if an owner
          objects, swap the image. Kim Yong Ji's header is her solo frame:
          her husband is a private person and stays out of the picture.
          All five were uploaded to R2 once; this only registers them.

    uv run python scripts/finish_article_2026_10_celebrity_weekend.py
    uv run python scripts/finish_article_2026_10_celebrity_weekend.py --commit
    uv run python scripts/finish_article_2026_10_celebrity_weekend.py --commit --publish
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_editorial_calendar import WIB
from sqlalchemy import func, select

from app.models import Article, ArticleImage
from app.core.database import AsyncSessionLocal, engine

MEDIA = "https://media.7magicwedding.com"


def _wib(day: int, hour: int) -> datetime:
    return datetime(2026, 10, day, hour, tzinfo=WIB).astimezone(timezone.utc)


# slug -> (go-live time, storage key of the original, file size, width, height)
BATCH: dict[str, tuple[datetime, str, int, int, int]] = {
    "pernikahan-andre-taulany-amanda-rigby": (
        _wib(16, 19),
        "articles/2026-10/31ecf0e47d7e4983a4a74d1bd8131e0e-pernikahan-andre-taulany-amanda-rigby.jpg",
        235724,
        1600,
        840,
    ),
    "pernikahan-jang-dong-yoon-kim-seung-yoon": (
        _wib(17, 9),
        "articles/2026-10/9416e5f2b65c42ae84b4c7db35dd0e48-pernikahan-jang-dong-yoon-kim-seung-yoon.jpg",
        174163,
        1600,
        840,
    ),
    "pernikahan-jerry-andrean-stefani-horison": (
        _wib(17, 19),
        "articles/2026-10/f361b7ad77364acdafbaa7c427489a90-pernikahan-jerry-andrean-stefani-horison.jpg",
        205482,
        1600,
        840,
    ),
    "pernikahan-kim-yong-ji": (
        _wib(18, 9),
        "articles/2026-10/2830ed1cf17249c086c52ac129457c13-pernikahan-kim-yong-ji.jpg",
        89795,
        1600,
        840,
    ),
    "pernikahan-mario-caesar-givina-lukita": (
        _wib(18, 19),
        "articles/2026-10/44b229fbac9d41f9927af9c89500dc19-pernikahan-mario-caesar-givina-lukita.jpg",
        355204,
        1600,
        840,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument(
        "--publish", action="store_true", help="also publish the articles whose slot has passed"
    )
    args = parser.parse_args()
    would = "" if args.commit else "would "
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        for slug, (go_live, key, size, width, height) in BATCH.items():
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                raise SystemExit(f"! not in database: {slug} -- run the importers first")
            print(slug)

            if article.published_at is None:
                print(f"  {would}date   {go_live:%Y-%m-%d %H:%M} UTC")
                if args.commit:
                    article.published_at = go_live

            if args.publish and article.status != "published":
                if go_live <= now:
                    print(f"  {would}publish")
                    if args.commit:
                        article.status = "published"
                else:
                    print(f"  not yet  (slot {go_live:%Y-%m-%d %H:%M} UTC)")

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
