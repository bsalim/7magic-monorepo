from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class ImageRef(BaseModel):
    """A displayable image. `small_url` stays the single-URL fallback; the
    srcset fields let the browser choose a width instead of always taking
    whatever `small_url` happens to be."""

    alt: str
    small_url: str
    large_url: str | None = None
    webp_srcset: str | None = None
    jpeg_srcset: str | None = None
    sizes: str | None = None
    width: int | None = None
    height: int | None = None


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class VenueCard(BaseModel):
    id: int
    name: str
    slug: str
    city: str
    district: str
    stars: int
    price_start_from: int | None
    price_for_total_pax: int
    path_url: str
    cover_photo: ImageRef


class VenueListResponse(BaseModel):
    items: list[VenueCard]
    pagination: Pagination


class VenueCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    district: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=2, max_length=255)
    stars: int = Field(ge=1, le=5)
    description: str = Field(min_length=1)
    price_start_from: int | None = Field(default=None, ge=0)
    price_for_total_pax: int = Field(default=0, ge=0)
    status: Literal["draft", "active", "archived"] = "draft"
    temp_venue_id: str | None = Field(
        default=None,
        description="Claim photos uploaded to this temp id during venue creation.",
    )


# Locales the platform serves. Indonesian is canonical; English overrides it.
Locale = Literal["id", "en"]


class VenuePriceBand(BaseModel):
    """One budget bracket. `max_price` is None for the open-ended top band."""

    label: str
    min_price: int
    max_price: int | None
    count: int


class VenuePriceBandsResponse(BaseModel):
    """Live pricing summary for the homepage anchor. `floor` is the cheapest
    real price; venues stored as 0 mean 'on request' and are excluded."""

    floor: int | None
    priced: int
    on_request: int
    bands: list[VenuePriceBand]


class VenueTranslationUpsert(BaseModel):
    description: str | None = None
    packages: dict[str, Any] | None = None


class VenueTranslationResponse(BaseModel):
    venue_id: int
    locale: str
    description: str | None = None
    packages: dict[str, Any] | None = None


class VenueUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    slug: str | None = Field(default=None, min_length=2, max_length=150)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    district: str | None = Field(default=None, min_length=2, max_length=100)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    stars: int | None = Field(default=None, ge=1, le=5)
    description: str | None = Field(default=None, min_length=1)
    price_start_from: int | None = Field(default=None, ge=0)
    price_for_total_pax: int | None = Field(default=None, ge=0)
    status: Literal["draft", "active", "archived"] | None = None


class VenueAdminSummary(BaseModel):
    id: int
    name: str
    slug: str
    city: str
    district: str
    stars: int
    price_start_from: int | None
    price_for_total_pax: int
    status: str
    cover_photo: ImageRef


class VenueDetail(VenueCard):
    address: str
    description: str
    status: str
    gallery: list[dict[str, Any]]
    packages: list[dict[str, str | int]] = Field(default_factory=list)
    seo: dict[str, str] | None = None


class VenueGalleryPhotoPublic(BaseModel):
    id: int
    url: str
    thumbnail_url: str
    alt_text: str | None = None
    sort_order: int
    webp: str
    fallback: str
    thumb_webp: str
    thumb_fallback: str


class VenuePublicDetail(VenueCard):
    address: str
    description: str
    status: str
    gallery: list[VenueGalleryPhotoPublic]
    packages: list[dict[str, str | int]] = Field(default_factory=list)
    seo: dict[str, str] | None = None


class VenuePhotoResponse(BaseModel):
    id: int
    venue_id: int | None = None
    temp_venue_id: str | None = None
    url: str
    thumbnail_url: str
    alt_text: str | None = None
    sort_order: int
    filename: str
    original_filename: str | None = None
    content_type: str | None = None
    file_size: int | None = None
    storage_key: str
    variants: dict[str, Any] = Field(default_factory=dict)


