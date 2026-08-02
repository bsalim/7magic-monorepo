import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.core.security import verify_password
from app.models import Role, User, UserRole
from app.services.user_seed import seed_admin_user


@pytest.mark.asyncio
async def test_seed_admin_user_creates_active_admin_user(tmp_path) -> None:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'seed.db'}")
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        await seed_admin_user(
            session,
            email="byonosalim@gmail.com",
            password="Admin123",
        )

    async with session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == "byonosalim@gmail.com"))
        ).scalar_one()
        role = (await session.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        user_roles = (
            await session.execute(
                select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
            )
        ).all()

        assert user.active is True
        assert user.email_confirmed_at is not None
        assert user.password_hash != "Admin123"
        assert verify_password("Admin123", user.password_hash)
        assert len(user_roles) == 1

    async with session_factory() as session:
        await seed_admin_user(
            session,
            email=" byonosalim@gmail.com ",
            password="Admin123",
        )

    async with session_factory() as session:
        users = (await session.execute(select(User))).scalars().all()
        roles = (await session.execute(select(Role))).scalars().all()
        user_roles = (await session.execute(select(UserRole))).scalars().all()

        assert len(users) == 1
        assert len(roles) == 1
        assert len(user_roles) == 1

    await engine.dispose()
