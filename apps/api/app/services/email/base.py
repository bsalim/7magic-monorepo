"""What a mailer is, independent of who sends it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmailMessage:
    """One outbound email, provider-agnostic.

    `text` is required rather than optional: a send with no plain-text
    alternative is a deliverability problem, and making it non-optional means no
    future caller can forget it. `reply_to` stays scalar because that is what
    every caller has -- Bird wanting a list is Bird's concern, handled there.
    """

    to: list[str]
    subject: str
    text: str
    html: str | None = None
    reply_to: str | None = None


class Mailer(Protocol):
    @property
    def configured(self) -> bool: ...

    async def send(self, message: EmailMessage) -> None:
        """Deliver, or raise.

        Swallowing belongs to the caller, because the two callers want different
        things: the tour endpoint wants the exception so it can log it against a
        registration id, while the lead notifier wants a bool.
        """
        ...
