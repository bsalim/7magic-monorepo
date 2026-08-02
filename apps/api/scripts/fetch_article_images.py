"""Source featured images for the article set from Pexels.

Two phases. `--stage` downloads three candidates per article at preview size
into a staging directory along with their metadata, so each one can be looked
at before it is chosen. `--finalise` takes the picks recorded in picks.json,
re-downloads them at full size into static/img/articles, and writes CREDITS.md.

Choosing by search-result title alone produces credits that are a list of
guesses, so the staging step exists to be reviewed rather than skipped.

    uv run python scripts/fetch_article_images.py --stage
    uv run python scripts/fetch_article_images.py --finalise
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO = Path(__file__).resolve().parents[3]
STAGING = REPO / "apps/web/static/img/articles/_staging"
FINAL = REPO / "apps/web/static/img/articles"
PICKS = STAGING / "picks.json"
META = STAGING / "candidates.json"

# One search query per article slug. Indonesian-specific wherever the topic
# allows it, since generic western stock is the failure mode these articles
# would otherwise land in.
QUERIES: dict[str, str] = {
    # adat-tradisi
    "istilah-tahapan-pernikahan-adat-jawa": "javanese traditional wedding ceremony",
    "menentukan-tanggal-pernikahan-weton-shio": "chinese zodiac lunar calendar",
    "tren-seserahan-mas-kawin-2026": "wedding gift tray hamper",
    "upacara-pedang-pora-pernikahan-militer": "indonesian soldier military uniform ceremony",
    # beauty-fashion
    "makeup-tahan-lama-cuaca-tropis": "bridal makeup artist applying",
    "panduan-memilih-cincin-kawin": "wedding rings close up",
    "tas-darurat-pengantin": "wedding day emergency kit essentials",
    "timeline-perawatan-diri-6-bulan-sebelum-menikah": "facial skincare treatment woman",
    # dekorasi
    "inspirasi-centerpiece-pelaminan-tidak-pasaran": "wedding table centerpiece flowers",
    "palet-warna-pernikahan-2026": "wedding flowers color palette",
    # pernikahan-islami
    "adab-dan-doa-bagi-pengantin-baru": "muslim couple praying together",
    "aturan-wali-nikah-dan-urutan-duduk-saat-akad": "ijab kabul akad nikah indonesia",
    "keuangan-rumah-tangga-islami": "muslim couple planning finances",
    "kriteria-memilih-pasangan-dalam-islam": "muslim couple hijab portrait",
    "mahar-dalam-islam": "gold jewelry wedding dowry",
    "menikah-dengan-sepupu-mahram-dan-kesehatan": "indonesian family gathering",
    "menikah-di-bulan-ramadan": "muslim couple iftar ramadan together",
    "musik-hiburan-pernikahan-islami": "wedding musicians performing",
    "nafkah-dan-tanggung-jawab-finansial-dalam-islam": "muslim couple home budget",
    "taaruf-sampai-khitbah-alur-menuju-pernikahan": "muslim couple meeting family",
    "tinggal-bersama-orang-tua-atau-pisah-rumah-setelah-menikah": "indonesian family home together",
    "walimah-syar-i-berkesan": "muslim wedding reception",
    # persiapan-pernikahan
    "cara-menghitung-porsi-katering-pernikahan": "wedding catering buffet food",
    "cara-menyusun-daftar-tamu-undangan-tanpa-drama-keluarga": "writing guest list planning",
    "prosesi-pemberkatan-pernikahan-katolik": "catholic church wedding ceremony",
    "susunan-acara-lamaran-dari-awal-sampai-akhir": "engagement ceremony family",
    "syarat-dokumen-nikah-2026-kua-catatan-sipil": "signing marriage documents paperwork",
    "tahapan-pemberkatan-pernikahan-kristen-protestan": "christian church wedding blessing",
    # photography
    "prewedding-negative-space-minimalis": "minimalist couple portrait landscape",
    "sepuluh-gaya-fotografi-pernikahan": "wedding photographer with camera",
    # tips-hubungan
    "bulan-madu-setelah-menikah-panduan-anggaran": "honeymoon couple travel beach",
    "jarak-usia-pernikahan-apa-yang-penting": "couple holding hands portrait",
    "kesetiaan-komitmen-sebelum-menikah": "couple serious conversation",
    "lebaran-pertama-sebagai-suami-istri": "eid family gathering indonesia",
    "membagi-peran-pekerjaan-rumah-tangga-setelah-menikah": "couple housework kitchen together",
    "memilih-bridesmaid-dan-groomsmen": "bridesmaids groomsmen wedding party group",
    "menikah-dulu-atau-beli-rumah-dulu": "couple new home keys",
    "menjaga-hubungan-baik-dengan-mertua": "asian multigenerational family at home",
    "percakapan-keuangan-sebelum-menikah": "couple discussing finances documents",
    "perjanjian-pranikah-panduan-lengkap": "couple signing legal document",
    "red-flags-sebelum-menikah": "asian couple serious difficult conversation",
    "siap-menikah-pasangan-belum-siap": "thoughtful woman looking window",
    "tes-kesehatan-pranikah-panduan-lengkap": "medical blood test laboratory",
    "thr-bonus-tahunan-untuk-dp-vendor-pernikahan": "indonesian rupiah banknotes cash",
    # venue-lokasi
    "12-pertanyaan-sebelum-tanda-tangan-venue-pernikahan": "wedding venue ballroom",
    "intimate-wedding-100-tamu-jakarta-rincian-biaya": "intimate wedding reception dinner",
    "masjid-gedung-favorit-jabodetabek-akad-nikah": "mosque interior indonesia",
    "menikah-di-bali-budget-masuk-akal": "bali wedding villa tropical",
}

CANDIDATES = 3
UA = "7magic-content/1.0"


def api_key() -> str:
    for env_path in (REPO / "apps/api/.env", REPO / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            if line.startswith("PEXELS_API_KEY="):
                return line.partition("=")[2].strip().strip("\"'")
    raise SystemExit("PEXELS_API_KEY not found in apps/api/.env or .env")


def search(key: str, query: str) -> list[dict]:
    url = (
        "https://api.pexels.com/v1/search?"
        + urllib.parse.urlencode(
            {"query": query, "per_page": CANDIDATES, "orientation": "landscape"}
        )
    )
    # Pexels rejects Python's default urllib User-Agent with a 403, so this
    # header is load-bearing rather than cosmetic.
    req = urllib.request.Request(
        url, headers={"Authorization": key, "User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp).get("photos", [])


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "7magic-content/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def stage(only: list[str] | None = None) -> None:
    key = api_key()
    STAGING.mkdir(parents=True, exist_ok=True)
    # Re-staging a subset keeps the candidates already reviewed, so merge into
    # the existing metadata rather than replacing it.
    meta: dict[str, list[dict]] = json.loads(META.read_text()) if META.exists() else {}
    wanted = {s: q for s, q in QUERIES.items() if not only or s in only}

    for i, (slug, query) in enumerate(sorted(wanted.items()), 1):
        try:
            photos = search(key, query)
        except Exception as exc:
            print(f"  ! {slug}: search failed ({exc})")
            continue
        entries = []
        for n, photo in enumerate(photos, 1):
            dest = STAGING / f"{slug}--{n}.jpg"
            try:
                download(photo["src"]["medium"], dest)
            except Exception as exc:
                print(f"  ! {slug} candidate {n}: download failed ({exc})")
                continue
            entries.append(
                {
                    "n": n,
                    "id": photo["id"],
                    "photographer": photo["photographer"],
                    "page": photo["url"],
                    "alt": photo.get("alt") or "",
                    "full": photo["src"]["large2x"],
                    "file": dest.name,
                }
            )
        meta[slug] = entries
        print(f"  [{i:2d}/{len(QUERIES)}] {slug}: {len(entries)} candidates  ({query})")
        time.sleep(0.3)

    META.write_text(json.dumps(meta, indent=2))
    print(f"\nStaged {sum(len(v) for v in meta.values())} images for {len(meta)} articles")
    print(f"Metadata: {META}")


def finalise() -> None:
    if not PICKS.exists():
        raise SystemExit(f"No picks file at {PICKS}")
    meta = json.loads(META.read_text())
    picks = json.loads(PICKS.read_text())
    FINAL.mkdir(parents=True, exist_ok=True)

    rows = []
    for slug in sorted(picks):
        choice = picks[slug]
        entry = next((e for e in meta.get(slug, []) if e["n"] == choice), None)
        if entry is None:
            print(f"  ! {slug}: pick {choice} not in candidates")
            continue
        dest = FINAL / f"{slug}.jpg"
        try:
            download(entry["full"], dest)
        except Exception as exc:
            print(f"  ! {slug}: full download failed ({exc})")
            continue
        size_kb = dest.stat().st_size // 1024
        rows.append((slug, entry, size_kb))
        print(f"  {slug}.jpg  {size_kb}KB  Pexels #{entry['id']} by {entry['photographer']}")

    lines = [
        "# Kredit foto — artikel",
        "",
        "Foto stok Pexels untuk gambar utama artikel. Lisensi Pexels mengizinkan",
        "penggunaan komersial tanpa atribusi; berkas ini ada supaya kita tahu mana",
        "yang harus diganti begitu 7Magic punya foto sendiri.",
        "",
        "Setiap gambar sudah dilihat satu per satu sebelum dipilih, bukan hanya",
        "diambil dari judul hasil pencarian.",
        "",
        "| Berkas | Artikel | Sumber | Lisensi |",
        "|---|---|---|---|",
    ]
    for slug, entry, _ in rows:
        alt = (entry["alt"] or "tanpa deskripsi")[:70]
        lines.append(
            f"| `{slug}.jpg` | {slug} | [Pexels #{entry['id']}]({entry['page']}) "
            f"— {alt}, oleh {entry['photographer']} | Pexels |"
        )
    (FINAL / "CREDITS.md").write_text("\n".join(lines) + "\n")

    total_mb = sum(kb for _, _, kb in rows) / 1024
    print(f"\nFinalised {len(rows)} images, {total_mb:.1f}MB total")
    print(f"Credits: {FINAL / 'CREDITS.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true", help="download candidates for review")
    parser.add_argument("--finalise", action="store_true", help="apply picks.json")
    parser.add_argument("--only", default="", help="comma-separated slugs to re-stage")
    args = parser.parse_args()
    if args.stage:
        stage([s for s in args.only.split(",") if s] or None)
    elif args.finalise:
        finalise()
    else:
        parser.error("pass --stage or --finalise")


if __name__ == "__main__":
    main()
