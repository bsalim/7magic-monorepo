from __future__ import annotations

from datetime import timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PromotionPopup
from app.models.promotion import FREQUENCIES
from app.schemas.content import PromotionPopupAdmin, PromotionPopupPublic, PromotionPopupUpdate

# Indonesian is canonical; English falls back to it field by field.
BASE_LOCALE = "id"

# The CMS edits one row in place rather than keeping a library of promos.
SINGLETON_ID = 1


def _localized(value_id: str | None, value_en: str | None, locale: str) -> str | None:
    if locale != BASE_LOCALE:
        # An English field left blank means "same as Indonesian", not "empty".
        return (value_en or "").strip() or value_id
    return value_id


class PromotionService:
    async def _get_or_create(self, session: AsyncSession) -> PromotionPopup:
        result = await session.execute(
            select(PromotionPopup).where(PromotionPopup.id == SINGLETON_ID)
        )
        popup = result.scalar_one_or_none()
        if popup is None:
            # The migration seeds this, but a database restored from an older
            # dump would not have it.
            popup = PromotionPopup(id=SINGLETON_ID, active=False, title_id="", body_id="")
            session.add(popup)
            await session.flush()
        return popup

    async def admin_detail(self, session: AsyncSession) -> PromotionPopupAdmin:
        popup = await self._get_or_create(session)
        return PromotionPopupAdmin.model_validate(popup, from_attributes=True)

    async def update(
        self, session: AsyncSession, payload: PromotionPopupUpdate
    ) -> PromotionPopupAdmin:
        popup = await self._get_or_create(session)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(popup, field, value)

        await session.flush()
        await session.refresh(popup)
        return PromotionPopupAdmin.model_validate(popup, from_attributes=True)

    async def public_detail(
        self, session: AsyncSession, locale: str = BASE_LOCALE
    ) -> PromotionPopupPublic | None:
        """The popup as the website should render it, or None when it is off.

        Returns None rather than an inactive payload so the web app never ships
        promo copy it is not going to show.
        """
        popup = await self._get_or_create(session)

        if not popup.active:
            return None

        title = _localized(popup.title_id, popup.title_en, locale)
        body = _localized(popup.body_id, popup.body_en, locale)

        # A promo with no title and no banner has nothing to display.
        if not (title or "").strip() and not popup.banner_url:
            return None

        # The version changes whenever the promo is edited, which lets the web
        # app re-show a dismissed popup after the content changes instead of
        # staying hidden behind a stale cookie.
        stamp = popup.updated_at or popup.created_at
        version = str(int(stamp.replace(tzinfo=stamp.tzinfo or timezone.utc).timestamp()))

        return PromotionPopupPublic(
            version=version,
            title=title or "",
            body=body or "",
            banner_url=popup.banner_url,
            cta_label=_localized(popup.cta_label_id, popup.cta_label_en, locale),
            cta_url=popup.cta_url,
            frequency=popup.frequency if popup.frequency in FREQUENCIES else "daily",
        )


promotion_service = PromotionService()
