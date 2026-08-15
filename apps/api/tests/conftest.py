"""Test-wide isolation from the notification providers.

pydantic-settings reads `apps/api/.env`, which on a developer machine holds real
Bird and Resend credentials. The lead tests exercise the full submit path, so
without this module a plain `uv run pytest` would post live WhatsApp alerts to
the team's phone -- and bill for them -- on every run.

Blanking the keys in the environment beats the dotenv file, because environment
variables take precedence there. It has to happen at import time: pytest imports
conftest before any test module, and `app.services.leads` builds its notifiers
from `get_settings()` at import. The cache clear covers the case where something
has already read the settings.

The shared `api` harness below sits in the same file, which is why the imports it
needs are not at the top: `app.main` pulls in the notifiers, so it may only be
imported once the credentials above have been blanked. Hence the file-wide E402
exemption.
"""

# ruff: noqa: E402

import os

from app.core.config import get_settings

# Every credential that could cause an outbound call during a test run. Add a
# new provider key here the moment you add it to Settings: a key reachable from
# the environment beats the dotenv file, so one missing name is enough to let a
# test post live mail.
for _name in (
    "BIRD_API_KEY",
    "BIRD_ACCESS_KEY",
    "BIRD_BASE_URL",
    "BIRD_WEBHOOK_SIGNING_KEY",
    "BIRD_MAIL_API_KEY",
    "WHATSAPP_TEAM_NUMBER",
    "RESEND_API_KEY",
):
    os.environ[_name] = ""

# Back to the default. A developer with MAIL_PROVIDER=bird exported would
# otherwise have the suite exercise a different provider than CI does.
os.environ["MAIL_PROVIDER"] = "resend"

get_settings.cache_clear()

import asyncio
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401  -- registers every table on Base.metadata
from app.api.v1.dependencies import require_admin_user
from app.core.database import Base, get_db_session
from app.main import app
from app.services.auth import AuthenticatedUser


@dataclass
class ApiHarness:
    """A TestClient wired to a throwaway SQLite file, plus the session factory that
    tests use to seed rows directly. `login` swaps the authenticated user so one test
    file can exercise org-wide and branch-scoped callers without rebuilding the app."""

    client: TestClient
    session_factory: async_sessionmaker[AsyncSession]
    user: AuthenticatedUser

    def login(self, user: AuthenticatedUser) -> None:
        self.user = user
        app.dependency_overrides[require_admin_user] = lambda: self.user

    def seed(self, coro_factory) -> None:
        """Run an `async def (session) -> None` against a fresh session and commit."""

        async def runner() -> None:
            async with self.session_factory() as session:
                await coro_factory(session)
                await session.commit()

        asyncio.run(runner())


def admin_user(**overrides) -> AuthenticatedUser:
    defaults = {
        "id": 1,
        "email": "admin@7magic.test",
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "roles": ["admin"],
        # An org-wide grant by default. Leave this empty and every scoped route
        # 403s, because an AccessSet built from no rows grants nothing.
        "branch_grants": (("admin", None),),
    }
    defaults.update(overrides)
    return AuthenticatedUser(**defaults)


@pytest.fixture()
def api(tmp_path) -> Generator[ApiHarness, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'api-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def prepare() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(prepare())

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    previous_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db_session] = override_db_session

    harness = ApiHarness(client=None, session_factory=session_factory, user=admin_user())  # type: ignore[arg-type]
    harness.login(harness.user)

    try:
        with TestClient(app) as test_client:
            harness.client = test_client
            yield harness
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        asyncio.run(engine.dispose())
