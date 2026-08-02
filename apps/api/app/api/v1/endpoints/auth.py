from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import extract_bearer_token, require_admin_user
from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.core.errors import error_response
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.schemas.auth import (
    AuthUserResponse,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
)
from app.services.auth import (
    MIN_PASSWORD_LENGTH,
    AdminRequiredError,
    AuthenticatedUser,
    InactiveUserError,
    InvalidCredentialsError,
    PasswordUnchangedError,
    WeakPasswordError,
    authenticate_admin_user,
    change_user_password,
)
from app.services.sessions import create_session, revoke_other_sessions, revoke_session

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    limiter: Annotated[LoginRateLimiter, Depends(get_login_rate_limiter)],
):
    throttle_key = _login_throttle_key(request, payload.email)
    if limiter.is_blocked(throttle_key):
        return error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="too_many_attempts",
            message="Too many failed login attempts. Try again later.",
        )

    try:
        user = await authenticate_admin_user(session, email=payload.email, password=payload.password)
    except InvalidCredentialsError:
        limiter.record_failure(throttle_key)
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            message="Email or password is incorrect.",
        )
    except InactiveUserError:
        return error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            code="inactive_user",
            message="This user is inactive.",
        )
    except AdminRequiredError:
        return error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            code="admin_required",
            message="CMS access requires an admin account.",
        )

    limiter.reset(throttle_key)
    access_token = await create_session(
        session, user_id=user.id, ttl_seconds=settings.session_ttl_seconds
    )
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.session_ttl_seconds,
        user=AuthUserResponse(**user.__dict__),
    )


def _login_throttle_key(request: Request, email: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{email.strip().lower()}"


@router.get("/me", response_model=AuthUserResponse)
async def me(user: Annotated[AuthenticatedUser, Depends(require_admin_user)]):
    return AuthUserResponse(**user.__dict__)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: Annotated[AuthenticatedUser, Depends(require_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
):
    try:
        await change_user_password(
            session,
            user_id=user.id,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except InvalidCredentialsError:
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            message="Current password is incorrect.",
        )
    except WeakPasswordError:
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="weak_password",
            message=f"New password must be at least {MIN_PASSWORD_LENGTH} characters.",
            details={"min_length": MIN_PASSWORD_LENGTH},
        )
    except PasswordUnchangedError:
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="password_unchanged",
            message="New password must be different from the current password.",
        )

    # Revoked after the commit, not before: a failure here leaves the new
    # password in place with stale sessions alive, which beats signing every
    # device out for a change that then failed. The caller's own session is
    # kept so the CMS does not bounce them to the login screen.
    token = extract_bearer_token(authorization)
    revoked = await revoke_other_sessions(session, user_id=user.id, keep_token=token or "")
    return {"status": "ok", "revoked_sessions": revoked}


@router.post("/logout")
async def logout(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    token = extract_bearer_token(authorization)
    if token:
        await revoke_session(session, token=token)
    return {"status": "ok"}
