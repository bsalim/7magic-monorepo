from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.errors import error_response
from app.schemas.content import (
    PromotionPopupPublic,
    ArticleDetail,
    Locale,
    ArticleListResponse,
    ContactLeadCreate,
    ContactLeadResponse,
    VenuePricingRequest,
    HomeResponse,
    VenueListResponse,
    ShowcaseDetail,
    ShowcaseListResponse,
)
from app.services.articles import ArticleNotFoundError, article_service
from app.services.catalog import NotFoundError, catalog_service
from app.services.leads import lead_service
from app.services.promotions import promotion_service
from app.services.showcases import ShowcaseNotFoundError, showcase_service

router = APIRouter()


@router.get("/home", response_model=HomeResponse)
async def home(session: Annotated[AsyncSession, Depends(get_db_session)]) -> HomeResponse:
    home_payload = catalog_service.home()
    return home_payload.model_copy(
        update={"featured_articles": await article_service.featured_articles(session)}
    )


@router.get("/venues")
async def list_venues(
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    city: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    stars_min: Annotated[int | None, Query(ge=1, le=5)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> VenueListResponse:
    return catalog_service.public_venues(q=q, city=city, stars_min=stars_min, page=page, page_size=page_size)


@router.get("/venues/{city}/{slug}")
async def venue_detail(city: str, slug: str) -> dict:
    try:
        return catalog_service.venue_detail(city=city, slug=slug).model_dump()
    except NotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            message="Venue not found.",
            details={"resource": "venue"},
        )


@router.get("/articles")
async def list_articles(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    category: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 12,
    locale: Annotated[Locale, Query()] = "id",
) -> ArticleListResponse:
    return await article_service.public_articles(
        session,
        category=category,
        page=page,
        page_size=page_size,
        locale=locale,
    )


@router.get("/articles/categories/{category}")
async def articles_by_category(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    category: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 12,
    locale: Annotated[Locale, Query()] = "id",
) -> ArticleListResponse:
    return await article_service.public_articles(
        session,
        category=category,
        page=page,
        page_size=page_size,
        locale=locale,
    )


@router.get("/articles/topics/{tag}")
async def articles_by_topic(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    tag: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 12,
    locale: Annotated[Locale, Query()] = "id",
) -> ArticleListResponse:
    return await article_service.public_articles(
        session,
        topic=tag,
        page=page,
        page_size=page_size,
        locale=locale,
    )


@router.get("/articles/authors/{author_slug}")
async def articles_by_author(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    author_slug: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 12,
    locale: Annotated[Locale, Query()] = "id",
) -> ArticleListResponse:
    return await article_service.public_articles(
        session,
        author_slug=author_slug,
        page=page,
        page_size=page_size,
        locale=locale,
    )


@router.get("/articles/{category}/{slug}")
async def article_detail(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    category: str,
    slug: str,
    locale: Annotated[Locale, Query()] = "id",
) -> ArticleDetail | dict:
    try:
        return await article_service.article_detail(
            session, category=category, slug=slug, locale=locale
        )
    except ArticleNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            message="Article not found.",
            details={"resource": "article"},
        )


@router.post(
    "/contact-leads",
    response_model=ContactLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact_lead(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: ContactLeadCreate,
) -> ContactLeadResponse:
    return await lead_service.create_contact_lead(session, payload)


@router.post(
    "/venue-pricing-requests",
    response_model=ContactLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_venue_pricing_request(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: VenuePricingRequest,
) -> ContactLeadResponse:
    return await lead_service.create_venue_pricing_request(session, payload)


@router.get("/promotion-popup", response_model=PromotionPopupPublic | None)
async def get_promotion_popup(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    locale: Annotated[Locale, Query()] = "id",
) -> PromotionPopupPublic | None:
    """Returns null when the popup is off, so the site ships no unused copy."""
    return await promotion_service.public_detail(session, locale=locale)


@router.get("/showcases", response_model=ShowcaseListResponse)
async def showcases(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    locale: Annotated[Locale, Query()] = "id",
    limit: Annotated[int, Query(ge=1, le=60)] = 24,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ShowcaseListResponse:
    return await showcase_service.list_published(
        session, locale=locale, limit=limit, offset=offset
    )


@router.get("/showcases/{slug}", response_model=None)
async def showcase_detail(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    locale: Annotated[Locale, Query()] = "id",
) -> ShowcaseDetail | JSONResponse:
    try:
        return await showcase_service.detail_by_slug(session, slug, locale=locale)
    except ShowcaseNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            message="Showcase not found.",
            details={"resource": "showcase"},
        )
