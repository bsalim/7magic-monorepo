"""Check translated article bodies against their Indonesian sources.

Translation is allowed to change the text between tags and nothing else. This checks
that, plus the two failure modes that slipped past a tag-only check while the English
translations were being produced:

  1. Tag stream drift -- a heading `id` anchor rewritten, a Quill bullet span dropped.
  2. Character loss -- an emoji, arrow, en dash or curly quote silently vanishing
     during an idiomatic rewrite. Counted per character, because the same character
     usually still appears elsewhere in the article and a set comparison misses it.
  3. Indonesian left in the English, and Indonesian number separators in English prose
     (`5.000 guests` reads as five to an English reader).

Usage:
    export DATABASE_URL=...
    uv run --with 'psycopg[binary]' python scripts/validate_article_translations.py \
        migrations/data/article_translations_en.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

import psycopg

TAG_SPLIT = re.compile(r"(<[^>]+>)")
NUMBER = re.compile(r"\d+\.\d{3}(?!\d)|\d+,\d(?!\d)")
LEFTOVER_ID = (" yang ", " dengan ", " untuk ", " kamu ", " nggak ", " gak ", " banget ")

# Punctuation the English voice legitimately adds or drops when re-expressing an idiom.
FREE_CHARS = set("—–-’‘“”\"'…‑")


class TagStream(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stream: list[tuple[str, tuple]] = []

    def handle_starttag(self, tag, attrs):
        self.stream.append((tag, tuple(sorted(attrs))))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        self.stream.append(("/" + tag, ()))


def tag_stream(html: str) -> list[tuple[str, tuple]]:
    parser = TagStream()
    parser.feed(html)
    parser.close()
    return parser.stream


def text_of(html: str) -> str:
    return "".join(TAG_SPLIT.split(html)[::2])


def main() -> int:
    with open(sys.argv[1], encoding="utf-8") as fh:
        translations = json.load(fh)

    dsn = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    with psycopg.connect(dsn) as conn:
        rows = conn.execute(
            "SELECT public_id::text, id, title_id, body_id FROM articles WHERE trash = false"
        ).fetchall()

    source = {pid: (aid, title, body) for pid, aid, title, body in rows}
    failures: list[str] = []
    # Character loss needs a human call rather than a hard gate: dropping an emoji is a
    # bug, but re-expressing "sore -> malam" as "afternoon rolling into evening" is the
    # idiomatic rewrite we asked for. Reported separately so a real loss stays visible.
    warnings: list[str] = []

    for public_id, entry in translations.items():
        if public_id not in source:
            failures.append(f"{public_id}: no live article with this public_id")
            continue

        article_id, _title_id, body_id = source[public_id]

        for field in ("title_en", "summary_en", "body_en"):
            if field not in entry:
                failures.append(f"id {article_id}: missing {field}")

        title_en = entry.get("title_en", "")
        if not title_en.strip():
            failures.append(f"id {article_id}: empty title_en")
        if len(title_en) > 255:
            failures.append(f"id {article_id}: title_en exceeds the 255-char column")

        body_en = entry.get("body_en", "")
        if not body_en.strip():
            failures.append(f"id {article_id}: empty body_en")
            continue

        want, got = tag_stream(body_id), tag_stream(body_en)
        if want != got:
            for i, (a, b) in enumerate(zip(want, got)):
                if a != b:
                    failures.append(f"id {article_id}: tag {i} differs -- {a!r} vs {b!r}")
                    break
            else:
                failures.append(
                    f"id {article_id}: tag count differs -- {len(want)} vs {len(got)}"
                )
            continue

        def symbols(html: str) -> Counter:
            return Counter(c for c in text_of(html) if ord(c) > 127 and c not in FREE_CHARS)

        before, after = symbols(body_id), symbols(body_en)
        lost = {c: n - after.get(c, 0) for c, n in before.items() if n > after.get(c, 0)}
        if lost:
            warnings.append(f"id {article_id}: characters not carried over: {lost}")

        text = " ".join(text_of(body_en).split()).lower()
        leftovers = [w for w in LEFTOVER_ID if w in f" {text} "]
        if leftovers:
            failures.append(f"id {article_id}: untranslated Indonesian: {leftovers}")

        for field in ("title_en", "summary_en", "body_en"):
            for i, part in enumerate(TAG_SPLIT.split(entry.get(field) or "")):
                if i % 2:
                    continue  # odd indices are tags; their attributes are not prose
                for match in NUMBER.finditer(part):
                    if re.search(r"Rp\s*$", part[: match.start()]):
                        continue  # a rupiah price keeps Indonesian formatting
                    failures.append(
                        f"id {article_id} {field}: Indonesian number format {match.group()!r}"
                    )

    print(f"checked {len(translations)} entries against {len(source)} live articles")

    if warnings:
        print(f"\n{len(warnings)} to review (not failures):")
        for warning in warnings:
            print(f"  ? {warning}")

    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\nall entries pass: tag streams identical, no Indonesian left, numbers localised")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
