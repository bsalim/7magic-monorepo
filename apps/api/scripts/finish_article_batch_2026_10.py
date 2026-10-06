"""Date and illustrate the October 2026 prenup articles, and correct one claim.

`import_markdown_articles.py` creates the three articles but ignores the `date:`
front matter and knows nothing about images; this fills both in, the same way
`finish_article_batch_2026_09.py` did for the previous batch.

  dates   Backdated and staggered (the public list has no scheduler, so a future
          `published_at` would show at once). Only set when empty, so publishing
          later from the CMS keeps them.

  images  One `article_images` row per article, pointing at the featured photo
          already on R2. The photos were uploaded once from a development
          machine through `R2VenuePhotoStorage.upload_image`, under
          `articles/2026-10/`; registering the existing objects avoids a second
          copy per environment. Sources and licences are in
          apps/web/static/img/articles/CREDITS.md; the inheritance article uses
          a frame of the Constitutional Court's own hearing broadcast, not stock.

  fix     "percakapan-keuangan-sebelum-menikah" told readers a prenup must be
          made before the wedding, "bukan sesudahnya". That has been wrong since
          Constitutional Court Decision 69/PUU-XIII/2015 (27 October 2016). The
          importer skips existing slugs, so the corrected Markdown never reaches
          the row; the sentence is replaced in `body_id` and `body_en` here.

Articles are found by slug, never by id. Safe to re-run: a date already set, an
article that already has an image, or a sentence already corrected is left alone.

    uv run python scripts/finish_article_batch_2026_10.py            # dry run
    uv run python scripts/finish_article_batch_2026_10.py --commit
    uv run python scripts/finish_article_batch_2026_10.py --commit --publish

`--publish` also sets the three batch articles to `published`. Import them as
drafts first: an article created as published is stamped with the import time,
and the backdated date above is only applied to an empty `published_at`.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_editorial_calendar import published_at_for
from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article, ArticleImage

MEDIA = "https://media.7magicwedding.com"

# slug -> ((month, day), storage key of the original, file size, width, height).
# The served URL is the 1200px rendition, as for the September batch.
BATCH: dict[str, tuple[tuple[int, int], str, int, int, int]] = {
    "perjanjian-pranikah-pisah-harta-kpr-dan-utang": (
        (9, 24),
        "articles/2026-10/4f15bed358f54877853fd39498d0fdf8-perjanjian-pranikah-pisah-harta-kpr-dan-utang.jpg",
        259586,
        1833,
        1300,
    ),
    "perjanjian-pranikah-perkawinan-campuran-wna": (
        (9, 30),
        "articles/2026-10/3009f605d7c64515a5d53b35e887197f-perjanjian-pranikah-perkawinan-campuran-wna.jpg",
        157526,
        1880,
        1298,
    ),
    "perjanjian-pranikah-dan-hak-waris-pasangan": (
        (10, 5),
        "articles/2026-10/9a623345fd974e0caf65d8b815a5b129-perjanjian-pranikah-dan-hak-waris-pasangan.jpg",
        122691,
        1594,
        954,
    ),
}

FIX_SLUG = "percakapan-keuangan-sebelum-menikah"
# column -> (wrong sentence, replacement)
FIXES: dict[str, tuple[str, str]] = {
    "body_id": (
        "Yang penting diketahui: perjanjian pranikah di Indonesia harus dibuat di hadapan "
        "notaris dan disahkan sebelum tanggal pernikahan berlangsung, bukan sesudahnya.",
        "Yang penting diketahui: perjanjian pranikah di Indonesia dibuat dengan akta notaris. "
        "Sejak putusan Mahkamah Konstitusi tahun 2016, perjanjian ini juga boleh dibuat setelah "
        "menikah, tetapi membuatnya sebelum hari H tetap lebih sederhana karena harta belum "
        "bercampur.",
    ),
    "body_en": (
        "One thing to know: in Indonesia a prenuptial agreement has to be executed before a "
        "notary and finalized before the wedding date, not afterwards.",
        "One thing to know: in Indonesia a prenuptial agreement is made as a notarial deed. "
        "Since a 2016 Constitutional Court decision it can also be made after the wedding, but "
        "signing before the day is still simpler, because nothing has been mixed yet.",
    ),
}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--publish", action="store_true", help="also publish the batch")
    args = parser.parse_args()
    would = "" if args.commit else "would "

    missing = 0
    async with AsyncSessionLocal() as session:
        for slug, ((month, day), key, size, width, height) in sorted(BATCH.items()):
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                print(f"  ! not in database, skipped  {slug}")
                missing += 1
                continue

            if article.published_at is None:
                when = published_at_for(month, day)
                print(f"  {would}date   {when:%Y-%m-%d}  {slug}")
                if args.commit:
                    article.published_at = when

            if args.publish and article.status != "published":
                print(f"  {would}publish  {slug}")
                if args.commit:
                    article.status = "published"

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

        article = await session.scalar(select(Article).where(Article.slug == FIX_SLUG))
        if article is None:
            print(f"  ! not in database, skipped  {FIX_SLUG}")
            missing += 1
        else:
            for column, (wrong, right) in FIXES.items():
                body = getattr(article, column) or ""
                if wrong in body:
                    print(f"  {would}fix    {column}  {FIX_SLUG}")
                    if args.commit:
                        setattr(article, column, body.replace(wrong, right))
                elif right not in body:
                    # Neither sentence: the text was edited in the CMS since.
                    # Leave it for a person rather than guess.
                    print(f"  ! {column} matches neither sentence, left alone  {FIX_SLUG}")

        if args.commit:
            await session.commit()
    await engine.dispose()

    print(f"\n{missing} missing")
    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
