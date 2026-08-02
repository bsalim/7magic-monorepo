from __future__ import annotations

import secrets
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.services.auth import (
    AdminRequiredError,
    AuthenticatedUser,
    InactiveUserError,
    InvalidTokenSubjectError,
    resolve_admin_user_by_id,
)
from app.services.sessions import resolve_session


class AuthError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def require_admin_user(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    token = extract_bearer_token(authorization)
    if token is None:
        raise AuthError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="missing_token",
            message="Missing bearer token.",
        )

    record = await resolve_session(
        session,
        token=token,
        ttl_seconds=settings.session_ttl_seconds,
        max_lifetime_seconds=settings.session_max_lifetime_seconds,
    )
    if record is None:
        raise AuthError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_token",
            message="Session token is invalid or expired.",
        )

    try:
        return await resolve_admin_user_by_id(session, user_id=record.user_id)
    except InvalidTokenSubjectError as error:
        raise AuthError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_token",
            message="Session token is invalid or expired.",
        ) from error
    except InactiveUserError as error:
        raise AuthError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="inactive_user",
            message="This user is inactive.",
        ) from error
    except AdminRequiredError as error:
        raise AuthError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="admin_required",
            message="CMS access requires an admin account.",
        ) from error


def require_website_read_access(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if settings.venue_read_allowed_origins:
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        origin_allowed = origin in settings.venue_read_allowed_origins
        referer_origin = _origin_from_url(referer)
        referer_allowed = referer_origin in settings.venue_read_allowed_origins

        if not origin_allowed and not referer_allowed:
            raise AuthError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="website_access_denied",
                message="Website venue access is not allowed from this origin.",
            )

    venue_key = request.headers.get("x-7magic-venue-key")
    if settings.venue_read_api_key and not secrets.compare_digest(
        venue_key or "", settings.venue_read_api_key
    ):
        raise AuthError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="website_access_denied",
            message="Website venue access key is invalid.",
        )


def _origin_from_url(url: str | None) -> str | None:
    if not url:
        return None

    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return None

    return f"{parsed.scheme}://{parsed.netloc}"


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()
