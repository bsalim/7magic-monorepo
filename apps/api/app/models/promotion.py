from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

# How often a visitor is shown the popup again after dismissing it.
FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"
FREQUENCY_ONCE = "once"
FREQUENCIES = (FREQUENCY_DAILY, FREQUENCY_WEEKLY, FREQUENCY_ONCE)


class PromotionPopup(TimestampMixin, Base):
    """The single promotional popup shown on the public site.

    Deliberately a singleton: the CMS edits one row (id=1) in place rather than
    keeping a library of promos. Indonesian is canonical and English is
    optional, mirroring Article — a blank ``*_en`` falls back to ``*_id``.
    """

    __tablename__ = "promotion_popups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    title_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    title_en: Mapped[str | None] = mapped_column(String(255))
    body_id: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_en: Mapped[str | None] = mapped_column(Text)

    banner_url: Mapped[str | None] = mapped_column(String(1024))
    # Retained so a replaced banner can be deleted from R2 later.
    banner_key: Mapped[str | None] = mapped_column(String(1024))

    cta_label_id: Mapped[str | None] = mapped_column(String(120))
    cta_label_en: Mapped[str | None] = mapped_column(String(120))
    cta_url: Mapped[str | None] = mapped_column(String(1024))

    frequency: Mapped[str] = mapped_column(
        String(16), nullable=False, default=FREQUENCY_DAILY
    )
