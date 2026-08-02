from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from app.api.v1.endpoints.fixtures import ARTICLES, TESTIMONIALS, VENUES
from app.schemas.content import (
    ArticleCard,
    ArticleCreate,
    ArticleDetail,
    ArticleListResponse,
    ContactLeadCreate,
    ContactLeadResponse,
    HomeResponse,
    Pagination,
    VenueAdminSummary,
    VenueCard,
    VenueCreate,
    VenueDetail,
    VenueListResponse,
    VenuePhotoResponse,
    VenueUpdate,
    utc_now_iso,
)


class SlugConflictError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


def venue_path(venue: dict[str, Any]) -> str:
    return f"/wedding-venue/{venue['city']}/{venue['slug']}"


def count_words_from_html(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"\b[\w'-]+\b", text))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "unknown"


def venue_card(venue: dict[str, Any]) -> VenueCard:
    return VenueCard(
        id=venue["id"],
        name=venue["name"],
        slug=venue["slug"],
        city=venue["city"],
        district=venue["district"],
        stars=venue["stars"],
        price_start_from=venue["price_start_from"],
        price_for_total_pax=venue["price_for_total_pax"],
        path_url=venue_path(venue),
        cover_photo=venue["cover_photo"],
    )


def article_card(article: dict[str, Any]) -> ArticleCard:
    return ArticleCard(
        id=article["id"],
        title=article["title"],
        slug=article["slug"],
        category=article["category"],
        summary=article["summary"],
        image_url=article.get("image_url") or "",
        author=article["author"],
        status=article["status"],
        featured=article["featured"],
        updated_at=article["updated_at"],
    )


