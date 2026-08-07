from __future__ import annotations

import re
from math import ceil

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Article, ArticleCategory, ArticleImage, User
from app.schemas.content import (
    ArticleAdminDetail,
    ArticleAdminSummary,
    ArticleCard,
    ArticleCreate,
    ArticleDetail,
    ArticleListResponse,
    ArticleUpdate,
    Pagination,
)

ARTICLE_FALLBACK_IMAGE = "/img/wedding-venue-deal-768.jpg"

# Indonesian is canonical; English falls back to it field by field.
BASE_LOCALE = "id"


class ArticleNotFoundError(LookupError):
    pass


class ArticleSlugConflictError(ValueError):
    """Another article in this category already uses the slug."""


def _plain_text(html: str) -> str:
    """Strip tags so the stored text is searchable without markup noise."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "unknown"


def _count_words_from_html(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"\b[\w'-]+\b", text))


def _author_name(author: User) -> str:
    name = " ".join(part for part in (author.first_name, author.last_name) if part).strip()
    return name or author.username or author.email


def _category_slug(article: Article, locale: str = BASE_LOCALE) -> str:
    """The category URL segment. Defaults to Indonesian because the CMS shows the
    canonical one; only the public locale-aware readers pass `locale`."""
    if article.category is None:
        return "articles" if locale == "en" else "artikel"
    return article.category.slug_for(locale)


def _article_image_url(article: Article) -> str:
    images = sorted(article.images, key=lambda image: image.id or 0)
    for image in images:
        if image.cdn_url:
            return image.cdn_url
        if image.image and image.image.startswith(("/", "http://", "https://")):
            return image.image
    return ARTICLE_FALLBACK_IMAGE


def _article_card(article: Article, locale: str = BASE_LOCALE) -> ArticleCard:
    updated_at = article.updated_at or article.published_at or article.created_at
    return ArticleCard(
        id=article.id,
        title=article.title_for(locale),
        slug=article.slug_for(locale),
        category=_category_slug(article, locale),
        summary=article.summary_for(locale),
        image_url=_article_image_url(article),
        author=_author_name(article.author),
        status=article.status,
        featured=article.featured,
        updated_at=updated_at.isoformat() if updated_at else "",
        locale=locale if article.has_translation(locale) else BASE_LOCALE,
        path=article.url_for(locale),
        # Only locales the article genuinely exists in. An English alternate on an
        # article whose body is still Indonesian is a false signal: it earns
        # English impressions for a page that reads as Indonesian, which bounces.
        # The URL keeps working either way -- this governs what is advertised,
        # not what resolves.
        alternates={
            code: article.url_for(code)
            for code in ("id", "en")
            if article.has_translation(code)
        },
    )


class ArticleService:
    # --- admin -------------------------------------------------------------

    async def admin_list(self, session: AsyncSession) -> list[ArticleAdminSummary]:
        """Every article an editor can act on, drafts included. Trashed rows are
        excluded -- delete is a soft delete."""
        query = (
            select(Article)
            .options(selectinload(Article.author), selectinload(Article.category))
            .where(Article.trash.is_(False))
            .order_by(Article.updated_at.desc().nullslast(), Article.id.desc())
        )
        articles = list((await session.execute(query)).scalars().all())

        return [
            ArticleAdminSummary(
                id=article.id,
                title=article.title_id,
                slug=article.slug,
                category=article.category.category if article.category else "",
                category_slug=_category_slug(article),
                status=article.status,
                featured=article.featured,
                word_count=article.word_count or 0,
                # Whether the English side is actually written, so the list can
                # show what still needs translating.
                has_english=article.has_translation("en"),
                published_at=article.published_at.isoformat() if article.published_at else None,
                updated_at=article.updated_at.isoformat() if article.updated_at else None,
            )
            for article in articles
        ]

    async def count(self, session: AsyncSession) -> dict[str, int]:
        """Totals for the dashboard. Trashed articles are excluded because they
        are not part of the catalogue an editor manages."""
        rows = (
            await session.execute(
                select(Article.status, func.count())
                .where(Article.trash.is_(False))
                .group_by(Article.status)
            )
        ).all()
        by_status = {status: total for status, total in rows}
        return {
            "total": sum(by_status.values()),
            "published": by_status.get("published", 0),
            "draft": by_status.get("draft", 0),
            "archived": by_status.get("archived", 0),
        }

    async def admin_detail(self, session: AsyncSession, article_id: int) -> ArticleAdminDetail:
        article = await self._get_for_admin(session, article_id)
        return self._admin_detail(article)

    async def create(
        self, session: AsyncSession, payload: ArticleCreate, author_id: int
    ) -> ArticleAdminDetail:
        category = await self._resolve_category(session, payload.category)
        await self._assert_slug_free(session, category_id=category.id, slug=payload.slug)
        slug_en = (payload.slug_en or "").strip() or None
        if slug_en == payload.slug:
            # Storing the same string twice buys nothing and would then have to be
            # kept in step; the fallback already produces this URL.
            slug_en = None
        if slug_en:
            await self._assert_slug_free(session, category_id=category.id, slug=slug_en)

        article = Article(
            author_id=author_id,
            category_id=category.id,
            title_id=payload.title_id,
            title_en=payload.title_en or None,
            slug=payload.slug,
            slug_en=slug_en,
            summary_id=payload.summary_id,
            summary_en=payload.summary_en or None,
            body_id=payload.body_id,
            body_en=payload.body_en or None,
            content_text=_plain_text(payload.body_id),
            word_count=_count_words_from_html(payload.body_id),
            featured=payload.featured,
            status=payload.status,
            topic=payload.topic,
            published_at=self._published_at_for(payload.status, None),
        )
        # Set before the article is persisted: while it is still pending, reading
        # `article.images` returns an empty collection instead of emitting a lazy
        # load, and the cascade fills in article_id on insert.
        self._set_featured_image(article, payload.image_url)
        session.add(article)
        await session.commit()

        return await self.admin_detail(session, article.id)

    async def update(
        self, session: AsyncSession, article_id: int, payload: ArticleUpdate
    ) -> ArticleAdminDetail:
        article = await self._get_for_admin(session, article_id)
        values = payload.model_dump(exclude_unset=True)

        if (category_slug := values.pop("category", None)) is not None:
            category = await self._resolve_category(session, category_slug)
            article.category_id = category.id

        if (slug := values.get("slug")) is not None and slug != article.slug:
            await self._assert_slug_free(
                session,
                category_id=article.category_id,
                slug=slug,
                exclude_article_id=article.id,
            )

        # Handled before the generic setattr below so a blank value clears the
        # column rather than storing "", which would route the English URL to an
        # empty segment instead of falling back.
        if "slug_en" in values:
            slug_en = (values.pop("slug_en") or "").strip() or None
            if slug_en == (values.get("slug") or article.slug):
                slug_en = None
            if slug_en and slug_en != article.slug_en:
                await self._assert_slug_free(
                    session,
                    category_id=article.category_id,
                    slug=slug_en,
                    exclude_article_id=article.id,
                )
            article.slug_en = slug_en

        # Derived fields track the Indonesian body, which is the canonical text
        # and the one indexed for search.
        if (body_id := values.pop("body_id", None)) is not None:
            article.body_id = body_id
            article.content_text = _plain_text(body_id)
            article.word_count = _count_words_from_html(body_id)

        # Blank English input clears the column so the article falls back
        # rather than publishing an empty translation.
        for field in ("title_en", "summary_en", "body_en"):
            if field in values:
                setattr(article, field, (values.pop(field) or "").strip() or None)

        if (status := values.get("status")) is not None:
            article.published_at = self._published_at_for(status, article.published_at)

        # Lives on article_images rather than on the article row, so it cannot go
        # through the generic setattr below -- Article has no `image_url` attribute
        # and the assignment would be silently discarded.
        if "image_url" in values:
            self._set_featured_image(article, values.pop("image_url"))

        for key, value in values.items():
            setattr(article, key, value)

        await session.commit()
        return await self.admin_detail(session, article_id)

    async def trash(self, session: AsyncSession, article_id: int) -> None:
        """Soft delete: the row survives so published URLs can be restored."""
        article = await self._get_for_admin(session, article_id)
        article.trash = True
        await session.commit()

    def _published_at_for(self, status: str, current: datetime | None) -> datetime | None:
        if status != "published":
            return current
        return current or datetime.now(timezone.utc)

    async def _resolve_category(self, session: AsyncSession, value: str) -> ArticleCategory:
        """Accept a slug or a display name, creating the category if it is new."""
        wanted = _slugify(value)
        category = await session.scalar(
            select(ArticleCategory).where(ArticleCategory.category_slug == wanted)
        )
        if category is None:
            category = ArticleCategory(category=value, category_slug=wanted)
            session.add(category)
            await session.flush()
        return category

    async def _assert_slug_free(
        self,
        session: AsyncSession,
        *,
        category_id: int | None,
        slug: str,
        exclude_article_id: int | None = None,
    ) -> None:
        # Both columns are checked, because the public lookup matches either one:
        # an English slug equal to some other article's Indonesian slug satisfies
        # the unique indexes but leaves the URL resolving to two articles.
        query = select(Article.id).where(
            Article.category_id == category_id,
            or_(Article.slug == slug, Article.slug_en == slug),
        )
        if exclude_article_id is not None:
            query = query.where(Article.id != exclude_article_id)
        if await session.scalar(query) is not None:
            raise ArticleSlugConflictError("Article slug already exists for this category.")

    def _set_featured_image(self, article: Article, image_url: str | None) -> None:
        """Point the article's featured image at `image_url`.

        `_article_image_url()` reads the lowest-id image row, so a write has to land
        on that same row or the value would not survive a round trip. Rewriting the
        row is safe for the article body: body HTML carries its own `<img src>`, and
        `article_images` is only a registry of uploaded files.

        The new row is appended to `article.images` rather than added to the session
        directly. The relationship cascade still writes it, and the in-memory
        collection stays correct -- sessions here run with expire_on_commit=False, so
        a collection that was already loaded is not refreshed by a later query, and
        the response would otherwise report the previous image.

        A blank value means "leave it alone" rather than "clear it", so a form that
        submits an empty field cannot wipe an existing image.
        """
        url = (image_url or "").strip()
        if not url:
            return

        images = sorted(article.images, key=lambda image: image.id or 0)
        if images:
            images[0].cdn_url = url
            return

        article.images.append(
            ArticleImage(
                cdn_url=url,
                image=url,
                filename=url.split("?", 1)[0].rsplit("/", 1)[-1][:255] or None,
            )
        )

    async def _get_for_admin(self, session: AsyncSession, article_id: int) -> Article:
        article = await session.scalar(
            select(Article)
            .options(
                selectinload(Article.author),
                selectinload(Article.category),
                selectinload(Article.images),
            )
            .where(Article.id == article_id, Article.trash.is_(False))
        )
        if article is None:
            raise ArticleNotFoundError("Article not found.")
        return article

    def _admin_detail(self, article: Article) -> ArticleAdminDetail:
        return ArticleAdminDetail(
            id=article.id,
            title_id=article.title_id,
            title_en=article.title_en or "",
            slug=article.slug,
            slug_en=article.slug_en or "",
            summary_id=article.summary_id or "",
            summary_en=article.summary_en or "",
            body_id=article.body_id,
            body_en=article.body_en or "",
            category=article.category.category if article.category else "",
            category_slug=_category_slug(article),
            topic=article.topic or [],
            status=article.status,
            featured=article.featured,
            word_count=article.word_count or 0,
            has_english=article.has_translation("en"),
            image_url=_article_image_url(article),
            author=_author_name(article.author) if article.author else "",
            published_at=article.published_at.isoformat() if article.published_at else None,
            updated_at=article.updated_at.isoformat() if article.updated_at else None,
        )

    # --- public ------------------------------------------------------------

    async def public_articles(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        topic: str | None = None,
        author_slug: str | None = None,
        page: int = 1,
        page_size: int = 12,
        locale: str = BASE_LOCALE,
    ) -> ArticleListResponse:
        articles = await self._published_articles(session, category=category, locale=locale)

        if topic:
            topic_query = topic.casefold()
            articles = [
                article
                for article in articles
                if topic_query in [item.casefold() for item in (article.topic or [])]
            ]
        if author_slug:
            articles = [
                article
                for article in articles
                if _slugify(_author_name(article.author)) == author_slug
                or article.author.username == author_slug
            ]

        total = len(articles)
        start = (page - 1) * page_size
        end = start + page_size
        return ArticleListResponse(
            items=[_article_card(article, locale) for article in articles[start:end]],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=ceil(total / page_size) if total else 0,
            ),
        )

    async def featured_articles(
        self, session: AsyncSession, *, limit: int = 4, locale: str = BASE_LOCALE
    ) -> list[ArticleCard]:
        articles = await self._published_articles(session, locale=locale)
        return [_article_card(article, locale) for article in articles[:limit]]

    async def article_detail(
        self,
        session: AsyncSession,
        *,
        category: str,
        slug: str,
        locale: str = BASE_LOCALE,
    ) -> ArticleDetail:
        articles = await self._published_articles(session, category=category, locale=locale)
        # Either slug resolves, in both locales. An English reader following a
        # link minted before the English slugs existed still lands on the article
        # rather than a 404, and `path` on the response tells the caller which URL
        # is canonical so it can redirect. Indonesian is matched first: it is the
        # canonical column, and only it is guaranteed non-null.
        article = next(
            (item for item in articles if slug in (item.slug, item.slug_en)),
            None,
        )
        if article is None:
            raise ArticleNotFoundError("Article not found.")

        content = article.body_for(locale)
        return ArticleDetail(
            **_article_card(article, locale).model_dump(),
            content=content,
            topic=article.topic or [],
            word_count=article.word_count or _count_words_from_html(content),
            published_at=article.published_at,
        )

    async def _published_articles(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        locale: str = BASE_LOCALE,  # noqa: ARG002 - kept so callers read naturally
    ) -> list[Article]:
        query = (
            select(Article)
            .options(
                selectinload(Article.author),
                selectinload(Article.category),
                selectinload(Article.images),
            )
            .where(
                Article.status == "published",
                Article.trash.is_(False),
            )
            .order_by(Article.featured.desc(), Article.published_at.desc(), Article.id.desc())
        )
        if category:
            # Matched against both segments regardless of locale, for the same
            # reason the article slug is: the English segment is what an English
            # URL carries, and the Indonesian one has to keep working after it.
            query = query.join(ArticleCategory).where(
                or_(
                    ArticleCategory.category_slug == category,
                    ArticleCategory.category_slug_en == category,
                )
            )

        result = await session.execute(query)
        return list(result.scalars().all())


article_service = ArticleService()
