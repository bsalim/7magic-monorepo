from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.models import User, UserRole


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AdminRequiredError(Exception):
    pass


class InvalidTokenSubjectError(Exception):
    pass


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    email: str
    username: str | None
    first_name: str
    last_name: str
    roles: list[str]


async def authenticate_admin_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> AuthenticatedUser:
    user = await _get_user_by_email(session, email)
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        raise InvalidCredentialsError
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
        await session.commit()

    return _require_admin_user(user)


async def resolve_admin_user_by_id(
    session: AsyncSession,
    *,
    user_id: int,
) -> AuthenticatedUser:
    result = await session.execute(_user_query().where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidTokenSubjectError

    return _require_admin_user(user)


def _require_admin_user(user: User) -> AuthenticatedUser:
    if not user.active:
        raise InactiveUserError

    roles = sorted(role_link.role.name for role_link in user.roles if role_link.role is not None)
    if "admin" not in roles:
        raise AdminRequiredError

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=roles,
    )


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    normalized_email = email.strip().lower()
    result = await session.execute(_user_query().where(User.email == normalized_email))
    return result.scalar_one_or_none()


def _user_query():
    return select(User).options(selectinload(User.roles).selectinload(UserRole.role))
