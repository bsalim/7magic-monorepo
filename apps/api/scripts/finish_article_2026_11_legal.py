"""Date, illustrate and publish the four legal-cluster articles.

  25 Nov  Perjanjian kawin setelah menikah
          image   Pexels #14646107, a couple signing documents, by Graziele Rosa.
  25 Nov  Menikah di luar negeri, tinggal di Bali: lapor nikah dan perjanjian kawin
          image   Pexels #7489119, a couple signing papers with an adviser, by Gustavo Fring.
  25 Nov  Harta bersama dan harta bawaan
          image   Pexels #6964107, a couple going through their bills, by Mikhail Nilov.
  25 Nov  Rumah atas nama istri atau suami, milik siapa
          image   Pexels #7579192, a couple holding a house key, by Kindel Media.

Articles #1, #2, #5 and #6 from docs/marketing/2026-11-legal-wedding-article-research.md,
all feeding /perjanjian-pranikah-bali. They go out together rather than one a day
because each links to the others, so no live page is left pointing at a draft.

The same release added /perjanjian-pranikah-bali links to three older prenup
articles. The Markdown importer skips existing slugs, so on prod run
`refresh_article_body.py` for those three before the translations import, or
the English tag-stream check will refuse them.

Each image was cropped 3:2 and uploaded once to R2 under articles/2026-11/; this
only registers it. Credits are in CREDITS.md and picks.json.

    uv run python scripts/import_markdown_articles.py --commit
    uv run python scripts/refresh_article_body.py perjanjian-pranikah-dan-hak-waris-pasangan \
        perjanjian-pranikah-perkawinan-campuran-wna perjanjian-pranikah-pisah-harta-kpr-dan-utang --commit
    uv run python scripts/import_article_translations_md.py --commit
    uv run python scripts/finish_article_2026_11_legal.py                    # dry run
    uv run python scripts/finish_article_2026_11_legal.py --commit           # dates + images, stay draft
    uv run python scripts/finish_article_2026_11_legal.py --commit --publish
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
PUBLISH_ON = datetime(2026, 11, 25, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)


@dataclass(frozen=True)
class Finish:
    slug: str
    key: str
    size: int


ARTICLES = [
    Finish(
        "perjanjian-kawin-setelah-menikah",
        "articles/2026-11/c9d1d00590544219bc340aab20cd3a5a-perjanjian-kawin-setelah-menikah.jpg",
        319542,
    ),
    Finish(
        "menikah-di-luar-negeri-tinggal-di-bali-lapor-nikah-dan-perjanjian-kawin",
        "articles/2026-11/064ba31ca77f4a80bd61be2123660f1d-menikah-di-luar-negeri-tinggal-di-bali-lapor-nikah-dan-perjanjian-kawin.jpg",
        301874,
    ),
    Finish(
        "harta-bersama-dan-harta-bawaan",
        "articles/2026-11/3adc945581644808a3053561285d21a8-harta-bersama-dan-harta-bawaan.jpg",
        271145,
    ),
    Finish(
        "rumah-atas-nama-istri-atau-suami-milik-siapa",
        "articles/2026-11/a1623f7a4ead4e4a97fdc47e53a06f45-rumah-atas-nama-istri-atau-suami-milik-siapa.jpg",
        442957,
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
                print(f"  {would}date   {PUBLISH_ON:%Y-%m-%d %H:%M} UTC")
                if args.commit:
                    article.published_at = PUBLISH_ON

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
