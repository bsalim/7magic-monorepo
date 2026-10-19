from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

VENUES: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Kempinski Indonesia",
        "slug": "kempinski-indonesia",
        "city": "jakarta",
        "district": "Jakarta Pusat",
        "address": "Jl. M.H. Thamrin No.1, Jakarta",
        "stars": 5,
        "description": "Elegant ballroom venue for refined Jakarta wedding receptions.",
        "price_start_from": 148_000_000,
        "price_for_total_pax": 300,
        "status": "active",
        "cover_photo": {
            "alt": "Kempinski Indonesia wedding venue",
            "small_url": "/img/kempinski-hotel-jakpus.jpg",
            "large_url": "/img/kempinski-hotel-jakpus.jpg",
        },
        "gallery": [
            {
                "webp": "/img/kempinski-hotel-jakpus.jpg",
                "fallback": "/img/kempinski-hotel-jakpus.jpg",
                "thumb_webp": "/img/kempinski-hotel-jakpus.jpg",
                "thumb_fallback": "/img/kempinski-hotel-jakpus.jpg",
            }
        ],
    },
    {
        "id": 2,
        "name": "The Westin Jakarta",
        "slug": "the-westin-jakarta",
        "city": "jakarta",
        "district": "Jakarta Selatan",
        "address": "Jl. H.R. Rasuna Said Kav.C-22A, Jakarta",
        "stars": 5,
        "description": "High-rise luxury venue with skyline views and premium hospitality.",
        "price_start_from": 168_000_000,
        "price_for_total_pax": 400,
        "status": "active",
        "cover_photo": {
            "alt": "The Westin Jakarta wedding venue",
            "small_url": "/img/the-westin.jpg",
            "large_url": "/img/the-westin.jpg",
        },
        "gallery": [],
    },
    {
        "id": 3,
        "name": "Ritz-Carlton Pacific Place",
        "slug": "ritz-carlton-pacific-place",
        "city": "jakarta",
        "district": "Jakarta Selatan",
        "address": "Sudirman Central Business District, Jakarta",
        "stars": 5,
        "description": "Premium city wedding venue for intimate and grand receptions.",
        "price_start_from": 188_000_000,
        "price_for_total_pax": 350,
        "status": "active",
        "cover_photo": {
            "alt": "Ritz-Carlton Pacific Place wedding venue",
            "small_url": "/img/Ritz-Carlton-PP.jpg",
            "large_url": "/img/Ritz-Carlton-PP.jpg",
        },
        "gallery": [],
    },
    {
        "id": 4,
        "name": "Hilton Bali Wiwaha Chapel",
        "slug": "wiwaha-chapel-hilton-bali",
        "city": "bali",
        "district": "Nusa Dua",
        "address": "Nusa Dua Selatan, Bali",
        "stars": 5,
        "description": "Ocean-facing chapel and resort venue for destination weddings.",
        "price_start_from": 128_000_000,
        "price_for_total_pax": 120,
        "status": "active",
        "cover_photo": {
            "alt": "Hilton Bali Wiwaha Chapel wedding venue",
            "small_url": "/img/venue-city-bali.jpg",
            "large_url": "/img/venue-city-bali.jpg",
        },
        "gallery": [],
    },
]

ARTICLES: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "How to Compare Wedding Venue Packages",
        "slug": "compare-wedding-venue-packages",
        "category": "wedding-venue",
        "summary": "A practical checklist for comparing inclusions, pax count, vendors, and hidden costs.",
        "content": "<h2 id=\"budget\">Budget</h2><p>Start from total guest count and package inclusions.</p>",
        "topic": ["packages", "budget"],
        "image_url": "/img/wedding-venue-deal-768.jpg",
        "author": "7Magic Editorial",
        "status": "published",
        "featured": True,
        "updated_at": datetime(2026, 5, 9, tzinfo=timezone.utc).isoformat(),
    },
    {
        "id": 2,
        "title": "Jakarta Ballroom Wedding Planning Notes",
        "slug": "jakarta-ballroom-wedding-planning-notes",
        "category": "wedding-planning",
        "summary": "Questions couples should ask before locking a hotel ballroom date.",
        "content": "<h2 id=\"date\">Date</h2><p>Ask about minimum spend and weekend availability early.</p>",
        "topic": ["ballroom", "jakarta"],
        "image_url": "/img/hero-home.jpg",
        "author": "7Magic Editorial",
        "status": "draft",
        "featured": False,
        "updated_at": datetime(2026, 5, 8, tzinfo=timezone.utc).isoformat(),
    },
]

