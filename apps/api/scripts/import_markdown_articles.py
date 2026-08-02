"""Import the Markdown articles in apps/web/content/articles into the database.

Article bodies are stored as HTML, so each file's Markdown body is converted on
the way in. The converter handles only the subset these files actually use --
headings, paragraphs, bullet and numbered lists, tables, bold and italic. It is
deliberately not a general Markdown implementation; anything outside that subset
(links, code fences, blockquotes, images) is reported as an error rather than
silently passed through as literal text.

Category slugs in the front matter are mapped onto the existing taxonomy via
CATEGORY_MAP below, so the import does not fragment it with near-duplicates.

    uv run python scripts/import_markdown_articles.py            # dry run
    uv run python scripts/import_markdown_articles.py --commit   # write
"""

from __future__ import annotations

import argparse
import asyncio
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models import Article, ArticleCategory, User
from app.schemas.content import ArticleCreate
from app.services.articles import ArticleService, _slugify

CONTENT_DIR = Path(__file__).resolve().parents[3] / "apps/web/content/articles"

# Front-matter category slug -> display name handed to the service. The service
# slugifies the display name, so each value must slugify back to its key or the
# import would create a second category alongside the intended one.
CATEGORY_MAP = {
    # Existing categories, reused so the import does not duplicate them.
    "persiapan-pernikahan": "Wedding Preparation",
    "adat-tradisi": "Tradisi wedding",
    "venue-lokasi": "Wedding Venue",
    "photography": "Photography",
    # Created on first import.
    "dekorasi": "Dekorasi",
    "beauty-fashion": "Beauty & Fashion",
    "tips-hubungan": "Tips Hubungan",
    "pernikahan-islami": "Pernikahan Islami",
}

# Constructs the converter cannot represent. Matched against the Markdown body
# so a file using them fails loudly instead of importing mangled HTML.
UNSUPPORTED = {
    "link": re.compile(r"\[[^\]]+\]\([^)]+\)"),
    "image": re.compile(r"!\[[^\]]*\]"),
    "code fence": re.compile(r"^```", re.M),
    "blockquote": re.compile(r"^>\s", re.M),
    "heading level 1": re.compile(r"^# ", re.M),
}


class ConversionError(ValueError):
    """The Markdown body uses something the converter does not support."""


@dataclass
class Parsed:
    path: Path
    front: dict[str, str]
    body_md: str
    body_html: str


def split_front_matter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise ConversionError(f"{path.name}: missing front matter")
    _, raw, body = text.split("---", 2)
    front: dict[str, str] = {}
    for line in raw.strip().splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip().strip('"').strip("'")
    return front, body.strip()


def inline(text: str) -> str:
    """Escape the text, then re-introduce the inline tags we support."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    # Single asterisks only; underscores are left alone because Indonesian prose
    # and identifiers use them without meaning emphasis.
    out = re.sub(r"(?<!\*)\*(?!\s)([^*]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", out)
    return out


def convert(md: str, path: Path) -> str:
    for label, pattern in UNSUPPORTED.items():
        if pattern.search(md):
            raise ConversionError(f"{path.name}: unsupported Markdown ({label})")

    lines = md.splitlines()
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if heading := re.match(r"^(#{2,4})\s+(.*)$", stripped):
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Table: a header row, a separator row of dashes, then body rows.
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            body_rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body_rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head_html = "".join(f"<th>{inline(c)}</th>" for c in header)
            rows_html = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                for row in body_rows
            )
            out.append(
                f"<table><thead><tr>{head_html}</tr></thead><tbody>{rows_html}</tbody></table>"
            )
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue

        # Paragraph: consecutive plain lines up to the next blank or block start.
        para: list[str] = []
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or re.match(r"^(#{2,4}\s|[-*]\s|\d+\.\s|\|)", nxt):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


def parse_file(path: Path) -> Parsed:
    front, body = split_front_matter(path.read_text(encoding="utf-8"), path)
    for key in ("title_id", "slug", "category", "excerpt_id"):
        if not front.get(key):
            raise ConversionError(f"{path.name}: missing front-matter key '{key}'")
    if front["category"] not in CATEGORY_MAP:
        raise ConversionError(f"{path.name}: unmapped category '{front['category']}'")
    return Parsed(path=path, front=front, body_md=body, body_html=convert(body, path))


async def resolve_author(session, username: str) -> User:
    user = await session.scalar(select(User).where(User.username == username.casefold()))
    if user is None:
        raise SystemExit(f"No user with username '{username.casefold()}' -- pass --author")
    return user


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="write to the database")
    parser.add_argument("--author", default="fiona", help="username to attribute articles to")
    parser.add_argument("--status", default="draft", choices=["draft", "published", "archived"])
    args = parser.parse_args()

    files = sorted(CONTENT_DIR.glob("*.md"))
    if not files:
        raise SystemExit(f"No Markdown files in {CONTENT_DIR}")

    parsed: list[Parsed] = []
    failures: list[str] = []
    for path in files:
        try:
            parsed.append(parse_file(path))
        except ConversionError as exc:
            failures.append(str(exc))

    if failures:
        print(f"{len(failures)} file(s) could not be converted:")
        for message in failures:
            print("  !", message)
        raise SystemExit(1)

    service = ArticleService()
    async with AsyncSessionLocal() as session:
        author = await resolve_author(session, args.author)

        # (category_slug, article_slug) pairs already stored, so a dry run reports
        # the same skips a real run would take instead of over-counting.
        existing = {
            (row.category_slug, row.slug)
            for row in (
                await session.execute(
                    select(ArticleCategory.category_slug, Article.slug).join(
                        ArticleCategory, Article.category_id == ArticleCategory.id
                    )
                )
            ).all()
        }
        created = skipped = 0

        for item in parsed:
            payload = ArticleCreate(
                title_id=item.front["title_id"],
                title_en=item.front.get("title_en") or None,
                slug=item.front["slug"],
                summary_id=item.front["excerpt_id"],
                body_id=item.body_html,
                category=CATEGORY_MAP[item.front["category"]],
                status=args.status,
            )
            # The stored slug comes from the mapped display name, not the
            # front-matter key -- 'persiapan-pernikahan' is filed as
            # 'wedding-preparation'.
            if (_slugify(payload.category), payload.slug) in existing:
                print(f"  already present, skipping  {payload.slug}  [{payload.category}]")
                skipped += 1
                continue

            tags = f"{len(item.body_html)} chars html"
            if not args.commit:
                print(f"  would create  {payload.slug}  [{payload.category}]  {tags}")
                created += 1
                continue
            try:
                detail = await service.create(session, payload, author.id)
                print(f"  created  id={detail.id}  {payload.slug}  [{payload.category}]")
                created += 1
            except Exception as exc:  # slug conflict or validation
                print(f"  ! skipped {payload.slug}: {exc}")
                skipped += 1

        verb = "would create" if not args.commit else "created"
        print(f"\n{verb} {created}, skipped {skipped}, author={author.username}, status={args.status}")
        if not args.commit:
            print("Dry run -- re-run with --commit to write.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
