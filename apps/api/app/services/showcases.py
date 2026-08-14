"""Wedding showcases — past weddings 7Magic organised.

Indonesian is canonical and English falls back to it field by field, matching
the article service. Kept separate from articles because a showcase has no
category, no author and no body requirement — it is a photo with a caption.
"""

from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Showcase
from app.schemas.content import (
    ImageRef,
    ShowcaseAdminDetail,
    ShowcaseAdminSummary,
    ShowcaseCard,
    ShowcaseCreate,
    ShowcaseDetail,
    ShowcaseListResponse,
    ShowcaseUpdate,
)

SHOWCASE_FALLBACK_IMAGE = "/img/wedding-venue-deal-768.jpg"

BASE_LOCALE = "id"


class ShowcaseNotFoundError(LookupError):
    pass


class ShowcaseSlugConflictError(ValueError):
    pass


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "showcase"


def _pick(primary: str | None, fallback: str | None) -> str:
    """English falls back to Indonesian when blank."""
    return (primary or "").strip() or (fallback or "").strip()


def _title_for(row: Showcase, locale: str) -> str:
    return _pick(row.title_en, row.title_id) if locale == "en" else row.title_id


def _body_for(row: Showcase, locale: str) -> str:
    return _pick(row.body_en, row.body_id) if locale == "en" else (row.body_id or "")


def _image_ref(row: Showcase, alt: str) -> ImageRef | None:
    url = row.image_url or SHOWCASE_FALLBACK_IMAGE
    variants = row.image_variants if isinstance(row.image_variants, dict) else {}
    return ImageRef(
        alt=alt,
        small_url=url,
        webp_srcset=variants.get("webp_srcset"),
        jpeg_srcset=variants.get("jpeg_srcset"),
        sizes=variants.get("sizes"),
    )


def _card(row: Showcase, locale: str = BASE_LOCALE) -> ShowcaseCard:
    title = _title_for(row, locale)
    return ShowcaseCard(
        title=title,
        slug=row.slug,
        showcase_date=row.showcase_date.isoformat() if row.showcase_date else None,
        image=_image_ref(row, title),
    )


