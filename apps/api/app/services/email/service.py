"""The two public ways to send mail, and the choice of who sends it.

Used to notify the 7Magic inbox when a couple submits a pricing request or a
contact enquiry, and to confirm a booked venue tour. Sending is deliberately
best-effort at both entry points: the lead or the registration is already
persisted by the time we get here, so a missing API key or a provider outage
must never turn into a failed submission for the visitor.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings, get_settings

from .base import EmailMessage, Mailer
from .bird import BirdMailer
from .layout import paragraphs, render_email, render_lead_email
from .resend import ResendMailer

logger = logging.getLogger("app.email")


def get_mailer(settings: Settings) -> Mailer:
    """One provider, chosen from config. Both stay configured, so switching back
    is the same one variable."""
    if settings.mail_provider == "bird":
        return BirdMailer(settings)
    return ResendMailer(settings)


async def send_email(
    *,
    to: list[str],
    subject: str,
    text: str,
    reply_to: str | None = None,
    locale: str | None = None,
) -> None:
    """Plain-text send, used by the tour endpoints for both the guest
    confirmation and the branch alert.

    Raises on transport failure rather than swallowing it, unlike EmailNotifier
    below: the tour endpoint decides for itself that a provider outage must not
    fail the request, and it wants the exception logged with the registration id.
    An unconfigured provider is a no-op, so a dev machine never posts live mail.
    """
    settings = get_settings()
    mailer = get_mailer(settings)
    # Two different situations, so two different messages: reporting "not
    # configured" for an empty recipient list sends whoever reads the log after
    # a credential that is already fine.
    if not to:
        logger.warning("No recipients -- no email sent: %s", subject)
        return
    if not mailer.configured:
        logger.warning(
            "%s is not configured -- no email sent: %s", settings.mail_provider, subject
        )
        return

    await mailer.send(
        EmailMessage(
            to=to,
            subject=subject,
            text=text,
            # Derived rather than authored: the templates behind these are plain
            # text edited in a CMS textarea and stay that way, and the original
            # ships alongside as the alternative part.
            # The locale reaches the shell too, so an Indonesian confirmation
            # does not carry an English heading in its footer.
            html=render_email(
                heading=subject,
                body_html=paragraphs(text),
                preheader=subject,
                locale=locale,
            ),
            reply_to=reply_to,
        )
    )


class EmailNotifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._mailer = get_mailer(settings)

    @property
    def configured(self) -> bool:
        return self._mailer.configured

    async def send_lead_notification(
        self, *, subject: str, heading: str, fields: dict[str, Any], reply_to: str | None = None
    ) -> bool:
        """Notify the 7Magic inbox. Returns whether the send succeeded; callers
        should not treat False as a request failure."""
        if not self.configured:
            logger.warning(
                "%s is not configured -- lead saved but no email sent: %s",
                self._settings.mail_provider,
                subject,
            )
            return False

        text_lines = [heading, ""]
        text_lines += [f"{label}: {value}" for label, value in fields.items() if value]

        try:
            await self._mailer.send(
                EmailMessage(
                    to=[self._settings.lead_notification_email],
                    subject=subject,
                    text="\n".join(text_lines),
                    html=render_lead_email(heading=heading, fields=fields),
                    # Lets the team reply straight to the couple from the alert.
                    reply_to=reply_to,
                )
            )
            return True
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "%s rejected the notification (%s): %s",
                self._settings.mail_provider,
                exc.response.status_code,
                exc.response.text[:300],
            )
            return False
        except httpx.HTTPError as exc:
            logger.warning("Could not reach %s: %s", self._settings.mail_provider, exc)
            return False
