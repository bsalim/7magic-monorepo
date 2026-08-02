from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ArticleCategory(Base):
    __tablename__ = "article_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    category_slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    articles: Mapped[list[Article]] = relationship(back_populates="category")


class Article(TimestampMixin, Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("category_id", "slug", name="uq_articles_category_slug"),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="article_status_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("article_categories.id"), index=True)
    # One row holds both languages. Indonesian is canonical and required;
    # English is optional and falls back to Indonesian when blank, so an
    # untranslated article simply leaves the _en fields empty.
    title_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str | None] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    summary_id: Mapped[str | None] = mapped_column(Text)
    summary_en: Mapped[str | None] = mapped_column(Text)
    body_id: Mapped[str] = mapped_column(Text, nullable=False)
    body_en: Mapped[str | None] = mapped_column(Text)
    content_text: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_asset_id: Mapped[int | None] = mapped_column(ForeignKey("media_assets.id", ondelete="SET NULL"))
    image_caption: Mapped[str | None] = mapped_column(String(255))
    featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    schema_jsonld: Mapped[str | None] = mapped_column(Text)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    trash: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    topic: Mapped[list[str] | None] = mapped_column(JSON)

    def title_for(self, locale: str) -> str:
        """English when it exists, Indonesian otherwise."""
        return (self.title_en or self.title_id) if locale == "en" else self.title_id

    def summary_for(self, locale: str) -> str:
        value = (self.summary_en or self.summary_id) if locale == "en" else self.summary_id
        return value or ""

    def body_for(self, locale: str) -> str:
        return (self.body_en or self.body_id) if locale == "en" else self.body_id

    def has_translation(self, locale: str) -> bool:
        """Whether this article genuinely exists in `locale` rather than
        falling back."""
        if locale == "en":
            return bool((self.title_en or "").strip() and (self.body_en or "").strip())
        return True

    author: Mapped[User] = relationship(back_populates="articles")
    category: Mapped[ArticleCategory | None] = relationship(back_populates="articles")
    images: Mapped[list[ArticleImage]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )

    @property
    def full_url(self) -> str:
        category_slug = self.category.category_slug if self.category else "artikel"
        return f"/artikel/{category_slug}/{self.slug}"


class ArticleImage(Base):
    __tablename__ = "article_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("articles.id", ondelete="SET NULL"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    temp_article_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    filename: Mapped[str | None] = mapped_column(String(255))
    file_type: Mapped[str | None] = mapped_column(String(20))
    file_hash: Mapped[str | None] = mapped_column(String(255), index=True)
    file_size: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    image: Mapped[str | None] = mapped_column(String(255))
    cdn_url: Mapped[str | None] = mapped_column(String(512))

    article: Mapped[Article | None] = relationship(back_populates="images")
    user: Mapped[User | None] = relationship(back_populates="article_images")


class ArticleTag(Base):
    __tablename__ = "article_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
