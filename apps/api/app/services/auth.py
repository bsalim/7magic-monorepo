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
    verify_password_argon2,
)
from app.domains.branches.access import CMS_ROLES
from app.models import User, UserRole

MIN_PASSWORD_LENGTH = 8


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AdminRequiredError(Exception):
    pass


class InvalidTokenSubjectError(Exception):
    pass


class WeakPasswordError(Exception):
    pass


class PasswordUnchangedError(Exception):
    pass


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    email: str
    username: str | None
    first_name: str
    last_name: str
    roles: list[str]
    # (role_name, branch_id) with branch_id None for an org-wide grant.
    branch_grants: tuple[tuple[str, int | None], ...] = ()


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


async def change_user_password(
    session: AsyncSession,
    *,
    user_id: int,
    current_password: str,
    new_password: str,
) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidTokenSubjectError

    if not verify_password_argon2(current_password, user.password_hash):
        raise InvalidCredentialsError

    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise WeakPasswordError

    if new_password == current_password:
        raise PasswordUnchangedError

    user.password_hash = hash_password(new_password)
    await session.commit()


def _require_admin_user(user: User) -> AuthenticatedUser:
    if not user.active:
        raise InactiveUserError

    roles = sorted(role_link.role.name for role_link in user.roles if role_link.role is not None)
    # Any CMS role may sign in, not only `admin`: a branch manager needs the CMS
    # to run their own branch. What they can reach once inside is decided per
    # request by the AccessSet built from branch_grants.
    if not CMS_ROLES.intersection(roles):
        raise AdminRequiredError

    grants = tuple(
        (role_link.role.name, role_link.branch_id)
        for role_link in user.roles
        if role_link.role is not None
    )

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=roles,
        branch_grants=grants,
    )


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    normalized_email = email.strip().lower()
    result = await session.execute(_user_query().where(User.email == normalized_email))
    return result.scalar_one_or_none()


def _user_query():
    return select(User).options(selectinload(User.roles).selectinload(UserRole.role))
