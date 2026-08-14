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
from typing import Any

from app.core.config import get_settings

# 600px is the width that survives every client and every phone.
_MAX_WIDTH = "600px"
_FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
_INK = "#172033"
_MUTED = "#6b7280"
_LINE = "#e5e7eb"
_CANVAS = "#f6f7f9"


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
    return "".join(
        f'<p style="margin:0 0 16px;font-family:{_FONT};font-size:15px;'
        f'line-height:1.65;color:{_INK}">'
        f"{html.escape(block.strip()).replace(chr(10), '<br />')}"
        "</p>"
        for block in blocks
    )


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


def _footer(note: str | None) -> str:
    lines = [
        '7Magic Wedding &middot; <a href="https://7magicwedding.com" '
        f'style="color:{_MUTED};text-decoration:underline">7magicwedding.com</a>'
    ]
    if note:
        lines.append(html.escape(note))
    return (
        f'<tr><td style="padding:22px 32px 28px;border-top:1px solid {_LINE};'
        f'font-family:{_FONT};font-size:12px;line-height:1.7;color:{_MUTED}">'
        f'{"<br />".join(lines)}</td></tr>'
    )


def render_email(
    *,
    heading: str,
    body_html: str,
    preheader: str | None = None,
    footer_note: str | None = None,
    logo_url: str | None = None,
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
        f"{_footer(footer_note)}"
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
