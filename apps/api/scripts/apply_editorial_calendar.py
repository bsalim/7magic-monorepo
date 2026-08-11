"""Apply the 2026 editorial calendar to the imported articles.

Sets `published_at` per docs/marketing/2026-editorial-calendar.md and flips
status to published. Dates are backdated -- the window closed before this
script was written -- so the articles present as a back-archive.

Times are 09:00 Asia/Jakarta, stored as UTC.

    uv run python scripts/apply_editorial_calendar.py            # dry run
    uv run python scripts/apply_editorial_calendar.py --commit
    uv run python scripts/apply_editorial_calendar.py --commit --status draft
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article

WIB = timezone(timedelta(hours=7))
PUBLISH_HOUR = 9

# slug -> (month, day) in 2026. Order and rationale live in
# docs/marketing/2026-editorial-calendar.md.
CALENDAR: dict[str, tuple[int, int]] = {
    # Januari -- kesiapan, keuangan, dokumen
    "siap-menikah-pasangan-belum-siap": (1, 3),
    "percakapan-keuangan-sebelum-menikah": (1, 7),
    "menikah-dulu-atau-beli-rumah-dulu": (1, 11),
    "susunan-acara-lamaran-dari-awal-sampai-akhir": (1, 15),
    "red-flags-sebelum-menikah": (1, 19),
    "syarat-dokumen-nikah-2026-kua-catatan-sipil": (1, 23),
    "menentukan-tanggal-pernikahan-weton-shio": (1, 27),
    "tren-seserahan-mas-kawin-2026": (1, 31),
    # Februari -- Valentine 14, Imlek 17, Ramadan mulai ~19
    "kriteria-memilih-pasangan-dalam-islam": (2, 4),
    "taaruf-sampai-khitbah-alur-menuju-pernikahan": (2, 8),
    "jarak-usia-pernikahan-apa-yang-penting": (2, 12),
    "kesetiaan-komitmen-sebelum-menikah": (2, 14),
    "menikah-di-bulan-ramadan": (2, 17),
    "walimah-syar-i-berkesan": (2, 21),
    "keuangan-rumah-tangga-islami": (2, 25),
    # Maret -- THR ~13, Idulfitri ~20, musim akad Syawal
    "thr-bonus-tahunan-untuk-dp-vendor-pernikahan": (3, 1),
    "mahar-dalam-islam": (3, 5),
    "nafkah-dan-tanggung-jawab-finansial-dalam-islam": (3, 9),
    "lebaran-pertama-sebagai-suami-istri": (3, 13),
    "menjaga-hubungan-baik-dengan-mertua": (3, 17),
    "adab-dan-doa-bagi-pengantin-baru": (3, 22),
    "aturan-wali-nikah-dan-urutan-duduk-saat-akad": (3, 26),
    "musik-hiburan-pernikahan-islami": (3, 30),
    # April -- pascalebaran, kunci venue, musim kemarau
    "menikah-dengan-sepupu-mahram-dan-kesehatan": (4, 3),
    "tes-kesehatan-pranikah-panduan-lengkap": (4, 7),
    "tinggal-bersama-orang-tua-atau-pisah-rumah-setelah-menikah": (4, 11),
    "12-pertanyaan-sebelum-tanda-tangan-venue-pernikahan": (4, 15),
    "masjid-gedung-favorit-jabodetabek-akad-nikah": (4, 19),
    "intimate-wedding-100-tamu-jakarta-rincian-biaya": (4, 23),
    "menikah-di-bali-budget-masuk-akal": (4, 27),
    # Mei -- detail eksekusi sebelum puncak musim
    "cara-menyusun-daftar-tamu-undangan-tanpa-drama-keluarga": (5, 1),
    "cara-menghitung-porsi-katering-pernikahan": (5, 5),
    "memilih-bridesmaid-dan-groomsmen": (5, 9),
    "perjanjian-pranikah-panduan-lengkap": (5, 13),
    "timeline-perawatan-diri-6-bulan-sebelum-menikah": (5, 17),
    "sepuluh-gaya-fotografi-pernikahan": (5, 21),
    "prewedding-negative-space-minimalis": (5, 25),
    "palet-warna-pernikahan-2026": (5, 29),
    # Juni -- puncak musim resepsi
    "inspirasi-centerpiece-pelaminan-tidak-pasaran": (6, 2),
    "makeup-tahan-lama-cuaca-tropis": (6, 6),
    "tas-darurat-pengantin": (6, 11),
    "panduan-memilih-cincin-kawin": (6, 16),
    "istilah-tahapan-pernikahan-adat-jawa": (6, 21),
    "upacara-pedang-pora-pernikahan-militer": (6, 26),
    # Juli -- pemberkatan, lalu pascanikah
    "prosesi-pemberkatan-pernikahan-katolik": (7, 1),
    "tahapan-pemberkatan-pernikahan-kristen-protestan": (7, 6),
    "bulan-madu-setelah-menikah-panduan-anggaran": (7, 13),
    "membagi-peran-pekerjaan-rumah-tangga-setelah-menikah": (7, 20),
}


def published_at_for(month: int, day: int) -> datetime:
    local = datetime(2026, month, day, PUBLISH_HOUR, tzinfo=WIB)
    return local.astimezone(timezone.utc)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument(
        "--status",
        default="published",
        choices=["draft", "published", "archived"],
        help="status to set alongside the date (default: published)",
    )
    args = parser.parse_args()

    if len(CALENDAR) != 48:
        raise SystemExit(f"Calendar has {len(CALENDAR)} entries, expected 48")

    async with AsyncSessionLocal() as session:
        articles = {
            a.slug: a
            for a in (
                await session.scalars(select(Article).where(Article.slug.in_(CALENDAR)))
            ).all()
        }

        missing = sorted(set(CALENDAR) - set(articles))
        if missing:
            print(f"{len(missing)} slug(s) in the calendar are not in the database:")
            for slug in missing:
                print("  !", slug)
            raise SystemExit(1)

        updated = 0
        for slug, (month, day) in sorted(CALENDAR.items(), key=lambda kv: kv[1]):
            article = articles[slug]
            when = published_at_for(month, day)
            stamp = when.astimezone(WIB).strftime("%Y-%m-%d %H:%M WIB")
            if args.commit:
                article.published_at = when
                article.status = args.status
            print(f"  {stamp}  {args.status:<9} {slug}")
            updated += 1

        if args.commit:
            await session.commit()

        verb = "updated" if args.commit else "would update"
        print(f"\n{verb} {updated} articles, status={args.status}")
        if not args.commit:
            print("Dry run -- re-run with --commit to write.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
