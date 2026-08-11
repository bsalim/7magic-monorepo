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

TESTIMONIALS: list[dict[str, str]] = [
    {
        "couple": "Marcell & Jenny",
        "message": "Speechless, kerja WO nya ok banget",
        "image": "/img/testimonials/1-marcell-jenny.jpg",
    },
    {
        "couple": "Widi & Kimi",
        "message": "7Magic mantap, cepat, dan gas full banget kinerjanya",
        "image": "/img/testimonials/3-widi-kimmi.jpg",
    },
    {
        "couple": "Andy & Brigitta",
        "message": "7Magic keren banget, top markotop",
        "image": "/img/testimonials/5-andy-brigitta.jpg",
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
        "stars": venue["stars"],
        "price_start_from": venue["price_start_from"],
        "price_for_total_pax": venue["price_for_total_pax"],
        "path_url": venue_path(venue),
        "cover_photo": venue["cover_photo"],
    }
