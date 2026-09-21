"""Load the English translations in apps/web/content/articles/en into the database.

The Markdown-authored articles keep their English beside the Indonesian source:
`articles/<slug>.md` is canonical, `articles/en/<slug>.md` is its translation,
written block for block against it. Both go through the converter in
`import_markdown_articles.py`, so matching Markdown gives matching HTML.

That match is enforced rather than trusted, by the same rule as
`translate_new_articles_to_en.py`: the tag stream of `body_en` must equal that of
the stored `body_id`, because heading order drives the table of contents and a
dropped list or link is otherwise invisible until a reader finds it. Any mismatch
aborts the run before anything is written, and names the first tag that differs.

Front matter of a translation file: `slug` (the Indonesian slug it translates),
`slug_en`, `title_en`, `excerpt_en`. Re-running overwrites the English fields, so
an edited translation is applied by running this again.

    uv run python scripts/import_article_translations_md.py            # dry run
    uv run python scripts/import_article_translations_md.py --commit
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from import_markdown_articles import CONTENT_DIR, ConversionError, convert, split_front_matter
from sqlalchemy import or_, select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article

EN_DIR = CONTENT_DIR / "en"
REQUIRED = ("slug", "slug_en", "title_en", "excerpt_en")


class TagStream(HTMLParser):
    """The tags of a document with every text node discarded.

    A third copy of the reader in `validate_article_translations.py`, for the
    reason the second one gives: the check has to run before the write.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, tuple]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, tuple(sorted(attrs))))

    def handle_endtag(self, tag):
        self.tags.append((f"/{tag}", ()))


def tag_stream(html: str) -> list[tuple[str, tuple]]:
    parser = TagStream()
    parser.feed(html)
    return parser.tags


def first_difference(source: list, translated: list) -> str:
    for index, (left, right) in enumerate(zip(source, translated, strict=False)):
        if left != right:
            return f"tag {index}: Indonesian has {left}, English has {right}"
    return f"Indonesian has {len(source)} tags, English has {len(translated)}"


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    args = parser.parse_args()

    files = sorted(EN_DIR.glob("*.md"))
    if not files:
        raise SystemExit(f"No translation files in {EN_DIR}")

    failures: list[str] = []
    ready: list[tuple[Article, dict[str, str], str]] = []

    async with AsyncSessionLocal() as session:
        for path in files:
            try:
                front, body = split_front_matter(path.read_text(encoding="utf-8"), path)
                missing = [key for key in REQUIRED if not front.get(key)]
                if missing:
                    raise ConversionError(f"{path.name}: missing front matter {missing}")
                body_en = convert(body, path)
            except ConversionError as exc:
                failures.append(str(exc))
                continue

            article = await session.scalar(select(Article).where(Article.slug == front["slug"]))
            if article is None:
                failures.append(f"{path.name}: no article with slug '{front['slug']}'")
                continue

            source, translated = tag_stream(article.body_id), tag_stream(body_en)
            if source != translated:
                failures.append(f"{path.name}: {first_difference(source, translated)}")
                continue

            # Either column resolves a public URL, so the English slug must not
            # collide with any other article's slug in either language.
            clash = await session.scalar(
                select(Article.slug).where(
                    Article.id != article.id,
                    Article.category_id == article.category_id,
                    or_(Article.slug == front["slug_en"], Article.slug_en == front["slug_en"]),
                )
            )
            if clash:
                failures.append(f"{path.name}: slug_en already used by '{clash}'")
                continue

            ready.append((article, front, body_en))

        if failures:
            print(f"{len(failures)} translation(s) rejected, nothing written:")
            for message in failures:
                print("  !", message)
            await engine.dispose()
            raise SystemExit(1)

        for article, front, body_en in ready:
            verb = "translated" if args.commit else "would translate"
            print(f"  {verb}  {article.slug}  ->  {front['slug_en']}  ({len(body_en)} chars)")
            if args.commit:
                article.title_en = front["title_en"]
                article.slug_en = front["slug_en"]
                article.summary_en = front["excerpt_en"]
                article.body_en = body_en
        if args.commit:
            await session.commit()
    await engine.dispose()

    print(f"\n{len(ready)} translation(s) {'written' if args.commit else 'valid'}")
    if not args.commit:
        print("Dry run -- re-run with --commit to write.")


if __name__ == "__main__":
    asyncio.run(main())