# The "Review Pengantin" sheet from 7Magic: real couples, in its order, with the
# date of their wedding. Quotes are the couples' own words with spelling and
# spacing tidied, nothing added. Photos are frames from their congratulation
# videos, square-cropped around both faces and uploaded once to R2 with webp and
# jpeg widths (the three smallest originals only reach 320 or 480px).
TESTIMONIALS: list[dict[str, Any]] = [
    {
        "couple": "Marcell & Jenny",
        "message": "Speechless, kerja WO-nya oke banget.",
        "wedding_date": "2022-01-15",
        "photo": {
            "alt": "Marcell & Jenny",
            "small_url": "https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/160b0bf4f8eb4ad7bc4c153ec34d47f5-1-marcell-jenny_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Ardy & Selvi",
        "message": "Luar biasa, pokoknya dibantu banget pas hari H. Keren pokoknya.",
        "wedding_date": "2023-11-04",
        "photo": {
            "alt": "Ardy & Selvi",
            "small_url": "https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/c2bb37f471804f488b525a7e0072b747-2-ardy-selvi_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Widi & Kimi",
        "message": "7Magic mantap, cepet, gas full banget kinerjanya.",
        "wedding_date": "2022-03-19",
        "photo": {
            "alt": "Widi & Kimi",
            "small_url": "https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/b1c1493a30124c00b6abe3ae824e737c-3-widi-kimmi_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Giovanni & Tiny",
        "message": "Timnya selalu support. Semoga 7Magic makin terus berkembang ke depannya.",
        "wedding_date": "2023-10-07",
        "photo": {
            "alt": "Giovanni & Tiny",
            "small_url": "https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/396a210dc9e3440c9f406785a4d08f4e-4-giovanni-tiny_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Andy & Brigitta",
        "message": "7Magic keren banget, top markotop.",
        "wedding_date": "2023-12-10",
        "photo": {
            "alt": "Andy & Brigitta",
            "small_url": "https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/9f4d00948c84479385ba5e6051139a21-5-andy-brigitta_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Johby & Devi",
        "message": "Thank you, acara kami berjalan dengan lancar. Sabar banget kru-krunya.",
        "wedding_date": "2021-12-19",
        "photo": {
            "alt": "Johby & Devi",
            "small_url": "https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/2a58c1c868204d2fbe7967ddd09362d4-6-johby-devi_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Tonny & Grace",
        "message": "Terima kasih ya untuk 7Magic, kami sangat terbantu di hari H pernikahan kami.",
        "wedding_date": "2023-10-28",
        "photo": {
            "alt": "Tonny & Grace",
            "small_url": "https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/b52259d00e9a46cab62db2c89cdfbbfb-7-tony-grace_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Anthony & Florence",
        "message": "Bener-bener kerjanya bagus banget, helpful banget di hari ini.",
        "wedding_date": "2021-01-03",
        "photo": {
            "alt": "Anthony & Florence",
            "small_url": "https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/525b830ee99c483d9682a3d15e1a6928-8-anthony-florence_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Daniel & Vera",
        "message": "7Magic bagus banget, ngebantu banget, kerja WO-nya tidak hitungan.",
        "wedding_date": "2021-05-22",
        "photo": {
            "alt": "Daniel & Vera",
            "small_url": "https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/ac1a526523a34af49fb538abc09ee6a8-9-daniel-vera_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Calvin & Paulina",
        "message": "Dari awal 7Magic itu detail banget, bantu kita banget dari awal sampai akhir.",
        "wedding_date": "2021-11-27",
        "photo": {
            "alt": "Calvin & Paulina",
            "small_url": "https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/7060efbd4a2f4afc94a12cd0752b9868-10-calvin-paulina_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Paulus & Niellen",
        "message": "Kita seneng banget dibantu sama tim kalian yang super solid.",
        "wedding_date": "2022-01-23",
        "photo": {
            "alt": "Paulus & Niellen",
            "small_url": "https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/41576d4e10e848d0b7b4f4779f9e8e06-11-paulus-niellen_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Ronny & Meli",
        "message": "Keren banget WO-nya, kerjanya rapi dan teratur. Top banget.",
        "wedding_date": "2021-11-14",
        "photo": {
            "alt": "Ronny & Meli",
            "small_url": "https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/4da86543cede4c6fbdca37b83f214851-12-ronny-meli_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Andi & Selvi",
        "message": "Thank you 7Magic, tanpa kalian hari ini acara kami tidak bisa seperti ini. Pokoknya WO paling the best.",
        "wedding_date": "2021-10-10",
        "photo": {
            "alt": "Andi & Selvi",
            "small_url": "https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/9760ab4fde224e80be754c66059fb925-13-andi-selvi_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Berly & Gabriela",
        "message": "7Magic service-nya gercep banget, the best lah pokoknya.",
        "wedding_date": "2024-09-08",
        "photo": {
            "alt": "Berly & Gabriela",
            "small_url": "https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_sm_480w.webp 480w, https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_md_800w.webp 800w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_sm_480w.jpg 480w, https://media.7magicwedding.com/testimonials/206c46894156420f8e08d64c0dcd3407-14-berly-gabriela_md_800w.jpg 800w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Yonathan & Gladys",
        "message": "7Magic memang the best.",
        "wedding_date": "2022-10-22",
        "photo": {
            "alt": "Yonathan & Gladys",
            "small_url": "https://media.7magicwedding.com/testimonials/89f27c5c0bc8498b8ea96af2ef9b24ae-15-yonathan-gladys_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/89f27c5c0bc8498b8ea96af2ef9b24ae-15-yonathan-gladys_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/89f27c5c0bc8498b8ea96af2ef9b24ae-15-yonathan-gladys_sm_480w.webp 480w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/89f27c5c0bc8498b8ea96af2ef9b24ae-15-yonathan-gladys_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/89f27c5c0bc8498b8ea96af2ef9b24ae-15-yonathan-gladys_sm_480w.jpg 480w",
            "width": 480,
            "height": 480,
        },
    },
    {
        "couple": "Raymond & Melisiu",
        "message": "7Magic, tim dan kerja samanya luar biasa.",
        "wedding_date": "2023-01-15",
        "photo": {
            "alt": "Raymond & Melisiu",
            "small_url": "https://media.7magicwedding.com/testimonials/767ec4b1819e4392b34c522f3bdf6a7f-16-raymond-melisiu_xs_320w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/767ec4b1819e4392b34c522f3bdf6a7f-16-raymond-melisiu_xs_320w.webp 320w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/767ec4b1819e4392b34c522f3bdf6a7f-16-raymond-melisiu_xs_320w.jpg 320w",
            "width": 320,
            "height": 320,
        },
    },
    {
        "couple": "Reynaldo & Michelle",
        "message": "Nggak kebayang jika nggak pakai WO 7Magic, dibantuin total seharian.",
        "wedding_date": "2022-11-05",
        "photo": {
            "alt": "Reynaldo & Michelle",
            "small_url": "https://media.7magicwedding.com/testimonials/197c259337064ba4a8efb360096e54be-17-reynaldo-saputra_sm_480w.jpg",
            "webp_srcset": "https://media.7magicwedding.com/testimonials/197c259337064ba4a8efb360096e54be-17-reynaldo-saputra_xs_320w.webp 320w, https://media.7magicwedding.com/testimonials/197c259337064ba4a8efb360096e54be-17-reynaldo-saputra_sm_480w.webp 480w",
            "jpeg_srcset": "https://media.7magicwedding.com/testimonials/197c259337064ba4a8efb360096e54be-17-reynaldo-saputra_xs_320w.jpg 320w, https://media.7magicwedding.com/testimonials/197c259337064ba4a8efb360096e54be-17-reynaldo-saputra_sm_480w.jpg 480w",
            "width": 480,
            "height": 480,
        },
    },
]


def venue_path(venue: dict[str, Any]) -> str:
    return f"/wedding-venue/{venue['city']}/{venue['slug']}"


def public_venue_card(venue: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": venue["id"],
        "name": venue["name"],
        "slug": venue["slug"],
        "city": venue["city"],
        "district": venue["district"],
        "address": venue["address"],
        "stars": venue["stars"],
        "price_start_from": venue["price_start_from"],
        "price_for_total_pax": venue["price_for_total_pax"],
        "path_url": venue_path(venue),
        "cover_photo": venue["cover_photo"],
    }
