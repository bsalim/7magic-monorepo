from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base, get_db_session
from app.core.rate_limit import get_login_rate_limiter
from app.main import app
from app.models import User, UserSession
from app.services.user_seed import seed_admin_user

EMAIL = "byonosalim@gmail.com"
CURRENT_PASSWORD = "Admin123"
NEW_PASSWORD = "sengkuni-langit-7"


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'change-password-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            await seed_admin_user(session, email=EMAIL, password=CURRENT_PASSWORD)

    import asyncio

    asyncio.run(prepare_database())
    app.dependency_overrides[get_db_session] = override_db_session
    get_login_rate_limiter().clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_login_rate_limiter().clear()
    asyncio.run(engine.dispose())


def login(client: TestClient, password: str = CURRENT_PASSWORD) -> str:
    response = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def read_password_hash() -> str:
    import asyncio

    async def query() -> str:
        async for session in app.dependency_overrides[get_db_session]():
            result = await session.execute(select(User).where(User.email == EMAIL))
            return result.scalar_one().password_hash
        raise AssertionError("no db session")

    return asyncio.run(query())


def count_sessions() -> int:
    import asyncio

    async def query() -> int:
        async for session in app.dependency_overrides[get_db_session]():
            return len((await session.execute(select(UserSession))).scalars().all())
        return -1

    return asyncio.run(query())


def test_change_password_updates_hash_and_allows_login_with_new_password(
    client: TestClient,
) -> None:
    token = login(client)
    before = read_password_hash()

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert read_password_hash() != before

    get_login_rate_limiter().clear()
    stale = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": CURRENT_PASSWORD},
    )
    assert stale.status_code == 401

    get_login_rate_limiter().clear()
    assert login(client, NEW_PASSWORD)


def test_change_password_keeps_current_session_and_revokes_the_others(
    client: TestClient,
) -> None:
    other_token = login(client)
    token = login(client)
    assert count_sessions() == 2

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["revoked_sessions"] == 1
    assert count_sessions() == 1

    still_valid = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert still_valid.status_code == 200

    revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {other_token}"})
    assert revoked.status_code == 401
    assert revoked.json()["error"]["code"] == "invalid_token"


def test_change_password_rejects_wrong_current_password(client: TestClient) -> None:
    token = login(client)
    before = read_password_hash()

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "not-the-password", "new_password": NEW_PASSWORD},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    assert read_password_hash() == before


def test_change_password_rejects_a_short_new_password(client: TestClient) -> None:
    token = login(client)
    before = read_password_hash()

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": "short7"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "weak_password"
    assert payload["error"]["details"] == {"min_length": 8}
    assert read_password_hash() == before


def test_change_password_rejects_reusing_the_current_password(client: TestClient) -> None:
    token = login(client)

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": CURRENT_PASSWORD},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "password_unchanged"


def test_change_password_requires_a_session(client: TestClient) -> None:
    missing = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
    )
    invalid = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        headers={"Authorization": "Bearer invalid"},
    )

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "missing_token"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_token"
