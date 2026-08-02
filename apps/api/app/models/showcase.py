from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import CheckConstraint, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Showcase(TimestampMixin, Base):
    """A past wedding 7Magic organised, shown as a card on the public site.

    Follows the same one-row-holds-both-languages shape as Article: Indonesian
    is canonical and required, English is optional and falls back to Indonesian
    when blank.

    The image is stored inline rather than through media_assets. A showcase has
    exactly one image and the storage service already hands back url, key and
    variants together, so a join would buy nothing.
    """

    __tablename__ = "showcases"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="showcase_status_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    title_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str | None] = mapped_column(String(255))
    body_id: Mapped[str | None] = mapped_column(Text)
    body_en: Mapped[str | None] = mapped_column(Text)

    showcase_date: Mapped[date | None] = mapped_column(Date, index=True)

    image_url: Mapped[str | None] = mapped_column(String(512))
    image_storage_key: Mapped[str | None] = mapped_column(String(512))
    image_variants: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    # Where an imported row came from, so a re-run can skip it and an editor can
    # trace a draft back to the original post.
    source_ref: Mapped[str | None] = mapped_column(String(255), unique=True)