class ShowcaseService:
    # --- admin --------------------------------------------------------------

    async def admin_list(self, session: AsyncSession) -> list[ShowcaseAdminSummary]:
        rows = (
            await session.scalars(
                select(Showcase).order_by(
                    Showcase.showcase_date.desc().nullslast(), Showcase.id.desc()
                )
            )
        ).all()
        return [
            ShowcaseAdminSummary(
                id=row.id,
                title=row.title_id,
                slug=row.slug,
                status=row.status,
                showcase_date=row.showcase_date.isoformat() if row.showcase_date else None,
                image_url=row.image_url,
                has_english=bool((row.title_en or "").strip()),
                updated_at=row.updated_at.isoformat() if row.updated_at else None,
            )
            for row in rows
        ]

    async def admin_detail(self, session: AsyncSession, showcase_id: int) -> ShowcaseAdminDetail:
        row = await self._get(session, showcase_id)
        return self._detail(row)

    async def create(self, session: AsyncSession, payload: ShowcaseCreate) -> ShowcaseAdminDetail:
        slug = (payload.slug or slugify(payload.title_id)).strip()
        await self._assert_slug_free(session, slug=slug)

        row = Showcase(
            slug=slug,
            title_id=payload.title_id,
            title_en=payload.title_en,
            body_id=payload.body_id,
            body_en=payload.body_en,
            showcase_date=payload.showcase_date,
            status=payload.status,
            image_url=payload.image_url,
            image_storage_key=payload.image_storage_key,
            image_variants=payload.image_variants,
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return self._detail(row)

    async def update(
        self, session: AsyncSession, showcase_id: int, payload: ShowcaseUpdate
    ) -> ShowcaseAdminDetail:
        row = await self._get(session, showcase_id)
        values = payload.model_dump(exclude_unset=True)

        if (slug := values.pop("slug", None)) is not None:
            slug = slug.strip()
            if slug != row.slug:
                await self._assert_slug_free(session, slug=slug, exclude_id=row.id)
            row.slug = slug

        for field, value in values.items():
            setattr(row, field, value)

        await session.commit()
        await session.refresh(row)
        return self._detail(row)

    async def delete(self, session: AsyncSession, showcase_id: int) -> list[str]:
        """Delete the row and hand back the R2 keys the caller should clean up.

        The row goes first on purpose. If R2 deletion fails we are left with
        orphaned objects, which is invisible and cheap to sweep later; the
        reverse order would leave a live row pointing at deleted images, which
        renders as a broken card on the public site.
        """
        row = await self._get(session, showcase_id)
        keys = storage_keys_for(row)
        await session.delete(row)
        await session.commit()
        return keys

    # --- public -------------------------------------------------------------

    async def list_published(
        self, session: AsyncSession, *, locale: str = BASE_LOCALE, limit: int = 24, offset: int = 0
    ) -> ShowcaseListResponse:
        base = select(Showcase).where(Showcase.status == "published")
        total = await session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        rows = (
            await session.scalars(
                base.order_by(
                    Showcase.showcase_date.desc().nullslast(), Showcase.id.desc()
                )
                .limit(limit)
                .offset(offset)
            )
        ).all()
        return ShowcaseListResponse(
            items=[_card(row, locale) for row in rows], total=int(total or 0)
        )

    async def detail_by_slug(
        self, session: AsyncSession, slug: str, *, locale: str = BASE_LOCALE
    ) -> ShowcaseDetail:
        row = await session.scalar(
            select(Showcase).where(Showcase.slug == slug, Showcase.status == "published")
        )
        if row is None:
            raise ShowcaseNotFoundError(slug)
        card = _card(row, locale)
        return ShowcaseDetail(**card.model_dump(), body=_body_for(row, locale))

    # --- internals ----------------------------------------------------------

    async def _get(self, session: AsyncSession, showcase_id: int) -> Showcase:
        row = await session.get(Showcase, showcase_id)
        if row is None:
            raise ShowcaseNotFoundError(showcase_id)
        return row

    async def _assert_slug_free(
        self, session: AsyncSession, *, slug: str, exclude_id: int | None = None
    ) -> None:
        stmt = select(Showcase.id).where(Showcase.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Showcase.id != exclude_id)
        if await session.scalar(stmt):
            raise ShowcaseSlugConflictError(f"Slug '{slug}' is already used by another showcase.")

    def _detail(self, row: Showcase) -> ShowcaseAdminDetail:
        return ShowcaseAdminDetail(
            id=row.id,
            title_id=row.title_id,
            title_en=row.title_en or "",
            slug=row.slug,
            body_id=row.body_id or "",
            body_en=row.body_en or "",
            showcase_date=row.showcase_date.isoformat() if row.showcase_date else None,
            status=row.status,
            image_url=row.image_url,
            image_storage_key=row.image_storage_key,
            image_variants=row.image_variants if isinstance(row.image_variants, dict) else None,
            has_english=bool((row.title_en or "").strip()),
            source_ref=row.source_ref,
            updated_at=row.updated_at.isoformat() if row.updated_at else None,
        )


showcase_service = ShowcaseService()


def showcase_image_variants(upload_result: dict) -> dict:
    """Narrow a storage upload result down to what a showcase row stores.

    The storage service returns the full variant manifest (every encoded size,
    both formats). A showcase only ever renders a <picture> srcset, so keeping
    the whole manifest on the row would store kilobytes of JSON nobody reads.
    Note the rename: storage calls it `sizes_attribute`, the row calls it
    `sizes`, matching what ImageRef expects.
    """
    return {
        "original": upload_result.get("url"),
        "webp_srcset": upload_result.get("webp_srcset"),
        "jpeg_srcset": upload_result.get("jpeg_srcset"),
        "sizes": upload_result.get("sizes_attribute"),
    }


def _keys_from_srcset(srcset: str | None, public_base: str) -> list[str]:
    """Pull object keys back out of a stored `url 320w, url 480w` srcset."""
    if not srcset:
        return []
    keys: list[str] = []
    for candidate in srcset.split(","):
        url = candidate.strip().split(" ")[0]
        if url.startswith(public_base):
            keys.append(url[len(public_base) :].lstrip("/"))
    return keys


def storage_keys_for(row: Showcase) -> list[str]:
    """Every R2 object belonging to this showcase: the original plus variants.

    Variant keys are recovered from the stored srcsets rather than rebuilt from
    the breakpoint table, so this stays correct for rows uploaded before the
    breakpoints were last changed.
    """
    settings = get_settings()
    public_base = (settings.r2_public_base_url or "").rstrip("/")

    keys: list[str] = []
    if row.image_storage_key:
        keys.append(row.image_storage_key)

    variants = row.image_variants if isinstance(row.image_variants, dict) else {}
    if public_base:
        keys.extend(_keys_from_srcset(variants.get("webp_srcset"), public_base))
        keys.extend(_keys_from_srcset(variants.get("jpeg_srcset"), public_base))
        original = variants.get("original")
        if isinstance(original, str) and original.startswith(public_base):
            keys.append(original[len(public_base) :].lstrip("/"))

    seen: set[str] = set()
    return [key for key in keys if key and not (key in seen or seen.add(key))]
