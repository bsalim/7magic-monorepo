"""Shared HTML shell for every transactional email.

Email clients are not browsers, and the markup here is shaped by that rather
than by taste: Outlook renders through Word, so structure is tables and not
flexbox; Gmail strips `<style>` blocks, so every rule is inline; web fonts do
not load, so the stack is system fonts; and a large share of readers block
remote images, so the logo has to degrade to something that still looks
deliberate rather than to a broken-image gap.

No I/O and no provider knowledge lives here -- just markup.
"""

from __future__ import annotations

import html
import re
from typing import Any

from app.core.config import get_settings
from app.core.locale import normalise_locale

# 600px is the width that survives every client and every phone.
_MAX_WIDTH = "600px"
_FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
_INK = "#172033"
_MUTED = "#6b7280"
_LINE = "#e5e7eb"
_CANVAS = "#f6f7f9"


# A detail line: a short label, a colon, then the value. Bounded deliberately --
# the label may not run past 24 characters or contain sentence punctuation, so
# ordinary prose that happens to include a colon is left alone.
_DETAIL_LINE = re.compile(r"^([^:.!?\n]{1,24}):[ \t]+(\S.*)$")


def _line(text: str) -> str:
    """One already-escaped line, with the value emphasised on a detail line.

    "Venue: The Ritz-Carlton" carries one piece of information the reader is
    scanning for, and it is not the word "Venue". Bolding the value makes the
    date, the venue and the head count findable at a glance instead of buried in
    an even-weight block.
    """
    match = _DETAIL_LINE.match(text)
    if not match:
        return text
    label, value = match.groups()
    return (
        f'<span style="color:{_MUTED}">{label}:</span> '
        f'<strong style="color:{_INK}">{value}</strong>'
    )


def paragraphs(text: str) -> str:
    """Escape CMS-authored plain text, then structure it.

    Escaping happens before structuring, and that ordering is the whole safety
    argument: event template text and guest-supplied values both arrive here
    untrusted. This is a different job from `core/html.py`, which allowlists the
    tags an author is *permitted* to write -- here authors write no HTML at all,
    so escaping everything is correct and no allowlist is involved.

    Blank lines separate paragraphs; a single newline is a line break, which is
    what makes the "Venue: / Date: / Guests:" block in a tour confirmation read
    as a block rather than one run-on line.
    """
    blocks = [block for block in text.split("\n\n") if block.strip()]
    rendered = []
    for block in blocks:
        # Escape first, then match: a label or value containing markup is inert
        # by the time the detail pattern sees it.
        lines = [_line(line) for line in html.escape(block.strip()).split("\n")]
        rendered.append(
            f'<p style="margin:0 0 16px;font-family:{_FONT};font-size:15px;'
            f'line-height:1.65;color:{_INK}">'
            f"{'<br />'.join(lines)}"
            "</p>"
        )
    return "".join(rendered)


def _header(logo_url: str) -> str:
    """An `<img>` when a logo is configured, a wordmark otherwise.

    The wordmark is not a placeholder. It is what readers with images blocked
    see either way, so it has to stand on its own.
    """
    if logo_url:
        inner = (
            f'<img src="{html.escape(logo_url)}" alt="7Magic Wedding" width="150" '
            'style="display:block;border:0;outline:none;text-decoration:none;'
            'max-width:150px;height:auto" />'
        )
    else:
        inner = (
            f'<span style="font-family:{_FONT};font-size:17px;letter-spacing:.2em;'
            f'font-weight:600;color:{_INK}">7MAGIC</span>'
            f'<span style="font-family:{_FONT};font-size:17px;letter-spacing:.2em;'
            f'font-weight:300;color:{_MUTED}"> WEDDING</span>'
        )
    return (
        f'<tr><td style="padding:28px 32px 22px;border-bottom:1px solid {_LINE}">'
        f"{inner}</td></tr>"
    )


# The registered offices, copied verbatim from the public site's footer
# (apps/web/src/lib/components/PublicFooter.svelte). Business data -- change it
# there and here together, or a guest gets a confirmation naming an office the
# site no longer lists.
OFFICES: tuple[tuple[str, str], ...] = (
    ("Jakarta", "Jalan Gajah Mada No. 10, Jakarta, Indonesia 10130"),
    (
        "Bali",
        "Sunday Arshika Hotel - Lobby, Sunset Road Kuta - Bali, Bali, 80612, Indonesia",
    ),
    ("Singapore", "110 Pasir Ris Street 11, Singapore 510110"),
)


