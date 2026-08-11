"""Allowlist sanitizer for admin-authored event copy.

Event descriptions and email bodies are written in a rich-text field and rendered
with `{@html}`. Everything not on the allowlist is dropped at write time, so the
render site never has to trust its input.
"""

from __future__ import annotations

from html.parser import HTMLParser

_ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "h2",
    "h3",
    "h4",
    "a",
    "blockquote",
    "span",
}
_VOID_TAGS = {"br"}
_ALLOWED_ATTRS = {"a": {"href", "title", "target", "rel"}}
_SAFE_URL_PREFIXES = ("https://", "http://", "mailto:", "tel:", "/")
_DROP_CONTENT_TAGS = {"script", "style"}


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._suppress_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._suppress_depth += 1
            return
        if self._suppress_depth or tag not in _ALLOWED_TAGS:
            return
        kept = []
        for name, value in attrs:
            if name not in _ALLOWED_ATTRS.get(tag, set()) or value is None:
                continue
            if name == "href" and not value.lower().startswith(_SAFE_URL_PREFIXES):
                continue
            kept.append(f' {name}="{value}"')
        closer = " /" if tag in _VOID_TAGS else ""
        self.parts.append(f"<{tag}{''.join(kept)}{closer}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._suppress_depth = max(0, self._suppress_depth - 1)
            return
        if self._suppress_depth or tag not in _ALLOWED_TAGS or tag in _VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._suppress_depth:
            return
        self.parts.append(data.replace("<", "&lt;").replace(">", "&gt;"))


def sanitize_html(value: str | None) -> str:
    if not value:
        return ""
    parser = _Sanitizer()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts).strip()
