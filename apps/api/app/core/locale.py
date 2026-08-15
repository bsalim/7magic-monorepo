"""The one rule for turning a caller's locale into one we can render.

It lives in core, not in a domain, because two places need it and they must not
disagree: the events domain renders the confirmation *body*, and the email
layout renders the *shell* around it. When only the body normalised, an `en-GB`
guest received an English confirmation wrapped in an Indonesian footer.

Indonesian is canonical and English is secondary, matching the public site.
"""

from __future__ import annotations

BASE_LOCALE = "id"
SUPPORTED_LOCALES = ("id", "en")


def normalise_locale(locale: str | None) -> str:
    """Reduce whatever the caller sent to a locale we can render.

    Accepts a region tag (`en-GB`, `en_US`) by taking the language half, since
    that is what a browser or an `Accept-Language` header tends to carry.
    Anything unrecognised -- including nothing at all -- falls back to the base
    locale rather than raising: a booking must never fail over the language of
    its receipt.
    """
    candidate = (locale or "").strip().lower().replace("_", "-").split("-")[0]
    return candidate if candidate in SUPPORTED_LOCALES else BASE_LOCALE
