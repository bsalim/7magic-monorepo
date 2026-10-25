"""Date, illustrate and publish six pre-wedding celebrity articles, 26-31 October 2026.

  26  Yoon Jong Hoon & Han Eun Seo     (wedding 1 Nov)   Commons, TV10, CC BY 3.0
  27  Lee You Jin & Cha Gyeong Eun     (14 Nov)          Pexels #33449194, Aydin Photography
  28  Ji Ye Eun & Vata                 (12 Dec)          Commons, TV10, CC BY 3.0
  29  Kwak Si Yang & Yoo Jiae          (28 Nov)          Commons, NewsInStar CC BY 3.0 + DarkestDays CC BY 4.0
  30  Abe Hoed & fiancee               (Dec, TBA)        Pexels #15486265, Rhea Jabagat
  31  Gege Elisa & fiance              (TBA)             Pexels #27425992, Pham Hoang Kha

Written before the weddings: the "on the day" sections were left out rather
than published empty (the editor notes survive as comments in the Markdown), so
each article can be extended after its wedding with refresh_article_body.py.
Where no openly licensed photo of the couple exists the header is a generic
Pexels scene, never a copyrighted photo of the couple or a private fiance(e).
Commons headers carry their credit burned in; images were uploaded to R2 once,
this only registers them. The site has no scheduler: each article is published
at 09:00 WIB by a one-off systemd timer running this script with
`--commit --publish --only <slug>`.

    uv run python scripts/finish_article_2026_10_celebrity_prewedding.py
    uv run python scripts/finish_article_2026_10_celebrity_prewedding.py --commit
    uv run python scripts/finish_article_2026_10_celebrity_prewedding.py --commit --publish --only <slug>
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
    "pernikahan-yoon-jong-hoon-han-eun-seo": (
        "articles/2026-10/2e9b77efe92f46bb867cb1bfe8ff1f80-pernikahan-yoon-jong-hoon-han-eun-seo.jpg",
        74951, 1600, 840, 26,
    ),
    "pernikahan-lee-you-jin-cha-gyeong-eun": (
        "articles/2026-10/1875221ab1a446e3b97e364d29900b85-pernikahan-lee-you-jin-cha-gyeong-eun.jpg",
        367205, 1880, 1253, 27,
    ),
    "pernikahan-ji-ye-eun-vata": (
        "articles/2026-10/5320e048bd614411b387305b4a71e5d6-pernikahan-ji-ye-eun-vata.jpg",
        106769, 1600, 840, 28,
    ),
    "pernikahan-kwak-si-yang-yoo-jiae": (
        "articles/2026-10/264755e9c1e04ff9ac08017a4373245b-pernikahan-kwak-si-yang-yoo-jiae.jpg",
        142866, 1600, 840, 29,
    ),
    "pernikahan-abe-hoed": (
        "articles/2026-10/9f35cdf8daf2440885a78bc8521401ec-pernikahan-abe-hoed.jpg",
        217496, 1880, 1253, 30,
    ),
    "pernikahan-gege-elisa": (
        "articles/2026-10/2d5a2263c3a94605a753f21826751319-pernikahan-gege-elisa.jpg",
        523224, 1880, 1253, 31,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the articles")
    parser.add_argument("--only", choices=sorted(ARTICLES), help="act on this article alone")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    async with AsyncSessionLocal() as session:
        for slug, (key, size, width, height, day) in ARTICLES.items():
            if args.only and slug != args.only:
                continue
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
