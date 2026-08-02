from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app import models  # noqa: F401
from app.core.database import Base, get_db_session
from app.core.rate_limit import get_login_rate_limiter
from app.core.security import hash_password
from app.main import app
from app.models import Role, User, UserRole, UserSession
from app.services.sessions import SESSION_REFRESH_INTERVAL_SECONDS
from app.services.user_seed import seed_admin_user


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'auth-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            await seed_admin_user(
                session,
                email="byonosalim@gmail.com",
                password="Admin123",
            )

    import asyncio

    asyncio.run(prepare_database())
    app.dependency_overrides[get_db_session] = override_db_session
    get_login_rate_limiter().clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_login_rate_limiter().clear()
    asyncio.run(engine.dispose())


def test_admin_can_login_and_resolve_session(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["expires_in"] > 0
    assert payload["user"]["email"] == "byonosalim@gmail.com"
    assert "admin" in payload["user"]["roles"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )

    assert me.status_code == 200
    assert me.json()["email"] == "byonosalim@gmail.com"


def test_login_rejects_bad_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_rejects_non_admin_user(client: TestClient) -> None:
    async def add_editor_user() -> None:
        async for session in app.dependency_overrides[get_db_session]():
            editor = Role(name="editor")
            user = User(
                email="editor@example.com",
                username="editor",
                password_hash=hash_password("Admin123"),
                active=True,
            )
            session.add_all([editor, user])
            await session.flush()
            session.add(UserRole(user_id=user.id, role_id=editor.id))
            await session.commit()

    import asyncio

    asyncio.run(add_editor_user())

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "editor@example.com", "password": "Admin123"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_required"


def test_login_is_rate_limited_after_repeated_failures(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "byonosalim@gmail.com", "password": "wrong"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )

    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "too_many_attempts"


def test_successful_login_resets_failure_count(client: TestClient) -> None:
    for _ in range(4):
        client.post(
            "/api/v1/auth/login",
            json={"email": "byonosalim@gmail.com", "password": "wrong"},
        )

    success = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )
    assert success.status_code == 200

    next_failure = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "wrong"},
    )
    assert next_failure.status_code == 401
    assert next_failure.json()["error"]["code"] == "invalid_credentials"


def test_me_rejects_missing_or_invalid_token(client: TestClient) -> None:
    missing = client.get("/api/v1/auth/me")
    invalid = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "missing_token"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_token"


def test_me_rejects_token_when_admin_role_is_removed(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )
    token = login.json()["access_token"]

    async def remove_admin_role() -> None:
        async for session in app.dependency_overrides[get_db_session]():
            result = await session.execute(
                select(User)
                .where(User.email == "byonosalim@gmail.com")
                .options(selectinload(User.roles).selectinload(UserRole.role))
            )
            user = result.scalar_one()
            user.roles.clear()
            await session.commit()

    import asyncio

    asyncio.run(remove_admin_role())

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_required"


def test_logout_revokes_session(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )
    token = login.json()["access_token"]

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200
    assert logout.json() == {"status": "ok"}

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401
    assert me.json()["error"]["code"] == "invalid_token"


def test_expired_session_is_rejected_and_deleted(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )
    token = login.json()["access_token"]

    async def expire_session() -> None:
        async for session in app.dependency_overrides[get_db_session]():
            record = (await session.execute(select(UserSession))).scalar_one()
            record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
            await session.commit()

    import asyncio

    asyncio.run(expire_session())

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401
    assert me.json()["error"]["code"] == "invalid_token"

    async def count_sessions() -> int:
        async for session in app.dependency_overrides[get_db_session]():
            return len((await session.execute(select(UserSession))).scalars().all())
        return -1

    assert asyncio.run(count_sessions()) == 0


def test_stale_session_slides_forward_on_use(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "byonosalim@gmail.com", "password": "Admin123"},
    )
    token = login.json()["access_token"]
    stale = datetime.now(UTC) - timedelta(seconds=SESSION_REFRESH_INTERVAL_SECONDS + 60)

    async def make_stale() -> None:
        async for session in app.dependency_overrides[get_db_session]():
            record = (await session.execute(select(UserSession))).scalar_one()
            record.last_seen_at = stale
            await session.commit()

    import asyncio

    asyncio.run(make_stale())

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200

    async def read_last_seen() -> datetime:
        async for session in app.dependency_overrides[get_db_session]():
            record = (await session.execute(select(UserSession))).scalar_one()
            return record.last_seen_at
        raise AssertionError("no db session")

    last_seen = asyncio.run(read_last_seen())
    assert last_seen.replace(tzinfo=UTC) > stale
