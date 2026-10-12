"""Re-import the Indonesian body of articles that already exist.

`import_markdown_articles.py` only creates: it skips any slug already in the
database, so an edit to a published article's Markdown (a fixed link, an added
figure) never reaches the page. This re-converts the named files and writes
`body_id` through `ArticleService.update`, which also recomputes the search text
and word count that track the Indonesian body.

English is not touched here. Run `import_article_translations_md.py` afterwards:
it rewrites `body_en` from `content/articles/en/` and refuses any file whose tag
stream no longer matches the refreshed Indonesian body, so the two cannot drift.

    uv run python scripts/refresh_article_body.py <slug> [<slug> ...]            # dry run
    uv run python scripts/refresh_article_body.py <slug> [<slug> ...] --commit
    uv run python scripts/import_article_translations_md.py --commit
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from import_markdown_articles import CONTENT_DIR, ConversionError, parse_file
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article
from app.schemas.content import ArticleUpdate
from app.services.articles import ArticleService


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="+", help="article slugs, as in the Markdown front matter")
    parser.add_argument("--commit", action="store_true", help="write to the database")
    args = parser.parse_args()

    service = ArticleService()
    async with AsyncSessionLocal() as session:
        for slug in args.slugs:
            path = CONTENT_DIR / f"{slug}.md"
            if not path.exists():
                raise SystemExit(f"! no Markdown file for '{slug}' in {CONTENT_DIR}")
            try:
                body_id = parse_file(path).body_html
            except ConversionError as exc:
                raise SystemExit(f"! {exc}") from exc

            article = await session.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                raise SystemExit(f"! not in database: {slug} -- import it first")
            if article.body_id == body_id:
                print(f"  unchanged  {slug}")
                continue

            print(
                f"  {'' if args.commit else 'would '}refresh  {slug}  "
                f"({len(article.body_id or '')} -> {len(body_id)} chars html)"
            )
            if args.commit:
                await service.update(session, article.id, ArticleUpdate(body_id=body_id))
    await engine.dispose()

    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
