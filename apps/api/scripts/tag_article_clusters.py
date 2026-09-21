"""Give related articles a shared topic so "Baca juga" can join them.

Topics were written one article at a time -- `sangjit-tionghoa` on one piece,
`sangjit-ceremony` on the next -- so almost no two articles shared one, and
`_related_articles` in app/services/articles.py ranks by shared topics. This adds
a small cluster vocabulary on top of whatever an article already carries.

Additive only: existing topics are kept in place and cluster topics are appended
when missing, so re-running is a no-op. Slugs missing from the database are
reported and skipped, which lets the same file run against a database that does
not have every article yet.

    uv run python scripts/tag_article_clusters.py            # dry run
    uv run python scripts/tag_article_clusters.py --commit
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article

# cluster topic -> article slugs. An article may sit in several clusters; the
# overlap is what ranks it: a sangjit piece shares two topics with another sangjit
# piece but only one with the tea pai article, so sangjit siblings come first.
CLUSTERS: dict[str, list[str]] = {
    "sangjit": [
        "apa-bedanya-acara-sangjit-acara-lamaran-dan-acara-saserahan-dalam-tradisi-tionghoa-yuk-kenali-bedanya-biar-nggak-bingung-lagi",
        "acara-sangjit-makna-tahapan-dan-checklist-lengkap-biar-nggak-panik-pas-hari-h",
        "acara-lamaran-dalam-adat-tionghoa-simbol-cinta-tradisi-dan-persatuan-dua-keluarga",
        "playlist-sangjit-mandarin-hokkien-instrumental",
        "angka-baik-dan-pantangan-pernikahan-tionghoa",
        "sangjit-hokkien-khek-tiociu-kanton-beda-aturan",
    ],
    "adat-tionghoa": [
        "apa-bedanya-acara-sangjit-acara-lamaran-dan-acara-saserahan-dalam-tradisi-tionghoa-yuk-kenali-bedanya-biar-nggak-bingung-lagi",
        "acara-sangjit-makna-tahapan-dan-checklist-lengkap-biar-nggak-panik-pas-hari-h",
        "acara-lamaran-dalam-adat-tionghoa-simbol-cinta-tradisi-dan-persatuan-dua-keluarga",
        "serba-serbi-pernikahan-adat-tionghoa-tradisi-mitos-dan-makna-simbolisnya",
        "10-prosesi-pernikahan-adat-tionghoa-yang-sarat-makna-tetap-hits-di-zaman-now",
        "tea-pai-tradisi-teh-pernikahan-tionghoa-yang-penuh-makna-filosofi",
        "tradisi-cio-tao-ritual-pernikahan-unik-cina-benteng-yang-sarat-makna-dan-filosofi",
        "tradisi-menghias-kamar-pengantin-adat-tionghoa-simbol-cinta-harapan-dan-keberuntungan",
        "menentukan-tanggal-pernikahan-weton-shio",
        "playlist-sangjit-mandarin-hokkien-instrumental",
        "lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik",
        "sungkeman-dan-tea-pai-lagu-pengiring",
        "angka-baik-dan-pantangan-pernikahan-tionghoa",
        "sangjit-hokkien-khek-tiociu-kanton-beda-aturan",
    ],
    "tea-pai": [
        "tea-pai-tradisi-teh-pernikahan-tionghoa-yang-penuh-makna-filosofi",
        "sungkeman-dan-tea-pai-lagu-pengiring",
    ],
    "adat-jawa": [
        "pernikahan-adat-jawa-penuh-filosofi-bukan-sekadar-janji-suci",
        "tradisi-langkahan-jawa-prosesi-menikah-mendahului-kakak-yang-penuh-makna-dan-doa-restu",
        "7-contoh-kata-kata-sungkeman-pernikahan-penuh-haru-untuk-ungkapkan-cinta-ke-orang-tua",
        "makna-janur-kuning-di-pernikahan-dari-simbol-tradisional-sampai-dekorasi-hits-masa-kini",
        "istilah-tahapan-pernikahan-adat-jawa",
        "menentukan-tanggal-pernikahan-weton-shio",
        "lagu-jawa-untuk-pernikahan-gending-campursari",
        "sungkeman-dan-tea-pai-lagu-pengiring",
    ],
    "sungkeman": [
        "7-contoh-kata-kata-sungkeman-pernikahan-penuh-haru-untuk-ungkapkan-cinta-ke-orang-tua",
        "sungkeman-dan-tea-pai-lagu-pengiring",
        "lagu-jawa-untuk-pernikahan-gending-campursari",
    ],
    "lagu-pernikahan": [
        "30-lagu-romantis-untuk-first-dance-wedding-yang-bikin-momen-jadi-unforgettable",
        "30-lagu-indonesia-terbaik-untuk-wedding-yang-bikin-semua-tamu-nyanyi-bareng",
        "musik-hiburan-pernikahan-islami",
        "playlist-sangjit-mandarin-hokkien-instrumental",
        "lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik",
        "lagu-jawa-untuk-pernikahan-gending-campursari",
        "sungkeman-dan-tea-pai-lagu-pengiring",
    ],
    "lagu-mandarin": [
        "playlist-sangjit-mandarin-hokkien-instrumental",
        "lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik",
    ],
    "lamaran": [
        "apa-bedanya-acara-sangjit-acara-lamaran-dan-acara-saserahan-dalam-tradisi-tionghoa-yuk-kenali-bedanya-biar-nggak-bingung-lagi",
        "acara-lamaran-dalam-adat-tionghoa-simbol-cinta-tradisi-dan-persatuan-dua-keluarga",
        "susunan-acara-lamaran-dari-awal-sampai-akhir",
        "tren-seserahan-mas-kawin-2026",
    ],
}


def topics_by_slug() -> dict[str, list[str]]:
    wanted: dict[str, list[str]] = {}
    for topic, slugs in CLUSTERS.items():
        for slug in slugs:
            wanted.setdefault(slug, []).append(topic)
    return wanted


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    args = parser.parse_args()

    changed = missing = 0
    async with AsyncSessionLocal() as session:
        for slug, topics in sorted(topics_by_slug().items()):
            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                print(f"  ! not in database, skipped  {slug}")
                missing += 1
                continue
            current = list(article.topic or [])
            have = {topic.casefold() for topic in current}
            added = [topic for topic in topics if topic not in have]
            if not added:
                continue
            # A new list, not an in-place append: the column is plain JSON, so
            # SQLAlchemy only notices the change when the attribute is reassigned.
            article.topic = current + added
            changed += 1
            print(f"  {'tagged' if args.commit else 'would tag'}  {slug[:60]:<60}  + {', '.join(added)}")
        if args.commit:
            await session.commit()
    await engine.dispose()

    print(f"\n{changed} article(s) {'updated' if args.commit else 'to update'}, {missing} missing")
    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
