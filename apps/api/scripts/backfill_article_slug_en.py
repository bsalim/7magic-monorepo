"""Fill in the English URL slugs that `slug_en` added.

Articles carried one slug for both languages, so an English article sat at the
Indonesian URL. This derives an English slug from `title_en` for every article
that genuinely has an English translation, and copies the reviewed English
segment onto each category.

Two rules keep the result stable rather than merely unique:

1. A slug that would come out identical to the Indonesian one is left NULL.
   `slug_for()` falls back, so the URL is the same either way, and a NULL says
   "this article has no English URL of its own" instead of duplicating the value
   in two columns that then have to be kept in step.
2. Uniqueness is checked against `slug` *and* `slug_en` within the category, not
   just `slug_en`. The public lookup matches either column, so an English slug
   that collides with some other article's Indonesian slug would make the URL
   ambiguous even though the unique index is satisfied.

Re-running is safe: rows that already have a slug_en are left alone unless
--force is passed, which is the escape hatch for a category rename.

    uv run python scripts/backfill_article_slug_en.py --dry-run
    uv run python scripts/backfill_article_slug_en.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models import Article, ArticleCategory

CATEGORY_SLUGS = Path(__file__).resolve().parents[1] / "migrations/data/article_category_slugs_en.json"


def slugify(value: str) -> str:
    """Kept in step with `app.services.articles._slugify` deliberately.

    Importing it would tie a one-shot script to the service layer's import
    graph; the rule is three lines and changing it would be a URL change worth
    noticing in both places.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "unknown"


def load_category_slugs() -> dict[str, str]:
    raw = json.loads(CATEGORY_SLUGS.read_text(encoding="utf-8"))
    return {key: value for key, value in raw.items() if not key.startswith("_")}


def unique_slug(candidate: str, taken: set[str]) -> str:
    """`candidate`, or the first free `candidate-2`, `candidate-3`, ... after it."""
    if candidate not in taken:
        return candidate
    suffix = 2
    while f"{candidate}-{suffix}" in taken:
        suffix += 1
    return f"{candidate}-{suffix}"


async def run(dry_run: bool, force: bool) -> int:
    mapping = load_category_slugs()
    planned_categories: list[tuple[str, str]] = []
    planned_articles: list[tuple[int, str, str]] = []
    skipped_same = 0
    skipped_untranslated = 0

    async with AsyncSessionLocal() as session:
        categories = list((await session.execute(select(ArticleCategory))).scalars().all())
        by_slug = {category.category_slug: category for category in categories}

        unknown = sorted(set(mapping) - set(by_slug))
        if unknown:
            print(f"error: mapping names categories that do not exist: {', '.join(unknown)}")
            return 1

        for slug, english in mapping.items():
            category = by_slug[slug]
            if category.category_slug_en == english:
                continue
            if category.category_slug_en and not force:
                print(f"  keep   category {slug} -> {category.category_slug_en} (use --force to change)")
                continue
            planned_categories.append((slug, english))
            if not dry_run:
                category.category_slug_en = english

        articles = list(
            (
                await session.execute(
                    select(Article)
                    .options(selectinload(Article.category))
                    .where(Article.trash.is_(False))
                    .order_by(Article.category_id, Article.id)
                )
            )
            .scalars()
            .all()
        )

        # Seeded per category with every slug already spoken for in either column,
        # so a generated English slug cannot shadow another article's URL.
        taken: dict[int | None, set[str]] = {}
        for article in articles:
            slugs = taken.setdefault(article.category_id, set())
            slugs.add(article.slug)
            if article.slug_en:
                slugs.add(article.slug_en)

        for article in articles:
            if article.slug_en and not force:
                continue
            if not article.has_translation("en"):
                skipped_untranslated += 1
                continue

            slugs = taken[article.category_id]
            # Its own slugs are not competitors when recomputing in --force mode.
            slugs.discard(article.slug_en or "")
            candidate = slugify(article.title_en or "")

            if candidate == article.slug:
                skipped_same += 1
                if article.slug_en and not dry_run:
                    article.slug_en = None
                continue

            resolved = unique_slug(candidate, slugs)
            slugs.add(resolved)
            planned_articles.append((article.id, article.slug, resolved))
            if not dry_run:
                article.slug_en = resolved

        for slug, english in planned_categories:
            print(f"  category {slug} -> {english}")
        for article_id, slug, resolved in planned_articles:
            print(f"  article {article_id:>4}  {slug} -> {resolved}")

        print(
            f"\n{len(planned_categories)} categories, {len(planned_articles)} articles to update; "
            f"{skipped_same} already match their Indonesian slug, "
            f"{skipped_untranslated} have no English translation"
        )

        if dry_run:
            print("dry run -- nothing written")
            return 0

        await session.commit()
        print("written")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report the plan, write nothing")
    parser.add_argument(
        "--force",
        action="store_true",
        help="recompute slugs that are already set (changes live English URLs)",
    )
    args = parser.parse_args()
    return asyncio.run(run(args.dry_run, args.force))


if __name__ == "__main__":
    raise SystemExit(main())