class CatalogService:
    def __init__(self) -> None:
        self._venues = deepcopy(VENUES)
        self._articles = deepcopy(ARTICLES)
        self._contact_leads: list[dict[str, Any]] = []
        self._temp_venue_photos: list[dict[str, Any]] = []
        self._next_venue_photo_id = 1

    def home(self) -> HomeResponse:
        published_articles = [article for article in self._articles if article["status"] == "published"]
        return HomeResponse(
            hero={
                "title": "Best Value Wedding Packages in Jakarta, Bali, and Singapore",
                "subtitle": (
                    "Secure your perfect wedding venue with curated 7Magic packages and "
                    "planning support."
                ),
                "image": "/img/wedding-venue-deal-1920.webp",
            },
            featured_venues=[
                venue_card(venue) for venue in self._venues if venue["status"] == "active"
            ][:8],
            featured_articles=[article_card(article) for article in published_articles[:4]],
            testimonials=TESTIMONIALS,
        )

    def public_venues(
        self,
        *,
        q: str | None = None,
        city: str | None = None,
        stars_min: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> VenueListResponse:
        results = [venue for venue in self._venues if venue["status"] == "active"]

        if q:
            query = q.casefold()
            results = [venue for venue in results if query in venue["name"].casefold()]
        if city:
            city_query = city.casefold()
            results = [venue for venue in results if venue["city"].casefold() == city_query]
        if stars_min:
            results = [venue for venue in results if venue["stars"] >= stars_min]

        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        return VenueListResponse(
            items=[venue_card(venue) for venue in results[start:end]],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=(total + page_size - 1) // page_size if total else 0,
            ),
        )

    def venue_detail(self, *, city: str, slug: str) -> VenueDetail:
        venue = self._find_venue_by_city_slug(city=city, slug=slug, active_only=True)
        if not venue:
            raise NotFoundError("Venue not found.")

        return self._venue_detail_from_record(venue)

    def admin_venue_detail(self, venue_id: int) -> VenueDetail:
        venue = self._find_venue_by_id(venue_id)
        if not venue:
            raise NotFoundError("Venue not found.")

        return self._venue_detail_from_record(venue)

    def _venue_detail_from_record(self, venue: dict[str, Any]) -> VenueDetail:
        return VenueDetail(
            **venue_card(venue).model_dump(),
            address=venue["address"],
            description=venue["description"],
            status=venue["status"],
            gallery=sorted(venue["gallery"], key=lambda photo: photo.get("sort_order", 0)),
            packages=[
                {
                    "name": "Wedding reception package",
                    "price": venue["price_start_from"] or 0,
                    "pax": venue["price_for_total_pax"],
                    "note": "Starting package, confirm inclusions with 7Magic.",
                }
            ],
            seo={
                "title": f"{venue['name']} - {venue['district']}, {venue['city']} | Wedding Venue",
                "meta_description": venue["description"],
                "canonical_url": venue_path(venue),
            },
        )

    def public_articles(
        self,
        *,
        category: str | None = None,
        topic: str | None = None,
        author_slug: str | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> dict[str, Any]:
        results = [article for article in self._articles if article["status"] == "published"]
        if category:
            results = [article for article in results if article["category"] == category]
        if topic:
            topic_query = topic.casefold()
            results = [
                article
                for article in results
                if topic_query in [item.casefold() for item in article.get("topic", [])]
            ]
        if author_slug:
            results = [article for article in results if slugify(article["author"]) == author_slug]

        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        return ArticleListResponse(
            items=[article_card(article) for article in results[start:end]],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=(total + page_size - 1) // page_size if total else 0,
            ),
        ).model_dump()

    def create_contact_lead(self, payload: ContactLeadCreate) -> ContactLeadResponse:
        lead = {
            **payload.model_dump(),
            "id": len(self._contact_leads) + 1,
            "created_at": utc_now_iso(),
        }
        self._contact_leads.append(lead)
        return ContactLeadResponse(
            id=lead["id"],
            status="received",
            message="Lead received.",
            created_at=lead["created_at"],
        )

    def article_detail(self, *, category: str, slug: str) -> ArticleDetail:
        article = next(
            (
                item
                for item in self._articles
                if item["category"] == category
                and item["slug"] == slug
                and item["status"] == "published"
            ),
            None,
        )
        if not article:
            raise NotFoundError("Article not found.")

        return ArticleDetail(
            **article_card(article).model_dump(),
            content=article["content"],
            topic=article.get("topic", []),
            word_count=article.get("word_count", count_words_from_html(article["content"])),
            published_at=article.get("published_at"),
        )

    def admin_dashboard(self) -> dict[str, Any]:
        return {
            "totals": {
                "venues": len(self._venues),
                "articles": len(self._articles),
                "drafts": len([article for article in self._articles if article["status"] == "draft"]),
                "leads": 18,
            },
            "recent_activity": [
                {
                    "id": 1,
                    "action": "published",
                    "entity": "article",
                    "actor": "7Magic Editorial",
                    "created_at": "2026-05-09T09:00:00+07:00",
                },
                {
                    "id": 2,
                    "action": "updated",
                    "entity": "venue",
                    "actor": "Venue Admin",
                    "created_at": "2026-05-08T15:30:00+07:00",
                },
            ],
        }

    def admin_venues(self) -> list[VenueAdminSummary]:
        return [
            VenueAdminSummary(
                id=venue["id"],
                name=venue["name"],
                slug=venue["slug"],
                city=venue["city"],
                district=venue["district"],
                stars=venue["stars"],
                price_start_from=venue["price_start_from"],
                price_for_total_pax=venue["price_for_total_pax"],
                status=venue["status"],
                cover_photo=venue["cover_photo"],
            )
            for venue in self._venues
        ]

    def create_venue(self, payload: VenueCreate) -> VenueDetail:
        if any(
            venue["city"].casefold() == payload.city.casefold() and venue["slug"] == payload.slug
            for venue in self._venues
        ):
            raise SlugConflictError("Venue slug already exists for this city.")

        venue = {
            **payload.model_dump(),
            "id": max(venue["id"] for venue in self._venues) + 1,
            "cover_photo": {
                "alt": f"{payload.name} wedding venue",
                "small_url": "/img/wedding-venue-deal-768.jpg",
                "large_url": "/img/wedding-venue-deal-1920.webp",
            },
            "gallery": [],
        }
        self._venues.append(venue)
        return self.admin_venue_detail(venue["id"])

    def update_venue(self, venue_id: int, payload: VenueUpdate) -> VenueDetail:
        venue = self._find_venue_by_id(venue_id)
        if not venue:
            raise NotFoundError("Venue not found.")

        values = payload.model_dump(exclude_unset=True)
        next_city = values.get("city", venue["city"])
        next_slug = values.get("slug", venue["slug"])
        if any(
            item["id"] != venue_id
            and item["city"].casefold() == next_city.casefold()
            and item["slug"] == next_slug
            for item in self._venues
        ):
            raise SlugConflictError("Venue slug already exists for this city.")

        venue.update(values)
        return self.admin_venue_detail(venue_id)

    def attach_venue_photo(
        self,
        *,
        storage_result: dict[str, Any],
        alt_text: str | None,
        sort_order: int,
        venue_id: int | None = None,
        temp_venue_id: str | None = None,
        set_as_cover: bool = False,
    ) -> VenuePhotoResponse:
        if venue_id is None and temp_venue_id is None:
            raise NotFoundError("Venue not found.")

        venue = self._find_venue_by_id(venue_id) if venue_id is not None else None
        if venue_id is not None and not venue:
            raise NotFoundError("Venue not found.")

        photo = {
            "id": self._next_venue_photo_id,
            "venue_id": venue_id,
            "temp_venue_id": temp_venue_id,
            "url": storage_result["url"],
            "thumbnail_url": storage_result["thumbnail_url"],
            "alt_text": alt_text,
            "sort_order": sort_order,
            "filename": storage_result["filename"],
            "original_filename": storage_result.get("original_filename"),
            "content_type": storage_result.get("content_type"),
            "file_size": storage_result.get("file_size"),
            "storage_key": storage_result["storage_key"],
            "variants": storage_result.get("variants", {}),
            "webp": storage_result["url"],
            "fallback": storage_result["url"],
            "thumbWebp": storage_result["thumbnail_url"],
            "thumbFallback": storage_result["thumbnail_url"],
        }
        self._next_venue_photo_id += 1

        if venue is not None:
            should_set_cover = set_as_cover or not venue["gallery"]
            venue["gallery"].append(photo)
            if should_set_cover:
                venue["cover_photo"] = {
                    "alt": alt_text or f"{venue['name']} wedding venue",
                    "small_url": storage_result["thumbnail_url"],
                    "large_url": storage_result["url"],
                }
        else:
            self._temp_venue_photos.append(photo)

        return VenuePhotoResponse(**photo)

    def _find_venue_by_id(self, venue_id: int | None) -> dict[str, Any] | None:
        return next((venue for venue in self._venues if venue["id"] == venue_id), None)

    def _find_venue_by_city_slug(
        self,
        *,
        city: str,
        slug: str,
        active_only: bool,
    ) -> dict[str, Any] | None:
        return next(
            (
                item
                for item in self._venues
                if item["city"].casefold() == city.casefold()
                and item["slug"] == slug
                and (not active_only or item["status"] == "active")
            ),
            None,
        )

    def admin_articles(self) -> list[ArticleCard]:
        return [article_card(article) for article in self._articles]

    def create_article(self, payload: ArticleCreate) -> ArticleDetail:
        if any(
            article["category"] == payload.category and article["slug"] == payload.slug
            for article in self._articles
        ):
            raise SlugConflictError("Article slug already exists for this category.")

        article = {
            **payload.model_dump(),
            "id": max(article["id"] for article in self._articles) + 1,
            "image_url": payload.image_url or "",
            "updated_at": utc_now_iso(),
            "word_count": count_words_from_html(payload.content),
        }
        self._articles.append(article)
        return ArticleDetail(**article_card(article).model_dump(), **{
            "content": article["content"],
            "topic": article["topic"],
            "word_count": article["word_count"],
            "published_at": article.get("published_at"),
        })


catalog_service = CatalogService()
