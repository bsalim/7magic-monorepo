"""Tidy AI-generated markup in article bodies.

Two fixes, both one-off:

1. Numbered emoji used as list markers (1️⃣ 2️⃣ …) become a real <ol>, so the
   numbering is styled by CSS instead of baked into the text.
2. Checkbox emoji that merely prefix a heading or paragraph (☑️ ✅ 🚫 …) are
   removed. They read as decoration the heading already conveys.

Decorative emoji elsewhere (📍 ✨ 💍 …) are left alone -- they carry tone rather
than structure, and stripping them would change how the articles read.

    uv run python scripts/clean_article_content.py --dry-run
    uv run python scripts/clean_article_content.py
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core.database import engine

# ☑️ and friends when they open a heading or paragraph, plus any following space.
LEADING_CHECKBOX = re.compile(
    r"(<(?:p|h2|h3|h4|li)[^>]*>)\s*(?:[✅☑❌✔\U0001F6AB]️?\s*)+"
)

# A run of "<p>1️⃣ text</p>" siblings that should have been an ordered list.
NUMBERED_PARAGRAPH = re.compile(
    r"<p[^>]*>\s*[0-9#*]️?⃣\s*(.*?)</p>", re.DOTALL
)

# Any leftover keycap emoji sitting inline.
INLINE_KEYCAP = re.compile(r"[0-9#*]️?⃣\s*")


def convert_numbered_paragraphs(html: str) -> tuple[str, int]:
    """Turn consecutive keycap paragraphs into a single <ol>."""
    matches = list(NUMBERED_PARAGRAPH.finditer(html))
    if not matches:
        return html, 0

    # Group runs that are adjacent in the source, so unrelated numbered
    # paragraphs elsewhere in the article do not get merged into one list.
    runs: list[list[re.Match[str]]] = [[matches[0]]]
    for match in matches[1:]:
        if match.start() - runs[-1][-1].end() <= 2:
            runs[-1].append(match)
        else:
            runs.append([match])

    converted = 0
    for run in reversed(runs):
        items = "".join(f"<li>{m.group(1).strip()}</li>" for m in run)
        html = html[: run[0].start()] + f"<ol>{items}</ol>" + html[run[-1].end() :]
        converted += len(run)

    return html, converted


def clean(html: str) -> tuple[str, dict[str, int]]:
    stats = {"checkbox": 0, "numbered": 0, "keycap": 0}

    cleaned, stats["checkbox"] = LEADING_CHECKBOX.subn(r"\1", html)
    cleaned, stats["numbered"] = convert_numbered_paragraphs(cleaned)
    cleaned, stats["keycap"] = INLINE_KEYCAP.subn("", cleaned)

    return cleaned, stats


def plain_text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def word_count(html: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", plain_text(html)))


async def run(dry_run: bool) -> int:
    async with engine.connect() as connection:
        rows = (
            await connection.execute(
                text("SELECT id, title, content_html FROM articles WHERE trash = false")
            )
        ).all()

    changes = []
    totals = {"checkbox": 0, "numbered": 0, "keycap": 0}

    for row in rows:
        original = row.content_html or ""
        cleaned, stats = clean(original)
        if cleaned == original:
            continue
        for key in totals:
            totals[key] += stats[key]
        changes.append((row.id, row.title, cleaned, stats))

    print(f"articles scanned : {len(rows)}")
    print(f"articles changed : {len(changes)}")
    print(f"  checkbox emoji removed : {totals['checkbox']}")
    print(f"  numbered items -> <ol>  : {totals['numbered']}")
    print(f"  stray keycaps removed   : {totals['keycap']}")
    print()

    for article_id, title, _, stats in changes[:12]:
        detail = ", ".join(f"{k}={v}" for k, v in stats.items() if v)
        print(f"  #{article_id:4} {title[:46]:48} {detail}")
    if len(changes) > 12:
        print(f"  ... and {len(changes) - 12} more")

    if dry_run:
        print("\nDry run -- nothing written.")
        return 0

    async with engine.begin() as connection:
        for article_id, _, cleaned, _ in changes:
            await connection.execute(
                text(
                    """
                    UPDATE articles
                    SET content_html = :html,
                        content_text = :plain,
                        word_count = :words
                    WHERE id = :id
                    """
                ),
                {
                    "id": article_id,
                    "html": cleaned,
                    "plain": plain_text(cleaned),
                    "words": word_count(cleaned),
                },
            )

    print(f"\nUpdated {len(changes)} articles.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report changes, write nothing")
    args = parser.parse_args()
    return asyncio.run(run(args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
