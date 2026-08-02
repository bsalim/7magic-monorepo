from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import Role, User, UserRole

ADMIN_ROLE_NAME = "admin"


async def seed_admin_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    role_name: str = ADMIN_ROLE_NAME,
) -> User:
    normalized_email = email.strip().lower()
    if not normalized_email:
        raise ValueError("email is required")
    if not password:
        raise ValueError("password is required")

    role = (await session.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
    if role is None:
        role = Role(name=role_name)
        session.add(role)
        await session.flush()

    user = (
        await session.execute(select(User).where(User.email == normalized_email))
    ).scalar_one_or_none()
    if user is None:
        user = User(
            email=normalized_email,
            username=normalized_email.split("@", 1)[0],
            first_name="Admin",
            last_name="User",
        )
        session.add(user)

    user.password_hash = hash_password(password)
    user.active = True
    user.email_confirmed_at = user.email_confirmed_at or datetime.now(timezone.utc)
    await session.flush()

    existing_user_role = (
        await session.execute(
            select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
        )
    ).scalar_one_or_none()
    if existing_user_role is None:
        session.add(UserRole(user_id=user.id, role_id=role.id))

    await session.commit()
    return user
