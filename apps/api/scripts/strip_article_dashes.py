"""Replace em dashes (and spaced en dashes) in article titles, summaries and bodies.

The dash-as-pause is the most recognisable tell of machine-written copy, and
the archive carries well over a thousand of them. Each one is swapped for the
punctuation a person would have typed, decided from where it sits:

* in a title or heading, a colon ("Mapag Panganten: Menyambut ..."), except a
  trailing place ("Holiday Inn Resort Baruna, Kuta") and a song credit after an
  italic title, which becomes "(Artist)";
* after a short lead-in at the start of a paragraph or list item, a colon
  ("<strong>Navy</strong>: biru tua ...");
* two in one sentence, brackets around the aside;
* next to other punctuation or at the edge of a block, nothing;
* before a clause that has commas of its own, a colon;
* anywhere else in prose, a comma.

En dashes in ranges ("20–100 pax", "Mei–Oktober") are correct typography and
stay. Only text nodes are touched, so image filenames and hrefs that happen to
contain a dash are safe. `content_text` is rebuilt from the new `body_id`.

    uv run python scripts/strip_article_dashes.py              # dry run
    uv run python scripts/strip_article_dashes.py --commit
    uv run python scripts/strip_article_dashes.py --markdown   # also rewrite apps/web/content/articles

Idempotent: a second run finds nothing to change.
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
from app.services.articles import _plain_text

CONTENT_DIR = Path(__file__).resolve().parents[3] / "apps/web/content/articles"

# Em dash anywhere; en dash only when spaced or between two lowercase words
# ("kota besar–sempurna"), which leaves numeric and month ranges alone.
DASH = re.compile(r"\s*(?:—|(?:(?<=\s)|^)–(?=\s|$)|(?<=[a-z])–(?=[a-z]))\s*")

TAG = re.compile(r"(<[^>]+>)")
BLOCK_OPEN = re.compile(r"<(p|li|h[1-6]|td|th|figcaption|blockquote|dt|dd)\b", re.I)
BLOCK_CLOSE = re.compile(r"</(p|li|h[1-6]|td|th|figcaption|blockquote|dt|dd)>", re.I)
HEADING_OPEN = re.compile(r"<h[1-6]\b", re.I)
HEADING_CLOSE = re.compile(r"</h[1-6]>", re.I)
ITALIC_CLOSE = re.compile(r"</(em|i)>$", re.I)

# Suffixes that name where a venue is, not what it is about. A colon in front
# of them reads oddly ("Baruna: Kuta"), a comma reads like an address.
PLACES = re.compile(
    r"\b(Kuta|Tuban|Uluwatu|Tabanan|Seminyak|Ungasan|Canggu|Ubud|Nusa Dua|Jimbaran|"
    r"Sanur|Bali|Diponegoro|Jakarta|Singapore|Singapura|Villa Tamarama)\b"
)

# Venue names that carry a dash officially. Dropping it keeps the name whole,
# where a comma or colon would read as two separate things.
NAMES = re.compile(r"(Hilton Jakarta)\s*[—–]\s*(Diponegoro)")
INLINE_CLOSE = re.compile(r"</(strong|b|em|i|a|u)>$", re.I)

PUNCT_BEFORE = tuple(".,;:!?")
OPEN_BEFORE = tuple("(“‘")
QUOTE_BEFORE = tuple("\"”’'")
PUNCT_AFTER = tuple(".,;:!?\"”’)")
SENTENCE_END = re.compile(r"[.!?][\"”’)]*(?:\s|$)")


def _sentence_after(after: str) -> str:
    end = SENTENCE_END.search(after)
    return after[: end.start()] if end else after


def _sentence_before(before: str) -> str:
    ends = list(SENTENCE_END.finditer(before))
    return before[ends[-1].end():] if ends else before


def _replacement(before: str, after: str, *, heading: bool, after_italic: bool,
                 first_in_block: bool, label_slot: bool, aside_open: bool) -> tuple[str, str]:
    """Return (replacement, kind); kind is "song", "open", "close" or ""."""
    before_s, after_s = before.rstrip(), after.lstrip()
    if aside_open:
        return (")" if after_s.startswith(PUNCT_AFTER) or not after_s.strip() else ") "), "close"
    if not before_s.strip() or not after_s.strip():
        return "", ""
    if before_s.endswith(OPEN_BEFORE):
        return "", ""
    if before_s.endswith(PUNCT_BEFORE):
        return " ", ""
    if before_s.endswith(QUOTE_BEFORE):
        return (" " if before_s.rstrip("\"”’'").endswith(PUNCT_BEFORE) else ", "), ""
    if after_s.startswith(PUNCT_AFTER):
        return "", ""

    if heading:
        if after_italic:
            return " (", "song"  # closed at the end of the heading
        tail = DASH.split(after_s, maxsplit=1)[0]
        if len(tail.split()) <= 4 and PLACES.search(tail):
            return ", ", ""
        return (": " if first_in_block else ", "), ""

    # Two dashes in one sentence fence off an aside; brackets say that
    # without the run of commas that swapping both would leave.
    sentence_after = _sentence_after(after_s)
    if DASH.search(sentence_after):
        return " (", "open"

    # "Name — what it is" in a list item or after a bold label.
    lead = re.sub(r"&#?\w+;", "&", before_s).strip()  # "&amp;" is not a semicolon
    if (label_slot and first_in_block and len(lead.split()) <= 6
            and not re.search(r"[.!?,;:]", lead) and not DASH.search(after_s)):
        return ": ", ""

    # A lone dash introducing a clause that already has commas of its own
    # would become a run-on with a comma; a colon keeps the break visible.
    if "," in sentence_after and ":" not in _sentence_before(before_s):
        return ": ", ""
    return ", ", ""


def _rewrite_text(segment: str, block_before: str, block_after: str, *, heading: bool,
                  after_italic: bool, label_slot: bool, state: dict) -> int:
    """Rewrite the dashes in one text node, updating `state` in place."""
    out, pos, count = [], 0, 0
    for match in DASH.finditer(segment):
        before = block_before + "".join(out) + segment[pos:match.start()]
        after = segment[match.end():] + block_after
        repl, kind = _replacement(
            before,
            after,
            heading=heading,
            after_italic=after_italic and match.start() == 0 and heading,
            first_in_block=state["dashes"] == 0,
            label_slot=label_slot,
            aside_open=state["aside"],
        )
        if kind == "song":
            state["song"] = True
        elif kind in ("open", "close"):
            state["aside"] = kind == "open"
        out.append(segment[pos:match.start()])
        out.append(repl)
        pos = match.end()
        count += 1
        state["dashes"] += 1
    out.append(segment[pos:])
    state["text"] = "".join(out)
    return count


def strip_html(html: str) -> tuple[str, int]:
    tokens = TAG.split(html)
    total = 0
    block_text = ""
    block_tag = ""
    heading = False
    state = {"dashes": 0, "aside": False, "song": False, "text": ""}

    for i, token in enumerate(tokens):
        if i % 2 == 1:  # a tag
            if opened := BLOCK_OPEN.match(token):
                block_text = ""
                block_tag = opened.group(1).lower()
                state.update(dashes=0, aside=False, song=False)
            if HEADING_OPEN.match(token):
                heading = True
            if HEADING_CLOSE.match(token):
                if state["song"]:
                    tokens[i - 1] = tokens[i - 1].rstrip() + ")"
                    state["song"] = False
                heading = False
            continue
        token, renamed = NAMES.subn(r"\1 \2", token)
        total += renamed
        tokens[i] = token
        if "—" not in token and "–" not in token:
            block_text += token
            continue

        # Plain text that follows this node up to the end of its block, so a
        # dash right before "</p>" is seen as trailing.
        rest = []
        for j in range(i + 1, len(tokens)):
            if j % 2 == 1 and BLOCK_CLOSE.match(tokens[j]):
                break
            if j % 2 == 0:
                rest.append(tokens[j])
        previous_tag = tokens[i - 1] if i else ""
        total += _rewrite_text(
            token,
            block_text,
            "".join(rest),
            heading=heading,
            after_italic=bool(ITALIC_CLOSE.search(previous_tag)),
            label_slot=block_tag == "li" or bool(INLINE_CLOSE.search(previous_tag)),
            state=state,
        )
        tokens[i] = state["text"]
        block_text += state["text"]

    return "".join(tokens), total


def strip_line(line: str, *, heading: bool, listed: bool = False) -> tuple[str, int]:
    """A title, summary or markdown line, treated as one block."""
    if "—" not in line and "–" not in line:
        return line, 0
    tag = "h2" if heading else "li" if listed else "p"
    html, count = strip_html(f"<{tag}>{line}</{tag}>")
    return html[len(tag) + 2 : -(len(tag) + 3)], count


# Markdown links and bare URLs are protected the way tags are in HTML.
MD_PROTECT = re.compile(r"(\]\([^)]*\)|https?://\S+|`[^`]*`)")
MD_ITALIC_SONG = re.compile(r"^(\s*#+\s.*?\*[^*]+\*)\s*[—–]\s*(.+)$")
FRONT_MATTER_TEXT = re.compile(r"^(title|excerpt|summary|description)(_id|_en)?:")


def strip_markdown(source: str) -> tuple[str, int]:
    lines = source.split("\n")
    total = 0
    in_front = lines[:1] == ["---"]
    for n, line in enumerate(lines):
        if n and in_front and line == "---":
            in_front = False
            continue
        if in_front and not FRONT_MATTER_TEXT.match(line):
            continue
        song = MD_ITALIC_SONG.match(line)
        if song:
            lines[n] = f"{song.group(1)} ({song.group(2).strip()})"
            total += 1
            continue
        heading = line.lstrip().startswith("#") or (in_front and line.startswith("title"))
        listed = bool(re.match(r"^\s*(?:[-*]|\d+\.)\s", line))
        prefix = re.match(r"^(\s*(?:#+|[-*]|\d+\.)?\s*)", line).group(1) if not in_front else ""
        body = line[len(prefix):]
        parts = MD_PROTECT.split(body)
        # Rewrite the line as one block; protected parts become opaque tags.
        joined = "".join(p if k % 2 == 0 else f"<x{k}>" for k, p in enumerate(parts))
        new, count = strip_line(joined, heading=heading, listed=listed)
        for k, p in enumerate(parts):
            if k % 2:
                new = new.replace(f"<x{k}>", p, 1)
        lines[n] = prefix + new
        total += count
    return "\n".join(lines), total


SINGLE_LINE = {"title_id": True, "title_en": True, "summary_id": False,
               "summary_en": False, "image_caption": True}
BODIES = ("body_id", "body_en")


async def run_db(commit: bool, show: int) -> None:
    columns = ", ".join(("id", "slug", *SINGLE_LINE, *BODIES))
    async with engine.connect() as connection:
        rows = (await connection.execute(text(f"SELECT {columns} FROM articles ORDER BY id"))).all()

    changes: list[tuple[int, dict[str, str]]] = []
    totals = dict.fromkeys((*SINGLE_LINE, *BODIES), 0)
    for row in rows:
        updates = {}
        for column, heading in SINGLE_LINE.items():
            value = getattr(row, column)
            if value:
                new, count = strip_line(value, heading=heading)
                if count:
                    updates[column], totals[column] = new, totals[column] + count
        for column in BODIES:
            value = getattr(row, column)
            if value:
                new, count = strip_html(value)
                if count:
                    updates[column], totals[column] = new, totals[column] + count
        if updates:
            changes.append((row.id, updates))

    print(f"articles scanned : {len(rows)}")
    print(f"articles changed : {len(changes)}")
    for column, count in totals.items():
        print(f"  {column:14} {count}")

    for article_id, updates in changes[:show]:
        for column in SINGLE_LINE:
            if column in updates:
                print(f"\n  #{article_id} {column}: {updates[column]}")

    if not commit:
        print("\nDry run, nothing written. Re-run with --commit.")
        return

    async with engine.begin() as connection:
        for article_id, updates in changes:
            if "body_id" in updates:
                updates["content_text"] = _plain_text(updates["body_id"])
            assignments = ", ".join(f"{column} = :{column}" for column in updates)
            await connection.execute(
                text(f"UPDATE articles SET {assignments} WHERE id = :id"),
                {**updates, "id": article_id},
            )
    print(f"\nUpdated {len(changes)} articles.")


def run_markdown(commit: bool) -> None:
    changed = 0
    for path in sorted(CONTENT_DIR.rglob("*.md")):
        source = path.read_text()
        new, count = strip_markdown(source)
        if count:
            changed += 1
            print(f"  {path.relative_to(CONTENT_DIR)}: {count}")
            if commit:
                path.write_text(new)
    print(f"markdown files {'rewritten' if commit else 'to rewrite'}: {changed}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--commit", action="store_true", help="write the changes")
    parser.add_argument("--markdown", action="store_true", help="also rewrite the markdown sources")
    parser.add_argument("--show", type=int, default=0, help="print N changed titles/summaries")
    args = parser.parse_args()
    asyncio.run(run_db(args.commit, args.show))
    if args.markdown:
        run_markdown(args.commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
