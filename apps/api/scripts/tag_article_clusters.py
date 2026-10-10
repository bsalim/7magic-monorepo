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
    # Doubles as a display switch: the article page shows the banner for the
    # /perjanjian-pranikah landing page on anything carrying this topic.
    "perjanjian-pranikah": [
        "perjanjian-pranikah-panduan-lengkap",
        "perjanjian-pranikah-pisah-harta-kpr-dan-utang",
        "perjanjian-pranikah-perkawinan-campuran-wna",
        "perjanjian-pranikah-dan-hak-waris-pasangan",
        "percakapan-keuangan-sebelum-menikah",
        # Written in the CMS, already carried the topic before this cluster.
        "perjanjian-pranikah-pro-kontra-tren-dan-realita-untuk-pasangan-millennial",
    ],
    # Celebrity weddings: the shared topic links the batch, the sub-topics keep
    # "Baca juga" on the same side of the Indonesian/international split.
    "pernikahan-selebriti": [
        "pernikahan-angga-yunanda-shenina-cinnamon-bvlgari-bali",
        "pernikahan-luna-maya-maxime-bouttier-bali-jakarta",
        "pernikahan-al-ghazali-alyssa-daguise-st-regis-jcc",
        "pernikahan-amanda-manopo-kenny-austin-langham-jakarta",
        "pernikahan-brisia-jodie-jonathan-alden-katedral-jakarta",
        "pernikahan-el-rumi-syifa-hadju-raffles-jakarta",
        "pernikahan-jennifer-coppen-justin-hubner-bali",
        "pernikahan-artis-indonesia-2025-2026-tren-yang-bisa-ditiru",
        "pernikahan-selena-gomez-benny-blanco-santa-barbara",
        "pernikahan-dua-lipa-callum-turner-london-sicilia",
        "pernikahan-taylor-swift-travis-kelce-madison-square-garden",
        "pernikahan-selebriti-dunia-2025-2026-ide-yang-bisa-ditiru",
        # Run-up pieces of 9 October 2026, and the schedule that spans both sides.
        "pernikahan-song-ji-ho-kim-so-ri",
        "pernikahan-asnawi-mangkualam-yuriska-patricia",
        "jadwal-pernikahan-artis-2026-2027",
    ],
    "pernikahan-artis-indonesia": [
        "pernikahan-angga-yunanda-shenina-cinnamon-bvlgari-bali",
        "pernikahan-luna-maya-maxime-bouttier-bali-jakarta",
        "pernikahan-al-ghazali-alyssa-daguise-st-regis-jcc",
        "pernikahan-amanda-manopo-kenny-austin-langham-jakarta",
        "pernikahan-brisia-jodie-jonathan-alden-katedral-jakarta",
        "pernikahan-el-rumi-syifa-hadju-raffles-jakarta",
        "pernikahan-jennifer-coppen-justin-hubner-bali",
        "pernikahan-artis-indonesia-2025-2026-tren-yang-bisa-ditiru",
        "pernikahan-asnawi-mangkualam-yuriska-patricia",
    ],
    "pernikahan-selebriti-dunia": [
        "pernikahan-selena-gomez-benny-blanco-santa-barbara",
        "pernikahan-dua-lipa-callum-turner-london-sicilia",
        "pernikahan-taylor-swift-travis-kelce-madison-square-garden",
        "pernikahan-selebriti-dunia-2025-2026-ide-yang-bisa-ditiru",
        "pernikahan-song-ji-ho-kim-so-ri",
    ],
    # Older slugs say "singapore", newer ones "singapura"; both are the same cluster.
    "menikah-di-singapura": [
        "lokasi-prewedding-unik-singapura",
        "7-venue-rooftop-paling-instagramable-di-singapore-untuk-akad-resepsi-view-marina-bay-city-lights-bikin-makin-syahdu",
        "nikah-bergaya-vintage-ala-kolonial-ini-3-venue-heritage-di-singapore-yang-super-elegan-instagramable",
        "nikah-di-private-space-ini-venue-eksklusif-ala-private-villa-rooftop-wedding-di-singapore",
        "nikah-di-tengah-kota-ini-dia-3-venue-wedding-strategis-dekat-mrt-di-singapore-anti-ribet-buat-tamu-lokal-internasional",
        "nikah-outdoor-di-tengah-alam-ini-5-garden-wedding-venue-paling-romantis-di-singapore",
        "sunset-wedding-vibes-2-venue-tepi-pantai-marina-paling-romantis-di-singapore",
        "venue-halal-friendly-di-singapore-tempat-akad-resepsi-sekaligus-yang-nyaman-untuk-semua-tamu-muslim",
        "mau-nikah-di-singapura-ini-10-hotel-bintang-5-paling-hits-buat-wedding-mewah-elegan",
        "nikah-intimate-gak-harus-mahal-8-venue-micro-wedding-super-aesthetic-di-tengah-kota-singapura",
        "tradisi-pernikahan-multietnis-di-singapura",
    ],
    "menikah-di-bali": [
        "apa-itu-elopement-menikah-berdua-di-bali",
        "lokasi-prewedding-unik-bali",
        "menikah-di-bali-budget-masuk-akal",
        "nikah-hemat-di-bali-ini-dia-3-venue-wedding-budget-di-bawah-50-juta-yang-tetap-estetik-intim",
        "mau-nikah-rustic-di-bali-ini-5-venue-dengan-nuansa-kayu-view-sawah-yang-super-aesthetic",
        "mau-nikah-outdoor-dengan-view-alam-ini-dia-5-garden-wedding-venue-di-bali-yang-bikin-hati-adem-dan-foto-makin-estetik",
        "mau-nikah-di-bali-ini-10-venue-wedding-tepi-pantai-paling-hits-2025-estetik-bikin-tamu-terpukau",
        "nikah-saat-golden-hour-ini-dia-3-venue-sunset-wedding-di-bali-yang-gak-cuma-cantik-tapi-bikin-speechless",
        "rencana-nikah-outdoor-tapi-takut-hujan-ini-5-venue-bali-dengan-rain-plan-backup-yang-aman-estetik",
        "cek-venue-sebelum-deal-ini-checklist-wajib-saat-venue-tour-wedding-di-bali",
        "5-glass-chapel-paling-aesthetic-di-bali-buat-kamu-yang-mau-nikah-ala-pinterest",
        "8-villa-wedding-bali-dengan-infinity-pool-dan-view-laut-yang-bikin-momen-nikah-kamu-makin-epic",
        "mau-nikah-cuma-sama-orang-tersayang-ini-5-villa-private-di-bali-buat-intimate-wedding-paling-eksklusif",
        "5-resort-mewah-di-bali-untuk-nikah-sekaligus-honeymoon-praktis-estetik-dan-bebas-ribet",
        "10-ballroom-hotel-paling-glamour-di-bali-buat-resepsi-wedding-yang-bikin-tamu-speechless",
        "mau-nikah-di-bali-gak-mau-ribet-ini-dia-3-venue-dengan-all-in-wedding-package-paling-worth-it",
        "mau-nikah-di-bali-tapi-gak-mau-ribet-ini-5-venue-wedding-dekat-bandara-yang-super-praktis",
        "venue-wedding-bali-dengan-vendor-lokal-berkualitas-bikin-nikahan-kamu-gak-cuma-estetik-tapi-juga-anti-drama",
        "wedding-di-bali-gak-harus-ribet-ini-3-venue-kids-friendly-biar-tamu-bawa-anak-tetap-happy",
    ],
    "foto-prewedding": [
        "lokasi-prewedding-unik-bali",
        "lokasi-prewedding-unik-singapura",
        "prewedding-negative-space-minimalis",
        "sepuluh-gaya-fotografi-pernikahan",
        "kecewa-sama-foto-wedding-tenang-ini-4-cara-biar-tetap-estetik-nggak-nyesel",
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
