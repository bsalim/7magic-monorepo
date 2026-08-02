from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_website_read_access
from app.core.database import get_db_session
from app.core.errors import error_response
from app.schemas.content import (
    Locale,
    VenueDetail,
    VenueListResponse,
    VenuePriceBandsResponse,
    VenuePublicDetail,
)
from app.services.venues import VenueNotFoundError, venue_service

router = APIRouter(dependencies=[Depends(require_website_read_access)])


@router.get("", response_model=VenueListResponse)
async def list_venues(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    city: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    stars_min: Annotated[int | None, Query(ge=1, le=5)] = None,
    # Repeatable exact ratings (?stars=5&stars=3), used by the tick-box filter on
    # the search page. stars_min stays for the hero search and for links already
    # in the wild, which mean "this rating and above".
    stars: Annotated[list[int] | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=24)] = 12,
) -> VenueListResponse:
    return await venue_service.website_list(
        session,
        q=q,
        city=city,
        stars_min=stars_min,
        stars=stars,
        page=page,
        page_size=page_size,
    )


@router.get("/price-bands", response_model=VenuePriceBandsResponse)
async def venue_price_bands(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> VenuePriceBandsResponse:
    return await venue_service.price_bands(session)


@router.get("/{city}/{slug}", response_model=VenuePublicDetail)
async def venue_detail(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    city: str,
    slug: str,
    locale: Annotated[Locale, Query()] = "id",
) -> VenueDetail | JSONResponse:
    try:
        return await venue_service.website_detail(
            session, city=city, slug=slug, locale=locale
        )
    except VenueNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            message="Venue not found.",
            details={"resource": "venue"},
        )
