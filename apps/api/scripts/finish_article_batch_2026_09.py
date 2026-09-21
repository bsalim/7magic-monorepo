"""Date and illustrate the September 2026 music-and-traditions batch.

`import_markdown_articles.py` creates the six articles but ignores the `date:`
front matter and knows nothing about images, so two things are left over:

  dates   `published_at` from CALENDAR in `apply_editorial_calendar.py`. That
          script is not used directly because its `--status` is applied to every
          slug it knows, which would re-status the whole archive; this touches
          the six slugs below and leaves `status` alone. `_published_at_for`
          keeps a preset date, so publishing later from the CMS preserves it.

  images  One `article_images` row per article, pointing at the featured photo
          already on R2. The photos were uploaded once, through
          `R2VenuePhotoStorage.upload_article_image`, from a development database
          where these articles are ids 170-175 -- hence the `articles/17x/` keys,
          which are just object names and do not have to match the id here.
          Registering the existing objects avoids uploading a second copy per
          environment. Sources and licences are in
          apps/web/static/img/articles/CREDITS.md.

The last four entries are not part of the batch: the three original sangjit
articles and "Serba-Serbi Pernikahan Adat Tionghoa" were published without any
image and showed the venue-deal fallback banner. They already have dates, so
only their image rows are added.

Articles are found by slug, never by id. Safe to re-run: a date already set or an
article that already has an image is left as it is.

    uv run python scripts/finish_article_batch_2026_09.py            # dry run
    uv run python scripts/finish_article_batch_2026_09.py --commit
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_editorial_calendar import CALENDAR, published_at_for
from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article, ArticleImage

MEDIA = "https://media.7magicwedding.com"

# slug -> (storage key of the original, file size, width, height). The served
# URL is the 1200px rendition, which is what the CMS upload endpoint stores too.
IMAGES: dict[str, tuple[str, int, int, int]] = {
    "angka-baik-dan-pantangan-pernikahan-tionghoa": (
        "articles/170/a2bb73ca6fca4ea28bc7f593ea6655f8-angka-baik-dan-pantangan-pernikahan-tionghoa.jpg",
        199347,
        1880,
        1253,
    ),
    "lagu-jawa-untuk-pernikahan-gending-campursari": (
        "articles/171/30ac1de0893c46f49eaf5d54b30056ac-lagu-jawa-untuk-pernikahan-gending-campursari.jpg",
        345916,
        1880,
        1249,
    ),
    "lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik": (
        "articles/172/b5751f79e2234e83a293bb98a2ff63a1-lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik.jpg",
        246395,
        1880,
        1214,
    ),
    "playlist-sangjit-mandarin-hokkien-instrumental": (
        "articles/173/7b2a5f5fe0834098804cb84b47d8e0f3-playlist-sangjit-mandarin-hokkien-instrumental.jpg",
        311688,
        1880,
        1253,
    ),
    "sungkeman-dan-tea-pai-lagu-pengiring": (
        "articles/174/19b923bdbe5242f38861a26bbaaea3a9-sungkeman-dan-tea-pai-lagu-pengiring.jpg",
        281292,
        1880,
        1255,
    ),
    "sangjit-hokkien-khek-tiociu-kanton-beda-aturan": (
        "articles/175/aa90f66e84ac42f39cc280634371ef44-sangjit-hokkien-khek-tiociu-kanton-beda-aturan.jpg",
        287939,
        1880,
        1254,
    ),
    "apa-bedanya-acara-sangjit-acara-lamaran-dan-acara-saserahan-dalam-tradisi-tionghoa-yuk-kenali-bedanya-biar-nggak-bingung-lagi": (
        "articles/12/0cad8113a55749a69b3ea7266cddcfc1-sangjit-12.jpg",
        339961,
        1880,
        1253,
    ),
    "acara-sangjit-makna-tahapan-dan-checklist-lengkap-biar-nggak-panik-pas-hari-h": (
        "articles/13/61aa24d3a7144b08a975217143ddd612-sangjit-13.jpg",
        308774,
        1880,
        1254,
    ),
    "acara-lamaran-dalam-adat-tionghoa-simbol-cinta-tradisi-dan-persatuan-dua-keluarga": (
        "articles/14/201505a552a248c3b54bb2d4ccd4db37-sangjit-14.jpg",
        136239,
        1880,
        1253,
    ),
    "serba-serbi-pernikahan-adat-tionghoa-tradisi-mitos-dan-makna-simbolisnya": (
        "articles/31/0970610ee66e4fcdad59a1e0b1b347a8-serba-serbi-pernikahan-adat-tionghoa-tradisi-mitos-dan-makna-simbolisnya.jpg",
        279992,
        1880,
        1253,
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    missing = 0
    async with AsyncSessionLocal() as session:
        for slug, (key, size, width, height) in sorted(IMAGES.items()):
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                print(f"  ! not in database, skipped  {slug}")
                missing += 1
                continue

            if article.published_at is None:
                when = published_at_for(*CALENDAR[slug])
                print(f"  {would}date   {when:%Y-%m-%d}  {slug}")
                if args.commit:
                    article.published_at = when

            has_image = await session.scalar(
                select(func.count()).select_from(ArticleImage).where(
                    ArticleImage.article_id == article.id
                )
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
