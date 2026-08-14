"""Transactional email.

The public surface is exactly what it was when this was a single module, so
every caller is unchanged. Providers live in `resend.py` and `bird.py` behind
the `Mailer` protocol; `MAIL_PROVIDER` picks one. Presentation lives in
`layout.py` and never performs I/O.
"""

from .base import EmailMessage, Mailer
from .layout import paragraphs, render_email, render_lead_email
from .service import EmailNotifier, get_mailer, send_email

__all__ = [
    "EmailMessage",
    "EmailNotifier",
    "Mailer",
    "get_mailer",
    "paragraphs",
    "render_email",
    "render_lead_email",
    "send_email",
]