# Keyed by locale so an Indonesian confirmation does not carry an English
# heading.
OFFICE_HEADING: dict[str, str] = {
    "id": "Alamat kantor",
    "en": "Office address",
}


def _footer(note: str | None, locale: str | None = None) -> str:
    """Company name, then the registered offices under a heading.

    A transactional email that names a real, findable business reads as one, and
    the addresses are what a guest checks when deciding whether a booking
    confirmation is genuine.
    """
    # The same normalisation the body uses, not a bare lookup: a bare lookup
    # missed on a region tag, so an `en-GB` guest got an English confirmation
    # wrapped in an Indonesian footer.
    heading = OFFICE_HEADING[normalise_locale(locale)]
    offices = "".join(
        f'<div style="margin-top:8px">'
        f'<div style="color:{_INK};font-weight:600">{html.escape(city)}</div>'
        f'<div style="color:{_MUTED}">{html.escape(address)}</div>'
        "</div>"
        for city, address in OFFICES
    )
    trailing = f'<div style="margin-top:14px">{html.escape(note)}</div>' if note else ""
    return (
        f'<tr><td style="padding:22px 32px 28px;border-top:1px solid {_LINE};'
        f'font-family:{_FONT};font-size:12px;line-height:1.6;color:{_MUTED}">'
        # Left, with everything under it. A centred name over left-aligned
        # addresses reads as two blocks that were laid out separately.
        f'<div style="font-weight:600;font-size:13px;color:{_INK};'
        'padding-bottom:14px">7Magic Wedding Planner</div>'
        f'<div style="color:{_INK};font-weight:600">{html.escape(heading)}</div>'
        f"{offices}{trailing}</td></tr>"
    )


def render_email(
    *,
    heading: str,
    body_html: str,
    preheader: str | None = None,
    footer_note: str | None = None,
    logo_url: str | None = None,
    locale: str | None = None,
) -> str:
    """Wrap a rendered body in the header/footer shell.

    `body_html` is already-safe markup -- either `paragraphs()` output or a
    field table built here. Callers never pass raw user text.
    """
    if logo_url is None:
        logo_url = get_settings().email_logo_url

    hidden = ""
    if preheader:
        # The line clients show next to the subject in the inbox list. Left
        # unset they scrape whatever text comes first, which is the logo alt.
        hidden = (
            '<div style="display:none;max-height:0;overflow:hidden;opacity:0;'
            f'mso-hide:all">{html.escape(preheader)}</div>'
        )

    return (
        f'<div style="background:{_CANVAS};padding:24px 12px;margin:0">{hidden}'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        f'width="100%" style="max-width:{_MAX_WIDTH};margin:0 auto;'
        f'background:#ffffff;border:1px solid {_LINE};border-radius:10px">'
        f"{_header(logo_url)}"
        f'<tr><td style="padding:30px 32px 14px">'
        f'<h1 style="margin:0 0 18px;font-family:{_FONT};font-size:20px;'
        f'line-height:1.35;font-weight:600;color:{_INK}">{html.escape(heading)}</h1>'
        f"{body_html}</td></tr>"
        f"{_footer(footer_note, locale)}"
        "</table></div>"
    )


def _row(label: str, value: Any) -> str:
    if value in (None, ""):
        return ""
    return (
        "<tr>"
        f'<td style="padding:6px 12px 6px 0;color:{_MUTED};white-space:nowrap">'
        f"{html.escape(label)}</td>"
        f'<td style="padding:6px 0"><strong>{html.escape(str(value))}</strong></td>'
        "</tr>"
    )


def render_lead_email(*, heading: str, fields: dict[str, Any]) -> str:
    """The 7Magic inbox notification. Same field table it always had, now inside
    the shared shell rather than being its own bare document."""
    rows = "".join(_row(label, value) for label, value in fields.items())
    body = (
        f'<p style="margin:0 0 18px;font-family:{_FONT};font-size:14px;color:{_MUTED}">'
        "Sent from the 7Magic website.</p>"
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        f'style="border-collapse:collapse;font-family:{_FONT};font-size:14px;'
        f'color:{_INK}">{rows}</table>'
    )
    return render_email(heading=heading, body_html=body, preheader=heading)