class ArticleCard(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    summary: str
    image_url: str
    author: str
    status: str
    featured: bool
    updated_at: str
    locale: str = "id"
    # `slug` and `category` are the segments for the requested locale, so they are
    # not enough on their own to reach the other language. These two carry the
    # rest: `path` is where this article canonically lives in the requested
    # locale -- the caller can compare it against the URL it was asked for and
    # redirect a stale one -- and `alternates` gives every locale's path, which is
    # what the hreflang tags and the sitemap need.
    path: str = ""
    alternates: dict[str, str] = Field(default_factory=dict)


class ArticleListResponse(BaseModel):
    items: list[ArticleCard]
    pagination: Pagination


class ArticleCreate(BaseModel):
    """Both languages on one payload. Indonesian is required; English is
    optional and blank means the article falls back to Indonesian."""

    title_id: str = Field(min_length=3, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    slug: str = Field(min_length=3, max_length=255)
    # Blank leaves the English URL identical to the Indonesian one, which is the
    # right default -- a slug is only worth translating once the article is.
    slug_en: str | None = Field(default=None, min_length=3, max_length=255)
    summary_id: str = Field(min_length=3)
    summary_en: str | None = None
    body_id: str = Field(min_length=1)
    body_en: str | None = None
    category: str = Field(min_length=2, max_length=255)
    topic: list[str] = Field(default_factory=list)
    status: Literal["draft", "published", "archived"] = "draft"
    featured: bool = False
    image_url: str | None = None
    published_at: datetime | None = None


class ArticleUpdate(BaseModel):
    title_id: str | None = Field(default=None, min_length=3, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, min_length=3, max_length=255)
    slug_en: str | None = Field(default=None, min_length=3, max_length=255)
    summary_id: str | None = Field(default=None, min_length=3)
    summary_en: str | None = None
    body_id: str | None = Field(default=None, min_length=1)
    body_en: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=255)
    topic: list[str] | None = None
    status: Literal["draft", "published", "archived"] | None = None
    featured: bool | None = None
    image_url: str | None = None


class ArticleAdminDetail(BaseModel):
    """Everything the CMS editor needs, with both languages side by side."""

    id: int
    title_id: str
    title_en: str = ""
    slug: str
    slug_en: str = ""
    summary_id: str
    summary_en: str = ""
    body_id: str
    body_en: str = ""
    category: str
    category_slug: str
    topic: list[str]
    status: str
    featured: bool
    word_count: int
    # False when the English fields are blank, so the editor can show what
    # still needs writing.
    has_english: bool = False
    image_url: str | None = None
    author: str
    published_at: str | None = None
    updated_at: str | None = None


class ArticleAdminSummary(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    category_slug: str
    status: str
    featured: bool
    word_count: int
    has_english: bool = False
    published_at: str | None = None
    updated_at: str | None = None


class ArticleAdminListResponse(BaseModel):
    items: list[ArticleAdminSummary]


class ArticleDetail(ArticleCard):
    content: str
    topic: list[str]
    word_count: int
    published_at: datetime | None = None


class ContactLeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    message: str = Field(min_length=5, max_length=2000)
    source_path: str | None = Field(default=None, max_length=255)
    venue_slug: str | None = Field(default=None, max_length=150)


class VenuePricingRequest(BaseModel):
    """Submitted from the venue detail modal. Venue prices are not shown
    publicly, so this is how a couple asks for them."""

    name: str = Field(min_length=2, max_length=120)
    whatsapp: str = Field(min_length=5, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    wedding_date: str | None = Field(default=None, max_length=30)
    best_time_to_reach: Literal["morning", "afternoon", "after_working_hours"] = "morning"
    venue_id: int | None = None
    venue_slug: str | None = Field(default=None, max_length=150)
    venue_name: str | None = Field(default=None, max_length=200)


class ContactLeadResponse(BaseModel):
    id: int
    status: Literal["received"]
    message: str
    created_at: str


class HomeHero(BaseModel):
    title: str
    subtitle: str
    image: str


class Testimonial(BaseModel):
    couple: str
    message: str
    image: str


class HomeResponse(BaseModel):
    hero: HomeHero
    featured_venues: list[VenueCard]
    featured_articles: list[ArticleCard]
    testimonials: list[Testimonial]


PromotionFrequency = Literal["daily", "weekly", "once"]


class PromotionPopupPublic(BaseModel):
    """The popup as the website renders it, already resolved to one locale."""

    # Changes whenever the promo is edited, so the web app can re-show a popup
    # a visitor dismissed under the previous content.
    version: str
    title: str
    body: str
    banner_url: str | None = None
    cta_label: str | None = None
    cta_url: str | None = None
    frequency: PromotionFrequency = "daily"


class PromotionPopupAdmin(BaseModel):
    id: int
    active: bool
    title_id: str
    title_en: str | None = None
    body_id: str
    body_en: str | None = None
    banner_url: str | None = None
    banner_key: str | None = None
    cta_label_id: str | None = None
    cta_label_en: str | None = None
    cta_url: str | None = None
    frequency: PromotionFrequency = "daily"
    updated_at: datetime | None = None


class PromotionPopupUpdate(BaseModel):
    """Every field optional so the CMS can PATCH-style save partial edits."""

    active: bool | None = None
    title_id: str | None = None
    title_en: str | None = None
    body_id: str | None = None
    body_en: str | None = None
    banner_url: str | None = None
    banner_key: str | None = None
    cta_label_id: str | None = None
    cta_label_en: str | None = None
    cta_url: str | None = None
    frequency: PromotionFrequency | None = None


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


# --- Wedding Showcases -------------------------------------------------------
# Same one-payload-two-languages shape as Article: Indonesian is required,
# English optional and blank means fall back to Indonesian.


class ShowcaseCreate(BaseModel):
    title_id: str = Field(min_length=2, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    body_id: str | None = None
    body_en: str | None = None
    showcase_date: date | None = None
    status: Literal["draft", "published", "archived"] = "draft"
    image_url: str | None = None
    image_storage_key: str | None = None
    image_variants: dict[str, Any] | None = None


class ShowcaseUpdate(BaseModel):
    title_id: str | None = Field(default=None, min_length=2, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    body_id: str | None = None
    body_en: str | None = None
    showcase_date: date | None = None
    status: Literal["draft", "published", "archived"] | None = None
    image_url: str | None = None
    image_storage_key: str | None = None
    image_variants: dict[str, Any] | None = None


class ShowcaseAdminDetail(BaseModel):
    id: int
    title_id: str
    title_en: str = ""
    slug: str
    body_id: str = ""
    body_en: str = ""
    showcase_date: str | None = None
    status: str
    image_url: str | None = None
    image_storage_key: str | None = None
    # False when the English fields are blank, so the editor can see what is
    # still untranslated without opening the row.
    has_english: bool = False
    source_ref: str | None = None
    updated_at: str | None = None


class ShowcaseAdminSummary(BaseModel):
    id: int
    title: str
    slug: str
    status: str
    showcase_date: str | None = None
    image_url: str | None = None
    has_english: bool = False
    updated_at: str | None = None


class ShowcaseAdminListResponse(BaseModel):
    items: list[ShowcaseAdminSummary]


class ShowcaseCard(BaseModel):
    """Public list item — one card on /wedding-showcases."""

    title: str
    slug: str
    showcase_date: str | None = None
    image: ImageRef | None = None


class ShowcaseListResponse(BaseModel):
    items: list[ShowcaseCard]
    total: int


class ShowcaseDetail(ShowcaseCard):
    body: str = ""
