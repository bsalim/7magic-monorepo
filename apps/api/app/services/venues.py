from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Venue, VenuePhoto, VenueTranslation
from app.schemas.content import (
    ImageRef,
    Pagination,
    VenueAdminSummary,
    VenueCard,
    VenueCreate,
    VenueDetail,
    VenueListResponse,
    VenuePhotoResponse,
    VenuePriceBand,
    VenuePriceBandsResponse,
    VenueTranslationResponse,
    VenueTranslationUpsert,
    VenueUpdate,
)

# Indonesian content lives on the venue row itself, so it never needs a lookup.
BASE_LOCALE = "id"

# Budget brackets the homepage offers. Upper bound is exclusive; None is open-ended.
PRICE_BANDS: list[tuple[str, int, int | None]] = [
    ("under_150m", 0, 150_000_000),
    ("150m_300m", 150_000_000, 300_000_000),
    ("over_300m", 300_000_000, None),
]


class VenueSlugConflictError(ValueError):
    pass


class VenueNotFoundError(LookupError):
    pass


class VenueService:
    async def admin_list(self, session: AsyncSession) -> list[VenueAdminSummary]:
        venues = await self._list_venues(session)
        return [self._admin_summary(venue) for venue in venues]

    async def admin_detail(self, session: AsyncSession, venue_id: int) -> VenueDetail:
        venue = await self._get_by_id(session, venue_id)
        return self._detail(venue)

    async def create(self, session: AsyncSession, payload: VenueCreate) -> VenueDetail:
        values = payload.model_dump()
        temp_venue_id = values.pop("temp_venue_id", None)
        values["city"] = _normalize_city(values["city"])
        if await self._has_city_slug_conflict(
            session,
            city=values["city"],
            slug=values["slug"],
        ):
            raise VenueSlugConflictError("Venue slug already exists for this city.")

        venue = Venue(**values)
        session.add(venue)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            if _is_city_slug_integrity_error(exc):
                raise VenueSlugConflictError("Venue slug already exists for this city.") from exc
            raise

        if temp_venue_id:
            await self._claim_temp_photos(
                session, venue_id=venue.id, temp_venue_id=temp_venue_id
            )

        return await self.admin_detail(session, venue.id)

    async def update(
        self,
        session: AsyncSession,
        venue_id: int,
        payload: VenueUpdate,
    ) -> VenueDetail:
        venue = await self._get_by_id(session, venue_id)
        values = payload.model_dump(exclude_unset=True)
        if "city" in values and values["city"] is not None:
            values["city"] = _normalize_city(values["city"])

        next_city = values.get("city", _normalize_city(venue.city))
        next_slug = values.get("slug", venue.slug)
        if next_city is not None and next_slug is not None:
            if await self._has_city_slug_conflict(
                session,
                city=next_city,
                slug=next_slug,
                exclude_venue_id=venue_id,
            ):
                raise VenueSlugConflictError("Venue slug already exists for this city.")

        for key, value in values.items():
            setattr(venue, key, value)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            if _is_city_slug_integrity_error(exc):
                raise VenueSlugConflictError("Venue slug already exists for this city.") from exc
            raise

        return await self.admin_detail(session, venue_id)

    async def archive(self, session: AsyncSession, venue_id: int) -> VenueDetail:
        venue = await self._get_by_id(session, venue_id)
        venue.status = "archived"
        await session.commit()
        return await self.admin_detail(session, venue_id)

    async def delete(self, session: AsyncSession, venue_id: int) -> None:
        venue = await self._get_by_id(session, venue_id)
        await session.delete(venue)
        await session.commit()

    async def set_cover_photo(
        self, session: AsyncSession, venue_id: int, photo_id: int
    ) -> VenueDetail:
        """Promote a photo to the venue cover. The cover is simply photos[0],
        which is ordered by sort_order, so promoting means giving this photo the
        lowest order. Other photos keep their relative order."""
        venue = await self._get_by_id(session, venue_id)
        photo = next((item for item in venue.photos if item.id == photo_id), None)
        if photo is None:
            raise VenueNotFoundError("Venue photo not found.")

        lowest = min(item.sort_order for item in venue.photos)
        if photo.sort_order != lowest or photo is not venue.photos[0]:
            photo.sort_order = lowest - 1
            await session.commit()

        return await self.admin_detail(session, venue_id)

    async def delete_photo(self, session: AsyncSession, venue_id: int, photo_id: int) -> VenueDetail:
        venue = await self._get_by_id(session, venue_id)
        photo = next((item for item in venue.photos if item.id == photo_id), None)
        if photo is None:
            raise VenueNotFoundError("Venue photo not found.")
        await session.delete(photo)
        await session.commit()
        return await self.admin_detail(session, venue_id)

    async def count(self, session: AsyncSession) -> dict[str, int]:
        rows = (
            await session.execute(select(Venue.status, func.count()).group_by(Venue.status))
        ).all()
        by_status = {status: total for status, total in rows}
        return {
            "total": sum(by_status.values()),
            "active": by_status.get("active", 0),
            "draft": by_status.get("draft", 0),
            "archived": by_status.get("archived", 0),
        }

    async def website_list(
        self,
        session: AsyncSession,
        q: str | None,
        city: str | None,
        stars_min: int | None,
        page: int,
        page_size: int,
        stars: list[int] | None = None,
    ) -> VenueListResponse:
        filters = [Venue.status == "active"]
        if q:
            query = f"%{q}%"
            filters.append(
                or_(
                    Venue.name.ilike(query),
                    Venue.district.ilike(query),
                    Venue.description.ilike(query),
                )
            )
        if city:
            filters.append(_normalized_city_expression() == _normalize_city(city))
        # An explicit set of ratings wins over the "and above" form: a request
        # carrying both is coming from the tick-box filter, and silently ANDing a
        # leftover stars_min would drop rows the user had ticked.
        wanted_stars = sorted({value for value in (stars or []) if 1 <= value <= 5})
        if wanted_stars:
            filters.append(Venue.stars.in_(wanted_stars))
        elif stars_min:
            filters.append(Venue.stars >= stars_min)

        total = await session.scalar(select(func.count()).select_from(Venue).where(*filters))
        result = await session.execute(
            select(Venue)
            .options(selectinload(Venue.photos))
            .where(*filters)
            .order_by(Venue.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        venues = result.scalars().all()

        return VenueListResponse(
            items=[self._card(venue) for venue in venues],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total or 0,
                total_pages=((total or 0) + page_size - 1) // page_size if total else 0,
            ),
        )

    async def price_bands(self, session: AsyncSession) -> VenuePriceBandsResponse:
        """Summarize active venue pricing for the homepage. A price of 0 means
        'on request', so it is excluded from the floor and every band -- counting
        it would advertise a floor of Rp 0."""
        priced = Venue.price_start_from > 0
        active = Venue.status == "active"

        floor = await session.scalar(
            select(func.min(Venue.price_start_from)).where(active, priced)
        )
        priced_count = await session.scalar(
            select(func.count()).select_from(Venue).where(active, priced)
        )
        total = await session.scalar(
            select(func.count()).select_from(Venue).where(active)
        )

        bands: list[VenuePriceBand] = []
        for label, low, high in PRICE_BANDS:
            filters = [active, priced, Venue.price_start_from >= low]
            if high is not None:
                filters.append(Venue.price_start_from < high)
            count = await session.scalar(
                select(func.count()).select_from(Venue).where(*filters)
            )
            bands.append(
                VenuePriceBand(label=label, min_price=low, max_price=high, count=count or 0)
            )

        return VenuePriceBandsResponse(
            floor=int(floor) if floor else None,
            priced=priced_count or 0,
            on_request=(total or 0) - (priced_count or 0),
            bands=bands,
        )

    async def get_translation(
        self, session: AsyncSession, venue_id: int, locale: str
    ) -> VenueTranslationResponse:
        """Return a venue's copy for one locale. A locale with no row yet returns
        empty fields rather than 404, so the CMS can render an empty editor."""
        venue = await self._get_by_id(session, venue_id)
        translation = next(
            (item for item in venue.translations if item.locale == locale), None
        )
        return VenueTranslationResponse(
            venue_id=venue.id,
            locale=locale,
            description=translation.description if translation else None,
            packages=translation.packages if translation else None,
        )

    async def upsert_translation(
        self,
        session: AsyncSession,
        venue_id: int,
        locale: str,
        payload: VenueTranslationUpsert,
    ) -> VenueTranslationResponse:
        venue = await self._get_by_id(session, venue_id)
        translation = next(
            (item for item in venue.translations if item.locale == locale), None
        )
        values = payload.model_dump(exclude_unset=True)

        if translation is None:
            translation = VenueTranslation(venue_id=venue.id, locale=locale, **values)
            session.add(translation)
        else:
            for key, value in values.items():
                setattr(translation, key, value)

        await session.commit()
        await session.refresh(translation)

        return VenueTranslationResponse(
            venue_id=venue.id,
            locale=translation.locale,
            description=translation.description,
            packages=translation.packages,
        )

    async def website_detail(
        self,
        session: AsyncSession,
        city: str,
        slug: str,
        locale: str = BASE_LOCALE,
    ) -> VenueDetail:
        normalized_city = _normalize_city(city)
        result = await session.execute(
            select(Venue)
            .options(selectinload(Venue.photos))
            .where(
                Venue.status == "active",
                _normalized_city_expression() == normalized_city,
                Venue.slug == slug,
            )
        )
        venue = result.scalar_one_or_none()
        if venue is None:
            result = await session.execute(
                select(Venue)
                .options(selectinload(Venue.photos))
                .where(
                    Venue.status == "active",
                    _normalized_city_expression() == normalized_city,
                    func.replace(Venue.slug, f"-{normalized_city}-", "-") == slug,
                )
            )
            venue = result.scalar_one_or_none()
        if venue is None:
            raise VenueNotFoundError("Venue not found.")

        detail = self._detail(venue, include_internal_photo_fields=False)
        return self._localize(detail, venue, locale)

    def _localize(self, detail: VenueDetail, venue: Venue, locale: str) -> VenueDetail:
        """Overlay a locale's translated fields onto the canonical detail. Absent
        translations and null fields fall through to the Indonesian base row."""
        if locale == BASE_LOCALE:
            return detail

        translation = next(
            (item for item in venue.translations if item.locale == locale), None
        )
        if translation is None:
            return detail

        overlay = {
            key: value
            for key, value in (
                ("description", translation.description),
                ("packages", translation.packages),
            )
            if value is not None
        }
        return detail.model_copy(update=overlay) if overlay else detail

    async def attach_photo(
        self,
        session: AsyncSession,
        venue_id: int,
        storage_result: dict[str, Any],
        alt_text: str | None,
        sort_order: int,
        set_as_cover: bool = False,
    ) -> VenuePhotoResponse:
        venue = await self._get_by_id(session, venue_id)
        photo_sort_order = sort_order
        if venue.photos:
            current_cover_order = venue.photos[0].sort_order
            if set_as_cover:
                photo_sort_order = min(photo.sort_order for photo in venue.photos) - 1
            else:
                photo_sort_order = max(sort_order, current_cover_order)

        photo = VenuePhoto(
            venue_id=venue_id,
            alt_text=alt_text,
            sort_order=photo_sort_order,
            original_filename=storage_result.get("original_filename"),
            filename=storage_result.get("filename"),
            content_type=storage_result.get("content_type"),
            storage_key=storage_result.get("storage_key"),
            cdn_url=storage_result.get("url"),
            thumbnail_url=storage_result.get("thumbnail_url"),
            original_file_size=storage_result.get("file_size"),
            **_responsive_columns(storage_result),
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)

        return self._photo_response(photo, variants=storage_result.get("variants", {}))

    async def attach_temp_photo(
        self,
        session: AsyncSession,
        *,
        temp_venue_id: str,
        storage_result: dict[str, Any],
        alt_text: str | None,
        sort_order: int,
    ) -> VenuePhotoResponse:
        """Persist a photo not yet bound to a venue, keyed by a temp id.

        Used while creating a new venue: the browser uploads to a generated
        ``temp_venue_id`` and the photos are claimed once the venue exists.
        """
        photo = VenuePhoto(
            venue_id=None,
            temp_venue_id=_as_uuid(temp_venue_id),
            alt_text=alt_text,
            sort_order=sort_order,
            original_filename=storage_result.get("original_filename"),
            filename=storage_result.get("filename"),
            content_type=storage_result.get("content_type"),
            storage_key=storage_result.get("storage_key"),
            cdn_url=storage_result.get("url"),
            thumbnail_url=storage_result.get("thumbnail_url"),
            original_file_size=storage_result.get("file_size"),
            **_responsive_columns(storage_result),
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)

        return self._photo_response(photo, variants=storage_result.get("variants", {}))

    async def _claim_temp_photos(
        self,
        session: AsyncSession,
        *,
        venue_id: int,
        temp_venue_id: str,
    ) -> int:
        """Bind any temp-uploaded photos to a freshly created venue."""
        try:
            temp_uuid = _as_uuid(temp_venue_id)
        except (ValueError, AttributeError):
            return 0

        result = await session.execute(
            select(VenuePhoto)
            .where(VenuePhoto.temp_venue_id == temp_uuid, VenuePhoto.venue_id.is_(None))
            .order_by(VenuePhoto.sort_order, VenuePhoto.id)
        )
        photos = list(result.scalars().all())
        for photo in photos:
            photo.venue_id = venue_id
            photo.temp_venue_id = None
        if photos:
            await session.commit()
        return len(photos)

    async def _list_venues(self, session: AsyncSession) -> list[Venue]:
        result = await session.execute(
            select(Venue).options(selectinload(Venue.photos)).order_by(Venue.id)
        )
        return list(result.scalars().all())

    async def _get_by_id(self, session: AsyncSession, venue_id: int) -> Venue:
        result = await session.execute(
            select(Venue).options(selectinload(Venue.photos)).where(Venue.id == venue_id)
        )
        venue = result.scalar_one_or_none()
        if venue is None:
            raise VenueNotFoundError("Venue not found.")
        return venue

    async def _has_city_slug_conflict(
        self,
        session: AsyncSession,
        *,
        city: str,
        slug: str,
        exclude_venue_id: int | None = None,
    ) -> bool:
        query = select(Venue.id).where(
            _normalized_city_expression() == _normalize_city(city),
            Venue.slug == slug,
        )
        if exclude_venue_id is not None:
            query = query.where(Venue.id != exclude_venue_id)

        return await session.scalar(query.limit(1)) is not None

    def _admin_summary(self, venue: Venue) -> VenueAdminSummary:
        return VenueAdminSummary(
            id=venue.id,
            name=venue.name,
            slug=venue.slug,
            city=venue.city,
            district=venue.district,
            stars=venue.stars,
            price_start_from=_int_or_none(venue.price_start_from),
            price_for_total_pax=venue.price_for_total_pax,
            status=venue.status,
            cover_photo=self._cover_photo(venue),
        )

    def _detail(self, venue: Venue, *, include_internal_photo_fields: bool = True) -> VenueDetail:
        return VenueDetail(
            **self._card(venue).model_dump(),
            address=venue.address,
            description=venue.description or "",
            status=venue.status,
            gallery=[
                self._gallery_photo(
                    photo,
                    include_internal_fields=include_internal_photo_fields,
                )
                for photo in venue.photos
            ],
            packages=self._packages(venue),
            seo={
                "title": f"{venue.name} - {venue.district}, {venue.city} | Wedding Venue",
                "meta_description": venue.description or "",
                "canonical_url": venue.path_url,
            },
        )

    def _card(self, venue: Venue) -> VenueCard:
        return VenueCard(
            id=venue.id,
            name=venue.name,
            slug=venue.slug,
            city=venue.city,
            district=venue.district,
            stars=venue.stars,
            price_start_from=_int_or_none(venue.price_start_from),
            price_for_total_pax=venue.price_for_total_pax,
            path_url=venue.path_url,
            cover_photo=self._cover_photo(venue),
        )

    def _cover_photo(self, venue: Venue) -> ImageRef:
        first_photo = venue.photos[0] if venue.photos else None
        if first_photo:
            large_url, thumb_url = _photo_image_urls(first_photo)
            if thumb_url or large_url:
                return ImageRef(
                    alt=first_photo.alt_text or f"{venue.name} wedding venue",
                    small_url=thumb_url or large_url,
                    large_url=large_url or thumb_url,
                    **_photo_responsive_fields(first_photo),
                )

        return ImageRef(
            alt=f"{venue.name} wedding venue",
            small_url="/img/wedding-venue-deal-768.jpg",
            large_url="/img/wedding-venue-deal-1920.webp",
        )

    def _gallery_photo(
        self,
        photo: VenuePhoto,
        *,
        include_internal_fields: bool,
    ) -> dict[str, Any]:
        large_url, thumb_url = _photo_image_urls(photo)
        url = large_url or thumb_url or ""
        thumbnail_url = thumb_url or url
        gallery_photo = {
            "id": photo.id,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "alt_text": photo.alt_text,
            "sort_order": photo.sort_order,
            "webp": url,
            "fallback": url,
            "thumb_webp": thumbnail_url,
            "thumb_fallback": thumbnail_url,
        }
        if include_internal_fields:
            gallery_photo.update(
                {
                    "venue_id": photo.venue_id,
                    "temp_venue_id": str(photo.temp_venue_id) if photo.temp_venue_id else None,
                    "filename": photo.filename or "",
                    "original_filename": photo.original_filename,
                    "content_type": photo.content_type,
                    "file_size": photo.original_file_size,
                    "storage_key": photo.storage_key or "",
                    "variants": {},
                }
            )
        return gallery_photo

    def _photo_response(
        self,
        photo: VenuePhoto,
        *,
        variants: dict[str, Any],
    ) -> VenuePhotoResponse:
        return VenuePhotoResponse(
            id=photo.id,
            venue_id=photo.venue_id,
            temp_venue_id=str(photo.temp_venue_id) if photo.temp_venue_id else None,
            url=photo.cdn_url or "",
            thumbnail_url=photo.thumbnail_url or photo.cdn_url or "",
            alt_text=photo.alt_text,
            sort_order=photo.sort_order,
            filename=photo.filename or "",
            original_filename=photo.original_filename,
            content_type=photo.content_type,
            file_size=photo.original_file_size,
            storage_key=photo.storage_key or "",
            variants=variants,
        )

    def _packages(self, venue: Venue) -> list[dict[str, str | int]]:
        if isinstance(venue.packages, list):
            return venue.packages

        return [
            {
                "name": "Wedding reception package",
                "price": _int_or_none(venue.price_start_from) or 0,
                "pax": venue.price_for_total_pax,
                "note": "Starting package, confirm inclusions with 7Magic.",
            }
        ]


def _int_or_none(value: Decimal | int | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _as_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def _variant_url(variant: dict[str, Any]) -> str | None:
    if not isinstance(variant, dict):
        return None
    return variant.get("cdn_url") or variant.get("s3_url") or variant.get("url")




def _responsive_columns(storage_result: dict[str, Any]) -> dict[str, Any]:
    """Variant columns from an upload result, empty when the storage layer could
    not render variants (non-image upload, or every variant upload failed)."""
    keys = (
        "webp_variants",
        "jpeg_variants",
        "webp_srcset",
        "jpeg_srcset",
        "sizes_attribute",
        "breakpoints_used",
        "formats_generated",
        "original_width",
        "original_height",
        "orientation",
    )
    return {key: storage_result[key] for key in keys if key in storage_result}

def _srcset_from_variants(variants: Any) -> str | None:
    """Build a `url 320w, url 480w, ...` srcset from a variant list."""
    if not isinstance(variants, list):
        return None

    entries = [
        f"{url} {width}w"
        for variant in variants
        if isinstance(variant, dict)
        and (width := variant.get("width"))
        and (url := _variant_url(variant))
    ]
    return ", ".join(entries) or None


def _photo_responsive_fields(photo: VenuePhoto) -> dict[str, Any]:
    """Responsive attributes for a photo, preferring the srcset strings stored at
    import time and falling back to rebuilding them from the variant lists."""
    webp = photo.webp_srcset or _srcset_from_variants(photo.webp_variants)
    jpeg = photo.jpeg_srcset or _srcset_from_variants(photo.jpeg_variants)

    return {
        "webp_srcset": webp,
        "jpeg_srcset": jpeg,
        "sizes": photo.sizes_attribute if (webp or jpeg) else None,
        "width": photo.original_width,
        "height": photo.original_height,
    }

def _photo_image_urls(photo: VenuePhoto) -> tuple[str | None, str | None]:
    """Resolve (large_url, thumb_url) for a venue photo.

    Directly-uploaded photos store ``cdn_url``/``thumbnail_url``. Imported
    photos instead carry responsive ``jpeg_variants``/``webp_variants`` JSON,
    so derive a large and a thumbnail URL from those when needed. JPEG variants
    are preferred for broad ``<img src>`` compatibility.
    """
    if photo.cdn_url:
        return photo.cdn_url, photo.thumbnail_url or photo.cdn_url

    variants = photo.jpeg_variants or photo.webp_variants
    if isinstance(variants, list) and variants:
        sized = [
            (variant.get("width") or 0, url)
            for variant in variants
            if (url := _variant_url(variant))
        ]
        if sized:
            sized.sort(key=lambda item: item[0])
            thumb_url = sized[0][1]
            # Prefer a mid/large variant (~1024w) for the cover image.
            large_url = next(
                (url for width, url in sized if width >= 1024),
                sized[-1][1],
            )
            return large_url, photo.thumbnail_url or thumb_url

    return photo.cdn_url, photo.thumbnail_url


def _normalize_city(value: str) -> str:
    return value.strip().casefold().replace(" ", "-")


def _normalized_city_expression() -> Any:
    return func.replace(func.lower(Venue.city), " ", "-")


def _is_city_slug_integrity_error(exc: IntegrityError) -> bool:
    message = str(exc.orig).casefold()
    return "uq_venues_city_slug" in message or (
        "unique" in message and "venues.city" in message and "venues.slug" in message
    )


venue_service = VenueService()
