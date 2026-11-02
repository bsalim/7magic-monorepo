"""Date, illustrate and publish the November 2026 batch: twelve articles, 3-27 November.

  03  Tanggal Cantik Menikah 2027                Pexels #31039957, by Đậu Photograph
  05  Baju Kondangan ke Bali Saat Musim Hujan    Pexels #38730059, by lumenicee
  07  Menikah di Tahun Kambing 2027              Pexels #34169046, by 光术 山影
  09  Menikah Sebelum Ramadan 2027               Pexels #38677845, by Tuti Isnawati
  11  WNI Menikah di Singapura                   Pexels #10351224, by Ilya Lisauskas
  13  Lokasi Nikah di Bali                       Pexels #36407456, by Tom Fisk
  16  Biaya Nikah di Jakarta                     Pexels #17023014, by Matheus Bertelli
  18  Warga Singapura Menikah di Bali            Pexels #11033113, by wayan ricci suandika
  20  Angpao Pernikahan Tionghoa                 Pexels #32322743, by Sóc Năng Động
  23  Menikah dengan WNA di Indonesia            Pexels #14419577, by Reynaldo Yodia
  25  Vow Renewal di Bali                        Pexels #8790770, by Kampus Production
  27  Sangjit dan Guo Da Li                      Pexels #34513733, by vdre

Planned from docs/marketing/2026-11-seo-keyword-research.md (Jakarta, Bali and
Singapore). 14 and 28 November are left free for the celebrity wedding-day
pieces. Images are cropped 3:2, logged in CREDITS.md and picks.json, and were
uploaded once to R2 under articles/2026-11/; this only registers them.

The site has no scheduler, so all twelve are imported as drafts and dated here.
Each is then published on its own morning by a one-off systemd timer that runs
this script with `--commit --publish --only <slug>`. Several articles link to
earlier ones in the batch, so publishing out of order leaves a dead link until
the earlier one is out.

    uv run python scripts/finish_article_2026_11.py                 # dry run
    uv run python scripts/finish_article_2026_11.py --commit        # dates + images, all stay drafts
    uv run python scripts/finish_article_2026_11.py --commit --publish --only <slug>
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
KEYS = "articles/2026-11/"

# slug -> (R2 key under KEYS, bytes, width, height, publish day in November 2026)
ARTICLES = {
    "tanggal-cantik-menikah-2027": (
        "d7996d2cb198425db19a04ea8b0c272d-tanggal-cantik-menikah-2027.jpg",
        130524, 1880, 1253, 3,
    ),
    "baju-kondangan-ke-bali-musim-hujan": (
        "038937652b384373aa33952f195f054b-baju-kondangan-ke-bali-musim-hujan.jpg",
        501537, 1880, 1253, 5,
    ),
    "menikah-tahun-kambing-2027-tahun-janda": (
        "5dd45e9efa91474eb33777700c5026b6-menikah-tahun-kambing-2027-tahun-janda.jpg",
        397546, 1880, 1253, 7,
    ),
    "menikah-sebelum-ramadan-2027-rajab-syakban": (
        "633a6a08907d41e5bf686354468bb6b7-menikah-sebelum-ramadan-2027-rajab-syakban.jpg",
        290558, 1880, 1253, 9,
    ),
    "wni-menikah-di-singapura": (
        "7dae74fdbabb403189c87df659caec9c-wni-menikah-di-singapura.jpg",
        504300, 1880, 1253, 11,
    ),
    "lokasi-nikah-di-bali-uluwatu-nusa-dua-canggu-seminyak-ubud": (
        "88aa1df492584539af0b534839d99f47-lokasi-nikah-di-bali-uluwatu-nusa-dua-canggu-seminyak-ubud.jpg",
        972225, 1880, 1253, 13,
    ),
    "biaya-nikah-di-jakarta": (
        "df743339284b4ddbaf7c515976cccc7a-biaya-nikah-di-jakarta.jpg",
        596330, 1880, 1253, 16,
    ),
    "menikah-di-bali-warga-singapura": (
        "1ec03d41d03841a6900c4a64cb1e9b74-menikah-di-bali-warga-singapura.jpg",
        477970, 1880, 1253, 18,
    ),
    "angpao-pernikahan-tionghoa": (
        "17390eb2d48346e78b5a3b3098dc2f75-angpao-pernikahan-tionghoa.jpg",
        340686, 1880, 1253, 20,
    ),
    "syarat-nikah-dengan-wna-di-indonesia": (
        "67dca5dc9d4c41d5889c714948272e88-syarat-nikah-dengan-wna-di-indonesia.jpg",
        288942, 1880, 1253, 23,
    ),
    "vow-renewal-di-bali-pembaruan-janji-nikah": (
        "bebe119d615741768a2168919233a3e9-vow-renewal-di-bali-pembaruan-janji-nikah.jpg",
        324887, 1880, 1253, 25,
    ),
    "sangjit-dan-guo-da-li-keluarga-jakarta-singapura": (
        "8e93612b8a9e4343961d63556c81632a-sangjit-dan-guo-da-li-keluarga-jakarta-singapura.jpg",
        549474, 1880, 1253, 27,
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
        for slug, (name, size, width, height, day) in ARTICLES.items():
            if args.only and slug != args.only:
                continue
            print(slug)
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                raise SystemExit(f"! not in database: {slug} -- run the importers first")

            if article.published_at is None:
                published = datetime(2026, 11, day, PUBLISH_HOUR, tzinfo=WIB).astimezone(timezone.utc)
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
                key = KEYS + name
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
