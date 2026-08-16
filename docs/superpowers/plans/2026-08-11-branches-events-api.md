# Branches, Events and Book a Tour — API Implementation Plan (Plan 1 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the 7magic API branches, branch-scoped permissions, events with registrations and emails, and the public Book a Tour endpoints — with routers small enough that no file becomes the next `resources.py`.

**Architecture:** Two new domain packages, `app/domains/branches/` and `app/domains/events/`, each holding its own models, schemas and service. Routers under `app/api/v1/admin/` are named for one resource each and contain HTTP concerns only. Permissions come from a nullable `branch_id` on the existing `user_roles` table, resolved per request into an access set.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Alembic (batch mode for SQLite), pytest + pytest-asyncio, `uv`.

**Spec:** `docs/superpowers/specs/2026-08-11-branches-events-tour-design.md`

---

## Ground rules for every task in this plan

1. **Routers hold no queries.** If a step has you writing `select(...)` inside `app/api/v1/`, it belongs in that domain's `service.py`.
2. **SQLite must keep working.** No `JSONB`, no `ARRAY`, no `postgresql_where` partial index. Use `sqlalchemy.JSON` and enforce single-row invariants in the service layer.
3. **Run from `apps/api`** unless a command says otherwise. Tests are `uv run pytest`.
4. **Commit at the end of every task.** The commit message bodies below are not optional garnish; they are how the next person reads this migration.

---

### Task 1: Test harness for API tests

Existing test files each build their own engine and `TestClient`. Six new test files would repeat ~40 lines each, so the shared harness comes first.

**Files:**
- Modify: `apps/api/tests/conftest.py`

- [ ] **Step 1: Append the harness to conftest**

Add to the end of `apps/api/tests/conftest.py` (keep the existing credential-blanking block at the top of the file exactly as it is):

```python
import asyncio
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass, field

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
```

Note `branch_grants` in `admin_user()` — that field lands on `AuthenticatedUser` in Task 4. Until then the harness is unused, which is fine; Task 2 tests the service layer directly.

- [ ] **Step 2: Verify nothing broke**

Run: `cd apps/api && uv run pytest -q`
Expected: the existing suite still passes (the new fixture is not yet used by any test).

- [ ] **Step 3: Commit**

```bash
git add apps/api/tests/conftest.py
git commit -m "test(api): add a shared TestClient harness for branch and event tests"
```

---

### Task 2: Branch models

**Files:**
- Create: `apps/api/app/domains/__init__.py`
- Create: `apps/api/app/domains/branches/__init__.py`
- Create: `apps/api/app/domains/branches/models.py`
- Modify: `apps/api/app/models/__init__.py`
- Test: `apps/api/tests/test_branch_models.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_branch_models.py`:

```python
from __future__ import annotations

from datetime import datetime, time

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour, BranchSettings


@pytest_asyncio.fixture()
async def session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'branch-models.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_branch_round_trips_with_settings_hours_and_closures(session: AsyncSession) -> None:
    branch = Branch(
        slug="jakarta-pusat",
        name="7Magic Jakarta Pusat",
        address_line1="Jl. Thamrin No. 1",
        city="jakarta",
        country_code="ID",
        timezone="Asia/Jakarta",
        public_email="jakarta@7magic.test",
    )
    branch.settings = BranchSettings(
        sender_display_name="7Magic Jakarta",
        reply_to_email="jakarta@7magic.test",
        tour_notification_recipients=["ops@7magic.test", "jakarta@7magic.test"],
    )
    branch.opening_hours.append(
        BranchOpeningHour(day_of_week=1, opens_at_local=time(10, 0), closes_at_local=time(18, 0))
    )
    branch.closures.append(
        BranchClosure(
            starts_at_local=datetime(2026, 12, 25, 0, 0),
            ends_at_local=datetime(2026, 12, 25, 23, 59),
            full_day=True,
            public_label="Libur Natal",
        )
    )
    session.add(branch)
    await session.commit()

    stored = await session.scalar(select(Branch).where(Branch.slug == "jakarta-pusat"))
    assert stored is not None
    assert stored.public_id is not None
    assert stored.is_default is False
    assert stored.settings.tour_notification_recipients == ["ops@7magic.test", "jakarta@7magic.test"]
    assert stored.opening_hours[0].day_of_week == 1
    assert stored.closures[0].public_label == "Libur Natal"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_branch_models.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains'`.

- [ ] **Step 3: Create the domain package**

Create `apps/api/app/domains/__init__.py` (empty file) and `apps/api/app/domains/branches/__init__.py` (empty file).

Create `apps/api/app/domains/branches/models.py`:

```python
from __future__ import annotations

import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.domains.events.models import Event


class Branch(TimestampMixin, Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="jakarta", index=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="ID")
    postal_code: Mapped[str | None] = mapped_column(String(20))
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Jakarta")
    public_phone: Mapped[str | None] = mapped_column(String(40))
    public_email: Mapped[str | None] = mapped_column(String(255))
    whatsapp_number: Mapped[str | None] = mapped_column(String(40))
    instagram_url: Mapped[str | None] = mapped_column(String(255))
    facebook_url: Mapped[str | None] = mapped_column(String(255))
    # Overrides the site origin used when building links for this branch. Some
    # branches run their own landing page; NULL falls back to the global origin.
    website_url: Mapped[str | None] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Where /tour lands with no branch in the URL. At most one row may be true --
    # enforced in branch_service, because SQLite has no partial unique index.
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    settings: Mapped["BranchSettings"] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    opening_hours: Mapped[list["BranchOpeningHour"]] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=lambda: (BranchOpeningHour.day_of_week, BranchOpeningHour.opens_at_local),
    )
    closures: Mapped[list["BranchClosure"]] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=lambda: BranchClosure.starts_at_local,
    )
    events: Mapped[list["Event"]] = relationship(back_populates="branch")


class BranchSettings(TimestampMixin, Base):
    __tablename__ = "branch_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sender_display_name: Mapped[str | None] = mapped_column(String(150))
    reply_to_email: Mapped[str | None] = mapped_column(String(255))
    # Who hears about a new tour registration at this branch. JSON, not ARRAY:
    # the dev database is SQLite.
    tour_notification_recipients: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    tour_intro_html: Mapped[str | None] = mapped_column(Text)
    arrival_instructions: Mapped[str | None] = mapped_column(Text)
    parking_notes: Mapped[str | None] = mapped_column(Text)

    branch: Mapped[Branch] = relationship(back_populates="settings")


class BranchOpeningHour(TimestampMixin, Base):
    __tablename__ = "branch_opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ISO 8601 numbering: Monday = 1 ... Sunday = 7. Stated here because the
    # source platform carries two competing conventions and paid for it.
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    opens_at_local: Mapped[time] = mapped_column(Time, nullable=False)
    closes_at_local: Mapped[time] = mapped_column(Time, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    branch: Mapped[Branch] = relationship(back_populates="opening_hours")


class BranchClosure(TimestampMixin, Base):
    __tablename__ = "branch_closures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Local wall-clock only. The source platform stores a UTC copy alongside and
    # the two can drift; convert with the branch timezone at read time instead.
    starts_at_local: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    ends_at_local: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    full_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(Text)  # internal
    public_label: Mapped[str | None] = mapped_column(Text)  # shown to guests
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    branch: Mapped[Branch] = relationship(back_populates="closures")


def branch_metadata(branch: Branch) -> dict[str, Any]:
    """Contact block reused by the public tour payload and branch emails."""
    return {
        "phone": branch.public_phone,
        "email": branch.public_email,
        "whatsapp": branch.whatsapp_number,
    }
```

- [ ] **Step 4: Register the tables on the metadata**

Alembic (`migrations/env.py`) and every test import `app.models` to populate `Base.metadata`. Domain models must be re-exported there or their tables will silently not exist.

In `apps/api/app/models/__init__.py`, add after the existing imports:

```python
# Domain-package models are re-exported here so `import app.models` still answers
# "what tables exist" -- alembic's env.py and the test fixtures both rely on that.
from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour, BranchSettings
```

and add `"Branch"`, `"BranchClosure"`, `"BranchOpeningHour"`, `"BranchSettings"` to `__all__`, keeping it alphabetically sorted.

- [ ] **Step 5: Run the test**

Run: `cd apps/api && uv run pytest tests/test_branch_models.py -q`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/domains apps/api/app/models/__init__.py apps/api/tests/test_branch_models.py
git commit -m "feat(api): add branch, settings, opening-hour and closure models"
```

---

### Task 3: Branch service and the single-default invariant

**Files:**
- Create: `apps/api/app/domains/branches/schemas.py`
- Create: `apps/api/app/domains/branches/service.py`
- Test: `apps/api/tests/test_branch_service.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_branch_service.py`:

```python
from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.domains.branches.schemas import BranchCreate, BranchUpdate
from app.domains.branches.service import BranchSlugConflictError, branch_service


@pytest_asyncio.fixture()
async def session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'branch-service.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


def _payload(**overrides) -> BranchCreate:
    data = {
        "slug": "jakarta-pusat",
        "name": "7Magic Jakarta Pusat",
        "addressLine1": "Jl. Thamrin No. 1",
        "city": "jakarta",
        "countryCode": "ID",
        "timezone": "Asia/Jakarta",
    }
    data.update(overrides)
    return BranchCreate.model_validate(data)


@pytest.mark.asyncio
async def test_create_branch_also_creates_its_settings_row(session: AsyncSession) -> None:
    branch = await branch_service.create(session, _payload())

    assert branch.settings is not None
    assert branch.settings.tour_notification_recipients == []


@pytest.mark.asyncio
async def test_first_branch_becomes_the_default(session: AsyncSession) -> None:
    branch = await branch_service.create(session, _payload())

    assert branch.is_default is True


@pytest.mark.asyncio
async def test_promoting_a_second_branch_demotes_the_first(session: AsyncSession) -> None:
    first = await branch_service.create(session, _payload())
    second = await branch_service.create(session, _payload(slug="bali", name="7Magic Bali"))

    await branch_service.update(session, second.id, BranchUpdate.model_validate({"isDefault": True}))

    refreshed_first = await branch_service.get(session, first.id)
    refreshed_second = await branch_service.get(session, second.id)
    assert refreshed_first.is_default is False
    assert refreshed_second.is_default is True


@pytest.mark.asyncio
async def test_duplicate_slug_is_rejected(session: AsyncSession) -> None:
    await branch_service.create(session, _payload())

    with pytest.raises(BranchSlugConflictError):
        await branch_service.create(session, _payload(name="Another"))


@pytest.mark.asyncio
async def test_list_hides_soft_deleted_branches(session: AsyncSession) -> None:
    branch = await branch_service.create(session, _payload())
    await branch_service.create(session, _payload(slug="bali", name="7Magic Bali"))

    await branch_service.delete(session, branch.id)

    remaining = await branch_service.list(session)
    assert [row.slug for row in remaining] == ["bali"]
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_branch_service.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains.branches.schemas'`.

- [ ] **Step 3: Write the schemas**

Create `apps/api/app/domains/branches/schemas.py`:

```python
from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BranchSchema(BaseModel):
    """camelCase over the wire, snake_case in Python -- the convention the CMS
    already expects from the venue and article endpoints."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class BranchCreate(BranchSchema):
    slug: str = Field(min_length=1, max_length=150)
    name: str = Field(min_length=1, max_length=150)
    address_line1: str = Field(default="", max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(default="jakarta", max_length=100)
    country_code: str = Field(default="ID", min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    timezone: str = Field(default="Asia/Jakarta", max_length=64)
    public_phone: str | None = Field(default=None, max_length=40)
    public_email: str | None = Field(default=None, max_length=255)
    whatsapp_number: str | None = Field(default=None, max_length=40)
    instagram_url: str | None = Field(default=None, max_length=255)
    facebook_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    active: bool = True
    bookable: bool = True
    is_default: bool = False


class BranchUpdate(BranchSchema):
    slug: str | None = Field(default=None, min_length=1, max_length=150)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=64)
    public_phone: str | None = Field(default=None, max_length=40)
    public_email: str | None = Field(default=None, max_length=255)
    whatsapp_number: str | None = Field(default=None, max_length=40)
    instagram_url: str | None = Field(default=None, max_length=255)
    facebook_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    active: bool | None = None
    bookable: bool | None = None
    is_default: bool | None = None


class BranchSettingsUpdate(BranchSchema):
    sender_display_name: str | None = Field(default=None, max_length=150)
    reply_to_email: str | None = Field(default=None, max_length=255)
    tour_notification_recipients: list[str] | None = None
    tour_intro_html: str | None = None
    arrival_instructions: str | None = None
    parking_notes: str | None = None


class OpeningHourInput(BranchSchema):
    day_of_week: int = Field(ge=1, le=7)  # ISO: Monday = 1
    opens_at_local: time
    closes_at_local: time
    active: bool = True
    sort_order: int = 0


class ClosureCreate(BranchSchema):
    starts_at_local: datetime
    ends_at_local: datetime
    full_day: bool = False
    reason: str | None = None
    public_label: str | None = None
    active: bool = True


class BranchSettingsResponse(BranchSchema):
    sender_display_name: str | None = None
    reply_to_email: str | None = None
    tour_notification_recipients: list[str] = Field(default_factory=list)
    tour_intro_html: str | None = None
    arrival_instructions: str | None = None
    parking_notes: str | None = None


class OpeningHourResponse(OpeningHourInput):
    id: int


class ClosureResponse(ClosureCreate):
    id: int


class BranchResponse(BranchSchema):
    id: int
    # UUID, not str: the column hands back a uuid.UUID and pydantic rejects it as a
    # string. `model_dump(mode="json")` renders it as one at the boundary.
    public_id: UUID
    slug: str
    name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    country_code: str
    postal_code: str | None = None
    timezone: str
    public_phone: str | None = None
    public_email: str | None = None
    whatsapp_number: str | None = None
    instagram_url: str | None = None
    facebook_url: str | None = None
    website_url: str | None = None
    active: bool
    bookable: bool
    is_default: bool
    settings: BranchSettingsResponse | None = None
    opening_hours: list[OpeningHourResponse] = Field(default_factory=list)
    closures: list[ClosureResponse] = Field(default_factory=list)
```

- [ ] **Step 4: Write the service**

Create `apps/api/app/domains/branches/service.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour, BranchSettings
from app.domains.branches.schemas import (
    BranchCreate,
    BranchSettingsUpdate,
    BranchUpdate,
    ClosureCreate,
    OpeningHourInput,
)


class BranchNotFoundError(Exception):
    pass


class BranchSlugConflictError(Exception):
    pass


class BranchService:
    async def list(
        self,
        session: AsyncSession,
        *,
        branch_ids: list[int] | None = None,
        active_only: bool = False,
    ) -> list[Branch]:
        """`branch_ids=None` means "every branch" and is only ever passed by an
        org-wide caller; the router resolves the scope, never this method."""
        query = select(Branch).where(Branch.deleted_at.is_(None)).order_by(Branch.name)
        if branch_ids is not None:
            query = query.where(Branch.id.in_(branch_ids))
        if active_only:
            query = query.where(Branch.active.is_(True))
        return list((await session.scalars(query)).all())

    async def get(self, session: AsyncSession, branch_id: int) -> Branch:
        branch = await session.scalar(
            select(Branch).where(Branch.id == branch_id, Branch.deleted_at.is_(None))
        )
        if branch is None:
            raise BranchNotFoundError
        return branch

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Branch:
        branch = await session.scalar(
            select(Branch).where(Branch.slug == slug, Branch.deleted_at.is_(None))
        )
        if branch is None:
            raise BranchNotFoundError
        return branch

    async def create(self, session: AsyncSession, payload: BranchCreate) -> Branch:
        await self._assert_slug_free(session, payload.slug, exclude_id=None)

        data = payload.model_dump()
        make_default = data.pop("is_default")
        branch = Branch(**data)
        branch.settings = BranchSettings(tour_notification_recipients=[])

        # The first branch is the default whether or not the caller asked: /tour
        # with no slug must always land somewhere.
        existing = await session.scalar(select(Branch.id).where(Branch.deleted_at.is_(None)))
        branch.is_default = make_default or existing is None

        session.add(branch)
        await session.flush()
        if branch.is_default:
            await self._demote_other_defaults(session, keep_id=branch.id)
        await session.commit()
        await session.refresh(branch)
        return branch

    async def update(self, session: AsyncSession, branch_id: int, payload: BranchUpdate) -> Branch:
        branch = await self.get(session, branch_id)
        changes = payload.model_dump(exclude_unset=True)

        if "slug" in changes and changes["slug"] != branch.slug:
            await self._assert_slug_free(session, changes["slug"], exclude_id=branch.id)

        promote = changes.pop("is_default", None)
        for key, value in changes.items():
            setattr(branch, key, value)

        if promote is True:
            branch.is_default = True
            await self._demote_other_defaults(session, keep_id=branch.id)
        elif promote is False and branch.is_default:
            # Refuse to leave the business with no default branch.
            branch.is_default = False
            fallback = await session.scalar(
                select(Branch)
                .where(Branch.id != branch.id, Branch.deleted_at.is_(None))
                .order_by(Branch.id)
            )
            if fallback is not None:
                fallback.is_default = True
            else:
                branch.is_default = True

        await session.commit()
        await session.refresh(branch)
        return branch

    async def delete(self, session: AsyncSession, branch_id: int) -> None:
        branch = await self.get(session, branch_id)
        branch.deleted_at = datetime.now(UTC)
        if branch.is_default:
            branch.is_default = False
            fallback = await session.scalar(
                select(Branch)
                .where(Branch.id != branch.id, Branch.deleted_at.is_(None))
                .order_by(Branch.id)
            )
            if fallback is not None:
                fallback.is_default = True
        await session.commit()

    async def update_settings(
        self, session: AsyncSession, branch_id: int, payload: BranchSettingsUpdate
    ) -> Branch:
        branch = await self.get(session, branch_id)
        if branch.settings is None:
            branch.settings = BranchSettings(tour_notification_recipients=[])
            await session.flush()
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(branch.settings, key, value)
        await session.commit()
        await session.refresh(branch)
        return branch

    async def replace_opening_hours(
        self, session: AsyncSession, branch_id: int, rows: list[OpeningHourInput]
    ) -> Branch:
        """Whole-week replace. A per-row PATCH invites the half-saved week the
        source platform kept producing when a day was dropped from the form."""
        branch = await self.get(session, branch_id)
        branch.opening_hours.clear()
        await session.flush()
        for row in rows:
            branch.opening_hours.append(BranchOpeningHour(**row.model_dump()))
        await session.commit()
        await session.refresh(branch)
        return branch

    async def add_closure(
        self, session: AsyncSession, branch_id: int, payload: ClosureCreate
    ) -> BranchClosure:
        branch = await self.get(session, branch_id)
        closure = BranchClosure(**payload.model_dump())
        branch.closures.append(closure)
        await session.commit()
        await session.refresh(closure)
        return closure

    async def delete_closure(self, session: AsyncSession, branch_id: int, closure_id: int) -> None:
        closure = await session.scalar(
            select(BranchClosure).where(
                BranchClosure.id == closure_id, BranchClosure.branch_id == branch_id
            )
        )
        if closure is None:
            raise BranchNotFoundError
        await session.delete(closure)
        await session.commit()

    async def _assert_slug_free(
        self, session: AsyncSession, slug: str, *, exclude_id: int | None
    ) -> None:
        query = select(Branch.id).where(Branch.slug == slug, Branch.deleted_at.is_(None))
        if exclude_id is not None:
            query = query.where(Branch.id != exclude_id)
        if await session.scalar(query) is not None:
            raise BranchSlugConflictError

    async def _demote_other_defaults(self, session: AsyncSession, *, keep_id: int) -> None:
        """SQLite has no partial unique index, so the invariant lives here. It runs
        inside the caller's transaction, so no window exists with two defaults."""
        await session.execute(
            update(Branch).where(Branch.id != keep_id).values(is_default=False)
        )


branch_service = BranchService()
```

- [ ] **Step 5: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_branch_service.py -q`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/domains/branches apps/api/tests/test_branch_service.py
git commit -m "feat(api): add the branch service with a single-default invariant"
```

---

### Task 4: Branch-scoped permissions

**Files:**
- Modify: `apps/api/app/models/user.py`
- Create: `apps/api/app/domains/branches/access.py`
- Modify: `apps/api/app/services/auth.py`
- Test: `apps/api/tests/test_branch_access.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_branch_access.py`:

```python
from __future__ import annotations

import pytest

from app.domains.branches.access import (
    BRANCH_WRITE,
    EVENT_WRITE,
    REGISTRATION_WRITE,
    AccessSet,
    access_set_for,
)


def test_org_wide_role_grants_every_branch() -> None:
    access = access_set_for([("admin", None)])

    assert access.is_org_wide is True
    assert access.has(EVENT_WRITE) is True
    assert access.has(EVENT_WRITE, branch_id=42) is True
    assert access.branches_with(EVENT_WRITE) is None  # None == unbounded


def test_branch_scoped_role_grants_only_its_branch() -> None:
    access = access_set_for([("branch_manager", 7)])

    assert access.is_org_wide is False
    assert access.has(EVENT_WRITE, branch_id=7) is True
    assert access.has(EVENT_WRITE, branch_id=8) is False
    assert access.branches_with(EVENT_WRITE) == [7]


def test_branch_staff_may_manage_registrations_but_not_branch_settings() -> None:
    access = access_set_for([("branch_staff", 7)])

    assert access.has(REGISTRATION_WRITE, branch_id=7) is True
    assert access.has(BRANCH_WRITE, branch_id=7) is False


def test_grants_from_several_branches_accumulate() -> None:
    access = access_set_for([("branch_manager", 7), ("branch_staff", 9)])

    assert sorted(access.branches_with(REGISTRATION_WRITE) or []) == [7, 9]
    assert access.branches_with(BRANCH_WRITE) == [7]


def test_an_unknown_role_grants_nothing() -> None:
    access = access_set_for([("editor", None)])

    assert access.has(EVENT_WRITE) is False
    assert access.branches_with(EVENT_WRITE) == []


def test_permitted_or_raise_rejects_a_branch_outside_the_scope() -> None:
    access = access_set_for([("branch_manager", 7)])

    assert access.assert_branch(EVENT_WRITE, 7) is None
    with pytest.raises(AccessSet.BranchForbidden):
        access.assert_branch(EVENT_WRITE, 8)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_branch_access.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains.branches.access'`.

- [ ] **Step 3: Write the access module**

Create `apps/api/app/domains/branches/access.py`:

```python
"""Branch-scoped permissions.

A role row with `branch_id IS NULL` is org-wide; a row with a branch is scoped to
it. `branches_with` returns `None` for an org-wide grant, meaning *unbounded* --
callers must treat that as "apply no branch filter", not as "no branches".
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

BRANCH_READ = "branch:read"
BRANCH_WRITE = "branch:write"
EVENT_READ = "event:read"
EVENT_WRITE = "event:write"
REGISTRATION_READ = "registration:read"
REGISTRATION_WRITE = "registration:write"

ALL_PERMISSIONS = frozenset(
    {BRANCH_READ, BRANCH_WRITE, EVENT_READ, EVENT_WRITE, REGISTRATION_READ, REGISTRATION_WRITE}
)

# A branch manager runs their branch outright. Branch staff work the front desk:
# they read events and handle registrations, but do not edit the branch itself.
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "owner": ALL_PERMISSIONS,
    "admin": ALL_PERMISSIONS,
    "branch_manager": ALL_PERMISSIONS,
    "branch_staff": frozenset({BRANCH_READ, EVENT_READ, REGISTRATION_READ, REGISTRATION_WRITE}),
}

# Roles that may sign in to the CMS at all.
CMS_ROLES = frozenset(ROLE_PERMISSIONS)


@dataclass(frozen=True)
class AccessSet:
    org_wide: frozenset[str] = frozenset()
    per_branch: dict[int, frozenset[str]] = field(default_factory=dict)

    class BranchForbidden(Exception):
        pass

    @property
    def is_org_wide(self) -> bool:
        return bool(self.org_wide)

    def has(self, permission: str, branch_id: int | None = None) -> bool:
        if permission in self.org_wide:
            return True
        if branch_id is None:
            return any(permission in perms for perms in self.per_branch.values())
        return permission in self.per_branch.get(branch_id, frozenset())

    def branches_with(self, permission: str) -> list[int] | None:
        """`None` means unbounded -- do not filter. `[]` means no access at all."""
        if permission in self.org_wide:
            return None
        return sorted(
            branch_id for branch_id, perms in self.per_branch.items() if permission in perms
        )

    def assert_branch(self, permission: str, branch_id: int | None) -> None:
        """Raises unless the caller may act on `branch_id`. `branch_id=None` means an
        all-branch record, which only an org-wide grant may touch."""
        if permission in self.org_wide:
            return
        if branch_id is None or permission not in self.per_branch.get(branch_id, frozenset()):
            raise AccessSet.BranchForbidden
        return


def access_set_for(grants: Iterable[tuple[str, int | None]]) -> AccessSet:
    org_wide: set[str] = set()
    per_branch: dict[int, set[str]] = {}
    for role_name, branch_id in grants:
        permissions = ROLE_PERMISSIONS.get(role_name)
        if not permissions:
            continue
        if branch_id is None:
            org_wide.update(permissions)
        else:
            per_branch.setdefault(branch_id, set()).update(permissions)
    return AccessSet(
        org_wide=frozenset(org_wide),
        per_branch={key: frozenset(value) for key, value in per_branch.items()},
    )
```

- [ ] **Step 4: Run the access tests**

Run: `cd apps/api && uv run pytest tests/test_branch_access.py -q`
Expected: 6 passed.

- [ ] **Step 5: Carry the grants on the authenticated user**

In `apps/api/app/models/user.py`, add to `UserRole`:

```python
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=True, index=True
    )
```

and change its `__table_args__` so the same role can be granted on several branches:

```python
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "branch_id", name="uq_user_roles_user_role_branch"),
    )
```

In `apps/api/app/services/auth.py`, add the field to the dataclass:

```python
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
```

and rewrite `_require_admin_user` (currently at `apps/api/app/services/auth.py:113`) to accept any CMS role rather than only `admin`, so a branch manager can sign in:

```python
def _require_admin_user(user: User) -> AuthenticatedUser:
    if not user.active:
        raise InactiveUserError

    roles = sorted(role_link.role.name for role_link in user.roles if role_link.role is not None)
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
```

Add the import at the top of `apps/api/app/services/auth.py`:

```python
from app.domains.branches.access import CMS_ROLES
```

- [ ] **Step 6: Add the sign-in test**

Append to `apps/api/tests/test_branch_access.py`:

```python
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.models import Role, User, UserRole
from app.services.auth import resolve_admin_user_by_id
from app.services.security import hash_password


@pytest_asyncio.fixture()
async def auth_session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'access.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_a_branch_manager_may_sign_in_and_carries_its_branch(auth_session) -> None:
    from app.domains.branches.models import Branch

    branch = Branch(slug="bali", name="7Magic Bali", timezone="Asia/Makassar")
    role = Role(name="branch_manager")
    user = User(email="manager@7magic.test", password_hash=hash_password("secret-password"))
    auth_session.add_all([branch, role, user])
    await auth_session.flush()
    auth_session.add(UserRole(user_id=user.id, role_id=role.id, branch_id=branch.id))
    await auth_session.commit()

    authenticated = await resolve_admin_user_by_id(auth_session, user_id=user.id)

    assert authenticated.branch_grants == (("branch_manager", branch.id),)
    assert access_set_for(authenticated.branch_grants).branches_with(EVENT_WRITE) == [branch.id]
```

If `hash_password` is not exported from `app.services.security`, import it from wherever `authenticate_admin_user` gets it — check the imports at the top of `apps/api/app/services/auth.py` and match them.

- [ ] **Step 7: Run the whole suite**

Run: `cd apps/api && uv run pytest -q`
Expected: all pass. If `test_auth_contracts.py` or `test_seed_admin_user.py` fail on the widened role check, read the failure: a test asserting that a user with role `editor` is rejected must still pass, because `editor` is not in `CMS_ROLES`. Fix the test only if it asserted the literal string `"admin"` as the sole gate.

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/domains/branches/access.py apps/api/app/models/user.py apps/api/app/services/auth.py apps/api/tests/test_branch_access.py
git commit -m "feat(api): scope roles to branches and resolve them into an access set"
```

---

### Task 5: Shared admin router primitives

**Files:**
- Create: `apps/api/app/api/v1/admin/__init__.py`
- Create: `apps/api/app/api/v1/admin/_shared.py`

- [ ] **Step 1: Create the package**

Create `apps/api/app/api/v1/admin/__init__.py` (empty file).

- [ ] **Step 2: Write the shared primitives**

Create `apps/api/app/api/v1/admin/_shared.py`:

```python
"""Primitives shared by the admin routers.

Add a helper here only once three or more routers need it. The source platform's
equivalent file carried that same threshold and it is the reason the split held.

`branch_scope` is the one piece every branch-aware route depends on: it resolves
the caller's grants into an AccessSet, so a router never reads role rows itself.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_admin_user
from app.core.database import get_db_session
from app.core.errors import error_response
from app.domains.branches.access import AccessSet, access_set_for
from app.services.auth import AuthenticatedUser

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[AuthenticatedUser, Depends(require_admin_user)]


def branch_scope(user: CurrentUser) -> AccessSet:
    return access_set_for(user.branch_grants)


BranchScope = Annotated[AccessSet, Depends(branch_scope)]


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def forbidden_branch():
    return error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code="branch_forbidden",
        message="You do not have access to this branch.",
    )


def not_found(code: str, message: str):
    return error_response(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)


def conflict(code: str, message: str):
    return error_response(status_code=status.HTTP_409_CONFLICT, code=code, message=message)
```

- [ ] **Step 3: Verify it imports**

Run: `cd apps/api && uv run python -c "from app.api.v1.admin import _shared; print(_shared.iso(None))"`
Expected: `None`

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/api/v1/admin
git commit -m "feat(api): add shared primitives for the per-resource admin routers"
```

---

### Task 6: Branch admin router

**Files:**
- Create: `apps/api/app/api/v1/admin/branches.py`
- Modify: `apps/api/app/api/v1/router.py`
- Test: `apps/api/tests/test_branch_admin_api.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_branch_admin_api.py`:

```python
from __future__ import annotations

from tests.conftest import admin_user


def _create_branch(api, slug="jakarta-pusat", name="7Magic Jakarta Pusat"):
    return api.client.post(
        "/api/v1/admin/branches",
        json={
            "slug": slug,
            "name": name,
            "addressLine1": "Jl. Thamrin No. 1",
            "city": "jakarta",
            "countryCode": "ID",
            "timezone": "Asia/Jakarta",
        },
    )


def test_create_and_list_branches(api) -> None:
    created = _create_branch(api)

    assert created.status_code == 201
    body = created.json()["data"]
    assert body["slug"] == "jakarta-pusat"
    assert body["isDefault"] is True
    assert body["settings"]["tourNotificationRecipients"] == []

    listed = api.client.get("/api/v1/admin/branches")
    assert listed.status_code == 200
    assert [row["slug"] for row in listed.json()["items"]] == ["jakarta-pusat"]


def test_duplicate_slug_returns_409(api) -> None:
    _create_branch(api)

    conflicted = _create_branch(api, name="Duplicate")

    assert conflicted.status_code == 409
    assert conflicted.json()["error"]["code"] == "branch_slug_conflict"


def test_branch_scoped_user_sees_only_its_branch(api) -> None:
    first = _create_branch(api).json()["data"]
    _create_branch(api, slug="bali", name="7Magic Bali")

    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", first["id"]),)))
    listed = api.client.get("/api/v1/admin/branches")

    assert [row["slug"] for row in listed.json()["items"]] == ["jakarta-pusat"]


def test_branch_scoped_user_cannot_edit_another_branch(api) -> None:
    first = _create_branch(api).json()["data"]
    other = _create_branch(api, slug="bali", name="7Magic Bali").json()["data"]

    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", first["id"]),)))
    response = api.client.patch(f"/api/v1/admin/branches/{other['id']}", json={"name": "Hijacked"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "branch_forbidden"


def test_branch_staff_cannot_edit_branch_settings(api) -> None:
    branch = _create_branch(api).json()["data"]

    api.login(admin_user(roles=["branch_staff"], branch_grants=(("branch_staff", branch["id"]),)))
    response = api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/settings",
        json={"tourNotificationRecipients": ["nope@7magic.test"]},
    )

    assert response.status_code == 403


def test_opening_hours_replace_the_whole_week(api) -> None:
    branch = _create_branch(api).json()["data"]

    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={"items": [{"dayOfWeek": 1, "opensAtLocal": "10:00:00", "closesAtLocal": "18:00:00"}]},
    )
    second = api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={"items": [{"dayOfWeek": 2, "opensAtLocal": "11:00:00", "closesAtLocal": "19:00:00"}]},
    )

    assert second.status_code == 200
    assert [row["dayOfWeek"] for row in second.json()["data"]["openingHours"]] == [2]
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_branch_admin_api.py -q`
Expected: FAIL — every request 404s, because the router is not mounted yet.

- [ ] **Step 3: Write the router**

Create `apps/api/app/api/v1/admin/branches.py`:

```python
"""Branch admin routes. HTTP only -- every query lives in branch_service."""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.v1.admin._shared import BranchScope, DbSession, conflict, forbidden_branch, not_found
from app.domains.branches.access import BRANCH_READ, BRANCH_WRITE, AccessSet
from app.domains.branches.schemas import (
    BranchCreate,
    BranchResponse,
    BranchSettingsUpdate,
    BranchUpdate,
    ClosureCreate,
    OpeningHourInput,
)
from app.domains.branches.service import (
    BranchNotFoundError,
    BranchSlugConflictError,
    branch_service,
)

router = APIRouter()


class OpeningHoursReplace(BaseModel):
    items: list[OpeningHourInput]


def _payload(branch) -> dict:
    return BranchResponse.model_validate(branch).model_dump(by_alias=True, mode="json")


@router.get("/branches")
async def list_branches(session: DbSession, scope: BranchScope):
    if not scope.has(BRANCH_READ):
        return forbidden_branch()
    branches = await branch_service.list(session, branch_ids=scope.branches_with(BRANCH_READ))
    return {"items": [_payload(branch) for branch in branches]}


@router.post("/branches", status_code=status.HTTP_201_CREATED)
async def create_branch(payload: BranchCreate, session: DbSession, scope: BranchScope):
    # Creating a branch is inherently org-wide: there is no branch to be scoped to yet.
    if not scope.is_org_wide or not scope.has(BRANCH_WRITE):
        return forbidden_branch()
    try:
        branch = await branch_service.create(session, payload)
    except BranchSlugConflictError:
        return conflict("branch_slug_conflict", "A branch with this slug already exists.")
    return {"data": _payload(branch)}


@router.get("/branches/{branch_id}")
async def get_branch(branch_id: int, session: DbSession, scope: BranchScope):
    try:
        scope.assert_branch(BRANCH_READ, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.get(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.patch("/branches/{branch_id}")
async def update_branch(
    branch_id: int, payload: BranchUpdate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.update(session, branch_id, payload)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    except BranchSlugConflictError:
        return conflict("branch_slug_conflict", "A branch with this slug already exists.")
    return {"data": _payload(branch)}


@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: int, session: DbSession, scope: BranchScope):
    if not scope.is_org_wide or not scope.has(BRANCH_WRITE):
        return forbidden_branch()
    try:
        await branch_service.delete(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": {"deleted": True}}


@router.put("/branches/{branch_id}/settings")
async def update_branch_settings(
    branch_id: int, payload: BranchSettingsUpdate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.update_settings(session, branch_id, payload)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.put("/branches/{branch_id}/opening-hours")
async def replace_opening_hours(
    branch_id: int, payload: OpeningHoursReplace, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.replace_opening_hours(session, branch_id, payload.items)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.post("/branches/{branch_id}/closures", status_code=status.HTTP_201_CREATED)
async def add_closure(
    branch_id: int, payload: ClosureCreate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        await branch_service.add_closure(session, branch_id, payload)
        branch = await branch_service.get(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.delete("/branches/{branch_id}/closures/{closure_id}")
async def delete_closure(
    branch_id: int, closure_id: int, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        await branch_service.delete_closure(session, branch_id, closure_id)
    except BranchNotFoundError:
        return not_found("closure_not_found", "Closure not found.")
    return {"data": {"deleted": True}}
```

- [ ] **Step 4: Mount it**

In `apps/api/app/api/v1/router.py`, add the import and the include. The existing `admin` name refers to `app.api.v1.endpoints.admin`; the new package is `app.api.v1.admin`, so alias it to avoid a confusing shadow:

```python
from app.api.v1.admin import branches as admin_branches
from app.api.v1.endpoints import admin, auth, health, public, venues

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(
    admin_branches.router,
    prefix="/admin",
    tags=["admin-branches"],
    dependencies=[Depends(require_admin_user)],
)
```

Add the imports `from fastapi import APIRouter, Depends` and `from app.api.v1.dependencies import require_admin_user` at the top.

- [ ] **Step 5: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_branch_admin_api.py -q`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/api/v1/admin/branches.py apps/api/app/api/v1/router.py apps/api/tests/test_branch_admin_api.py
git commit -m "feat(api): expose branch admin routes with branch-scoped access"
```

---

### Task 7: Event models and the HTML sanitizer

**Files:**
- Create: `apps/api/app/domains/events/__init__.py`
- Create: `apps/api/app/domains/events/models.py`
- Create: `apps/api/app/domains/events/sanitize.py`
- Modify: `apps/api/app/models/__init__.py`
- Test: `apps/api/tests/test_event_sanitize.py`

- [ ] **Step 1: Write the failing sanitizer test**

Create `apps/api/tests/test_event_sanitize.py`:

```python
from __future__ import annotations

from app.domains.events.sanitize import sanitize_html


def test_allowed_formatting_survives() -> None:
    assert sanitize_html("<p>Halo <strong>calon pengantin</strong></p>") == (
        "<p>Halo <strong>calon pengantin</strong></p>"
    )


def test_script_tags_are_removed_with_their_contents() -> None:
    assert sanitize_html("<p>Halo</p><script>alert(1)</script>") == "<p>Halo</p>"


def test_event_handlers_are_stripped_from_allowed_tags() -> None:
    assert sanitize_html('<p onclick="steal()">Halo</p>') == "<p>Halo</p>"


def test_javascript_hrefs_are_dropped() -> None:
    assert sanitize_html('<a href="javascript:alert(1)">klik</a>') == "<a>klik</a>"


def test_https_hrefs_are_kept() -> None:
    assert sanitize_html('<a href="https://7magic.id">klik</a>') == '<a href="https://7magic.id">klik</a>'


def test_none_becomes_an_empty_string() -> None:
    assert sanitize_html(None) == ""
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_event_sanitize.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains.events'`.

- [ ] **Step 3: Write the sanitizer**

Create `apps/api/app/domains/events/__init__.py` (empty) and `apps/api/app/domains/events/sanitize.py`:

```python
"""Allowlist sanitizer for admin-authored event copy.

Event descriptions and email bodies are written in a rich-text field and rendered
with `{@html}`. Everything not on the allowlist is dropped at write time, so the
render site never has to trust its input.
"""

from __future__ import annotations

from html.parser import HTMLParser

_ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li",
    "h2", "h3", "h4", "a", "blockquote", "span",
}
_VOID_TAGS = {"br"}
_ALLOWED_ATTRS = {"a": {"href", "title", "target", "rel"}}
_SAFE_URL_PREFIXES = ("https://", "http://", "mailto:", "tel:", "/")
_DROP_CONTENT_TAGS = {"script", "style"}


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._suppress_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._suppress_depth += 1
            return
        if self._suppress_depth or tag not in _ALLOWED_TAGS:
            return
        kept = []
        for name, value in attrs:
            if name not in _ALLOWED_ATTRS.get(tag, set()) or value is None:
                continue
            if name == "href" and not value.lower().startswith(_SAFE_URL_PREFIXES):
                continue
            kept.append(f' {name}="{value}"')
        closer = " /" if tag in _VOID_TAGS else ""
        self.parts.append(f"<{tag}{''.join(kept)}{closer}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP_CONTENT_TAGS:
            self._suppress_depth = max(0, self._suppress_depth - 1)
            return
        if self._suppress_depth or tag not in _ALLOWED_TAGS or tag in _VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._suppress_depth:
            return
        self.parts.append(data.replace("<", "&lt;").replace(">", "&gt;"))


def sanitize_html(value: str | None) -> str:
    if not value:
        return ""
    parser = _Sanitizer()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts).strip()
```

- [ ] **Step 4: Run the sanitizer tests**

Run: `cd apps/api && uv run pytest tests/test_event_sanitize.py -q`
Expected: 6 passed.

- [ ] **Step 5: Write the event models**

Create `apps/api/app/domains/events/models.py`:

```python
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.branches.models import Branch
from app.models.mixins import TimestampMixin

REGISTRATION_STATUSES = ("registered", "attended", "no_show", "cancelled")
TEMPLATE_KINDS = ("thank_you", "no_show", "cancel")


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    # NULL means the event belongs to every branch (a company-wide open house).
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    venue: Mapped[str | None] = mapped_column(String(300))
    event_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registration_opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registration_closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    capacity: Mapped[int | None] = mapped_column(Integer)
    cover_image_url: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # selectin, not lazy: the routers read `event.branch.name` for the Branch column
    # after the query has returned, and a lazy load there raises MissingGreenlet
    # under asyncio.
    branch: Mapped[Branch | None] = relationship(back_populates="events", lazy="selectin")
    registrations: Mapped[list["EventRegistration"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    email_templates: Mapped[list["EventEmailTemplate"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", lazy="selectin"
    )


class EventRegistration(TimestampMixin, Base):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    guest_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    mobile: Mapped[str | None] = mapped_column(String(40))
    party_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    visit_date: Mapped[date | None] = mapped_column(Date)
    visit_slot: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="registered", index=True)
    follow_up: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    # "public" (the website form) or "cms" (typed in by the team).
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    attended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attended_by_user_id: Mapped[int | None] = mapped_column(Integer)

    # Also selectin: the registrations router reads `registration.event.branch.name`
    # for its Branch column and its CSV export.
    event: Mapped[Event] = relationship(back_populates="registrations", lazy="selectin")
    guests: Mapped[list["EventRegistrationGuest"]] = relationship(
        back_populates="registration", cascade="all, delete-orphan", lazy="selectin"
    )


class EventRegistrationGuest(Base):
    __tablename__ = "event_registration_guests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(
        ForeignKey("event_registrations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    mobile: Mapped[str | None] = mapped_column(String(40))

    registration: Mapped[EventRegistration] = relationship(back_populates="guests")


class EventEmailTemplate(TimestampMixin, Base):
    __tablename__ = "event_email_templates"
    __table_args__ = (
        UniqueConstraint("event_id", "kind", name="uq_event_email_templates_event_id_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # see TEMPLATE_KINDS
    subject: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    event: Mapped[Event] = relationship(back_populates="email_templates")
```

- [ ] **Step 6: Register the event tables**

In `apps/api/app/models/__init__.py`, add:

```python
from app.domains.events.models import (
    Event,
    EventEmailTemplate,
    EventRegistration,
    EventRegistrationGuest,
)
```

and add `"Event"`, `"EventEmailTemplate"`, `"EventRegistration"`, `"EventRegistrationGuest"` to `__all__`.

- [ ] **Step 7: Verify the metadata builds**

Run: `cd apps/api && uv run python -c "from app import models; from app.core.database import Base; print(sorted(t for t in Base.metadata.tables if 'event' in t or 'branch' in t))"`
Expected: `['branch_closures', 'branch_opening_hours', 'branch_settings', 'branches', 'event_email_templates', 'event_registration_guests', 'event_registrations', 'events']`

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/domains/events apps/api/app/models/__init__.py apps/api/tests/test_event_sanitize.py
git commit -m "feat(api): add event models and an allowlist HTML sanitizer"
```

---

### Task 8: Event service and the registration gate

The rule that decides whether an event is open is used by both the public GET and the public POST. It lives in the service so the page a guest sees and the answer they get on submit cannot disagree.

**Files:**
- Create: `apps/api/app/domains/events/schemas.py`
- Create: `apps/api/app/domains/events/service.py`
- Test: `apps/api/tests/test_event_service.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_event_service.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour
from app.domains.events.models import Event, EventRegistration
from app.domains.events.schemas import PublicRegistration
from app.domains.events.service import RegistrationBlocked, event_service

NOW = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)


@pytest_asyncio.fixture()
async def session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'event-service.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


async def _branch_with_event(session, **event_overrides) -> tuple[Branch, Event]:
    branch = Branch(slug="jakarta", name="7Magic Jakarta", timezone="Asia/Jakarta")
    # Open Monday to Saturday, 10:00-18:00. 2026-09-07 is a Monday.
    for day in range(1, 7):
        branch.opening_hours.append(
            BranchOpeningHour(day_of_week=day, opens_at_local=time(10, 0), closes_at_local=time(18, 0))
        )
    session.add(branch)
    await session.flush()

    fields = {
        "branch_id": branch.id,
        "name": "Book a Tour",
        "registration_opens_at": NOW - timedelta(days=7),
        "registration_closes_at": NOW + timedelta(days=7),
        "event_start_at": NOW + timedelta(days=10),
        "event_end_at": NOW + timedelta(days=10, hours=6),
    }
    fields.update(event_overrides)
    event = Event(**fields)
    session.add(event)
    await session.commit()
    return branch, event


def _registration(**overrides) -> PublicRegistration:
    data = {
        "name": "Rina",
        "email": "rina@example.test",
        "mobile": "+628111111111",
        "visitDate": "2026-09-07",  # a Monday
        "visitSlot": "10:00",
        "guests": [],
    }
    data.update(overrides)
    return PublicRegistration.model_validate(data)


@pytest.mark.asyncio
async def test_registration_succeeds_inside_the_window(session) -> None:
    branch, event = await _branch_with_event(session)

    registration = await event_service.register(
        session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
    )

    assert registration.status == "registered"
    assert registration.party_size == 1


@pytest.mark.asyncio
async def test_registration_before_the_window_opens_is_blocked(session) -> None:
    branch, event = await _branch_with_event(session, registration_opens_at=NOW + timedelta(days=1))

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
        )

    assert exc.value.code == "registration_not_open"


@pytest.mark.asyncio
async def test_registration_after_the_window_closes_is_blocked(session) -> None:
    branch, event = await _branch_with_event(session, registration_closes_at=NOW - timedelta(days=1))

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
        )

    assert exc.value.code == "registration_closed"


@pytest.mark.asyncio
async def test_an_event_stays_open_until_its_end_timestamp_not_its_date(session) -> None:
    """The window is judged on the full timestamp: an event ending at 19:00 must
    still accept a 14:00 registration on the same day."""
    same_day_afternoon = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)
    branch, event = await _branch_with_event(
        session,
        registration_opens_at=None,
        registration_closes_at=None,
        event_start_at=datetime(2026, 9, 1, 9, 0, tzinfo=UTC),
        event_end_at=datetime(2026, 9, 1, 19, 0, tzinfo=UTC),
    )

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(),
        now=same_day_afternoon,
        source="public",
    )

    assert registration.id is not None


@pytest.mark.asyncio
async def test_a_finished_event_is_blocked(session) -> None:
    branch, event = await _branch_with_event(
        session,
        registration_opens_at=None,
        registration_closes_at=None,
        event_start_at=NOW - timedelta(days=3),
        event_end_at=NOW - timedelta(days=3, hours=-6),
    )

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
        )

    assert exc.value.code == "event_ended"


@pytest.mark.asyncio
async def test_capacity_counts_guests_not_registrations(session) -> None:
    branch, event = await _branch_with_event(session, capacity=3)
    await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(guests=[{"name": "Budi"}]),
        now=NOW,
        source="public",
    )

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session,
            event=event,
            branch=branch,
            payload=_registration(
                email="lain@example.test", guests=[{"name": "A"}, {"name": "B"}]
            ),
            now=NOW,
            source="public",
        )

    assert exc.value.code == "event_full"


@pytest.mark.asyncio
async def test_a_closed_day_is_rejected(session) -> None:
    branch, event = await _branch_with_event(session)
    branch.closures.append(
        BranchClosure(
            starts_at_local=datetime(2026, 9, 7, 0, 0),
            ends_at_local=datetime(2026, 9, 7, 23, 59),
            full_day=True,
            public_label="Libur",
        )
    )
    await session.commit()

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
        )

    assert exc.value.code == "branch_closed"


@pytest.mark.asyncio
async def test_a_day_with_no_opening_hours_is_rejected(session) -> None:
    branch, event = await _branch_with_event(session)

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session,
            event=event,
            branch=branch,
            payload=_registration(visitDate="2026-09-13"),  # a Sunday, day 7, no hours
            now=NOW,
            source="public",
        )

    assert exc.value.code == "branch_closed"


@pytest.mark.asyncio
async def test_the_same_email_cannot_register_twice_for_one_event(session) -> None:
    branch, event = await _branch_with_event(session)
    await event_service.register(
        session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
    )

    with pytest.raises(RegistrationBlocked) as exc:
        await event_service.register(
            session,
            event=event,
            branch=branch,
            payload=_registration(email="RINA@example.test"),
            now=NOW,
            source="public",
        )

    assert exc.value.code == "already_registered"


@pytest.mark.asyncio
async def test_a_cancelled_registration_frees_the_email_and_the_seat(session) -> None:
    branch, event = await _branch_with_event(session, capacity=1)
    first = await event_service.register(
        session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
    )
    first.status = "cancelled"
    await session.commit()

    again = await event_service.register(
        session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
    )

    assert isinstance(again, EventRegistration)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_event_service.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains.events.schemas'`.

- [ ] **Step 3: Write the schemas**

Create `apps/api/app/domains/events/schemas.py`:

```python
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class EventSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class EventCreate(EventSchema):
    branch_id: int | None = None
    name: str = Field(min_length=1, max_length=200)
    description_html: str = ""
    venue: str | None = Field(default=None, max_length=300)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    color: str | None = Field(default=None, max_length=20)
    is_active: bool = True


class EventUpdate(EventSchema):
    branch_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description_html: str | None = None
    venue: str | None = Field(default=None, max_length=300)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    color: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class EventResponse(EventSchema):
    id: int
    public_id: UUID  # dumped with mode="json", so it reaches the wire as a string
    branch_id: int | None = None
    branch_name: str | None = None
    name: str
    description_html: str
    venue: str | None = None
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = None
    cover_image_url: str | None = None
    color: str | None = None
    is_active: bool
    registration_count: int = 0
    head_count: int = 0


class GuestInput(EventSchema):
    name: str = Field(min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)


class PublicRegistration(EventSchema):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)
    visit_date: date | None = None
    visit_slot: str | None = Field(default=None, max_length=40)
    guests: list[GuestInput] = Field(default_factory=list)


class RegistrationUpdate(EventSchema):
    status: str | None = None
    follow_up: bool | None = None
    notes: str | None = None
    visit_date: date | None = None
    visit_slot: str | None = Field(default=None, max_length=40)


class RegistrationResponse(EventSchema):
    id: int
    public_id: UUID
    event_id: int
    event_name: str | None = None
    branch_id: int | None = None
    branch_name: str | None = None
    guest_name: str
    email: str
    mobile: str | None = None
    party_size: int
    visit_date: date | None = None
    visit_slot: str | None = None
    status: str
    follow_up: bool
    notes: str | None = None
    source: str
    attended_at: datetime | None = None
    guests: list[GuestInput] = Field(default_factory=list)
    created_at: datetime | None = None
```

- [ ] **Step 4: Write the service**

Create `apps/api/app/domains/events/service.py`:

```python
from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch
from app.domains.events.models import (
    REGISTRATION_STATUSES,
    Event,
    EventRegistration,
    EventRegistrationGuest,
)
from app.domains.events.sanitize import sanitize_html
from app.domains.events.schemas import (
    EventCreate,
    EventUpdate,
    PublicRegistration,
    RegistrationUpdate,
)

# A registration in one of these states no longer holds a seat or an email slot.
RELEASED_STATUSES = ("cancelled",)


class EventNotFoundError(Exception):
    pass


class RegistrationNotFoundError(Exception):
    pass


class RegistrationBlocked(Exception):
    """Why a registration cannot be accepted. `code` is the wire contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _as_utc(value: datetime | None) -> datetime | None:
    """SQLite hands back naive datetimes even for timezone-aware columns; treat
    those as UTC so comparisons against `now` never raise."""
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def registration_block(event: Event, now: datetime) -> tuple[str, str] | None:
    """Why this event cannot be registered for right now, or None when it is open.
    Every comparison is against the full timestamp, not the calendar date."""
    opens_at = _as_utc(event.registration_opens_at)
    closes_at = _as_utc(event.registration_closes_at)
    if opens_at and now < opens_at:
        return ("registration_not_open", "Registration for this event has not opened yet.")
    if closes_at and now > closes_at:
        return ("registration_closed", "Registration for this event has closed.")
    ends_at = _as_utc(event.event_end_at or event.event_start_at)
    if ends_at and now > ends_at:
        return ("event_ended", "This event has already taken place.")
    return None


def branch_accepts_date(branch: Branch, visit_date: date) -> bool:
    """A date works if the branch has active opening hours for that ISO weekday and
    no active closure covers it."""
    iso_day = visit_date.isoweekday()
    if not any(row.day_of_week == iso_day and row.active for row in branch.opening_hours):
        return False
    for closure in branch.closures:
        if not closure.active:
            continue
        if closure.starts_at_local.date() <= visit_date <= closure.ends_at_local.date():
            return False
    return True


class EventService:
    async def list(
        self,
        session: AsyncSession,
        *,
        branch_ids: list[int] | None = None,
        include_inactive: bool = True,
    ) -> list[tuple[Event, int, int]]:
        """Returns (event, registration_count, head_count). Counts come from one
        grouped query rather than a per-row lazy load."""
        query = select(Event).where(Event.deleted_at.is_(None)).order_by(Event.id.desc())
        if branch_ids is not None:
            query = query.where(Event.branch_id.in_(branch_ids))
        if not include_inactive:
            query = query.where(Event.is_active.is_(True))
        events = list((await session.scalars(query)).all())
        if not events:
            return []

        counts = await session.execute(
            select(
                EventRegistration.event_id,
                func.count(EventRegistration.id),
                func.coalesce(func.sum(EventRegistration.party_size), 0),
            )
            .where(
                EventRegistration.event_id.in_([event.id for event in events]),
                EventRegistration.status.not_in(RELEASED_STATUSES),
            )
            .group_by(EventRegistration.event_id)
        )
        by_event = {row[0]: (row[1], row[2]) for row in counts}
        return [(event, *by_event.get(event.id, (0, 0))) for event in events]

    async def get(self, session: AsyncSession, event_id: int) -> Event:
        event = await session.scalar(
            select(Event).where(Event.id == event_id, Event.deleted_at.is_(None))
        )
        if event is None:
            raise EventNotFoundError
        return event

    async def create(
        self, session: AsyncSession, payload: EventCreate, *, created_by_user_id: int | None
    ) -> Event:
        data = payload.model_dump()
        data["description_html"] = sanitize_html(data.get("description_html"))
        event = Event(**data, created_by_user_id=created_by_user_id)
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    async def update(self, session: AsyncSession, event_id: int, payload: EventUpdate) -> Event:
        event = await self.get(session, event_id)
        changes = payload.model_dump(exclude_unset=True)
        if "description_html" in changes:
            changes["description_html"] = sanitize_html(changes["description_html"])
        for key, value in changes.items():
            setattr(event, key, value)
        await session.commit()
        await session.refresh(event)
        return event

    async def delete(self, session: AsyncSession, event_id: int) -> None:
        event = await self.get(session, event_id)
        event.deleted_at = datetime.now(UTC)
        await session.commit()

    async def open_tour_event(self, session: AsyncSession, branch: Branch, now: datetime) -> Event | None:
        """The event a visitor to this branch's tour page should see: an active
        event for this branch (or a company-wide one) that is currently open,
        soonest first."""
        candidates = await session.scalars(
            select(Event)
            .where(
                Event.deleted_at.is_(None),
                Event.is_active.is_(True),
                Event.branch_id.in_([branch.id, None]),
            )
            .order_by(Event.event_start_at.is_(None), Event.event_start_at)
        )
        for event in candidates:
            if registration_block(event, now) is None:
                return event
        return None

    async def head_count(self, session: AsyncSession, event_id: int) -> int:
        return int(
            await session.scalar(
                select(func.coalesce(func.sum(EventRegistration.party_size), 0)).where(
                    EventRegistration.event_id == event_id,
                    EventRegistration.status.not_in(RELEASED_STATUSES),
                )
            )
            or 0
        )

    async def register(
        self,
        session: AsyncSession,
        *,
        event: Event,
        branch: Branch | None,
        payload: PublicRegistration,
        now: datetime,
        source: str,
    ) -> EventRegistration:
        block = registration_block(event, now)
        if block:
            raise RegistrationBlocked(*block)

        email = payload.email.strip().lower()
        if "@" not in email:
            raise RegistrationBlocked("validation_error", "Email must be a valid email address.")

        if payload.visit_date is not None and branch is not None:
            if not branch_accepts_date(branch, payload.visit_date):
                raise RegistrationBlocked(
                    "branch_closed", "This branch is closed on the date you chose."
                )

        duplicate = await session.scalar(
            select(EventRegistration.id).where(
                EventRegistration.event_id == event.id,
                func.lower(EventRegistration.email) == email,
                EventRegistration.status.not_in(RELEASED_STATUSES),
            )
        )
        if duplicate is not None:
            raise RegistrationBlocked(
                "already_registered", "This email is already registered for this event."
            )

        heads = 1 + len(payload.guests)
        if event.capacity is not None:
            taken = await self.head_count(session, event.id)
            if taken + heads > event.capacity:
                raise RegistrationBlocked("event_full", "This event is fully booked.")

        registration = EventRegistration(
            event_id=event.id,
            guest_name=payload.name.strip(),
            email=email,
            mobile=payload.mobile,
            party_size=heads,
            visit_date=payload.visit_date,
            visit_slot=payload.visit_slot,
            source=source,
        )
        for guest in payload.guests:
            registration.guests.append(EventRegistrationGuest(**guest.model_dump()))
        session.add(registration)
        await session.commit()
        await session.refresh(registration)
        return registration

    async def list_registrations(
        self,
        session: AsyncSession,
        *,
        branch_ids: list[int] | None = None,
        event_id: int | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> list[EventRegistration]:
        statement = (
            select(EventRegistration)
            .join(Event, Event.id == EventRegistration.event_id)
            .where(Event.deleted_at.is_(None))
            .order_by(EventRegistration.created_at.desc(), EventRegistration.id.desc())
        )
        if branch_ids is not None:
            statement = statement.where(Event.branch_id.in_(branch_ids))
        if event_id is not None:
            statement = statement.where(EventRegistration.event_id == event_id)
        if status:
            statement = statement.where(EventRegistration.status == status)
        if query:
            pattern = f"%{query.strip().lower()}%"
            statement = statement.where(
                func.lower(EventRegistration.guest_name).like(pattern)
                | func.lower(EventRegistration.email).like(pattern)
            )
        return list((await session.scalars(statement)).all())

    async def get_registration(self, session: AsyncSession, registration_id: int) -> EventRegistration:
        registration = await session.scalar(
            select(EventRegistration).where(EventRegistration.id == registration_id)
        )
        if registration is None:
            raise RegistrationNotFoundError
        return registration

    async def update_registration(
        self,
        session: AsyncSession,
        registration_id: int,
        payload: RegistrationUpdate,
        *,
        acting_user_id: int | None,
    ) -> EventRegistration:
        registration = await self.get_registration(session, registration_id)
        changes = payload.model_dump(exclude_unset=True)

        new_status = changes.get("status")
        if new_status is not None and new_status not in REGISTRATION_STATUSES:
            raise RegistrationBlocked("invalid_status", f"Unknown status '{new_status}'.")

        if new_status == "attended" and registration.status != "attended":
            registration.attended_at = datetime.now(UTC)
            registration.attended_by_user_id = acting_user_id
        if new_status is not None and new_status != "attended":
            registration.attended_at = None
            registration.attended_by_user_id = None

        if changes.get("follow_up") is True and not registration.follow_up:
            registration.follow_up_at = datetime.now(UTC)
        if changes.get("follow_up") is False:
            registration.follow_up_at = None

        for key, value in changes.items():
            setattr(registration, key, value)
        await session.commit()
        await session.refresh(registration)
        return registration


event_service = EventService()
```

- [ ] **Step 5: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_event_service.py -q`
Expected: 10 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/domains/events/schemas.py apps/api/app/domains/events/service.py apps/api/tests/test_event_service.py
git commit -m "feat(api): add the event service with one shared registration gate"
```

---

### Task 9: Event admin router

**Files:**
- Create: `apps/api/app/api/v1/admin/events.py`
- Modify: `apps/api/app/api/v1/router.py`
- Test: `apps/api/tests/test_event_admin_api.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_event_admin_api.py`:

```python
from __future__ import annotations

from tests.conftest import admin_user


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    return api.client.post(
        "/api/v1/admin/branches",
        json={"slug": slug, "name": name, "timezone": "Asia/Jakarta"},
    ).json()["data"]


def _event(api, branch_id: int | None, name="Book a Tour") -> dict:
    return api.client.post(
        "/api/v1/admin/events",
        json={"branchId": branch_id, "name": name, "descriptionHtml": "<p>Datang ya</p>"},
    ).json()["data"]


def test_create_event_sanitizes_its_description(api) -> None:
    branch = _branch(api)

    created = api.client.post(
        "/api/v1/admin/events",
        json={
            "branchId": branch["id"],
            "name": "Book a Tour",
            "descriptionHtml": "<p>Halo</p><script>alert(1)</script>",
        },
    )

    assert created.status_code == 201
    assert created.json()["data"]["descriptionHtml"] == "<p>Halo</p>"


def test_list_events_carries_the_branch_name_for_the_branch_column(api) -> None:
    branch = _branch(api)
    _event(api, branch["id"])

    listed = api.client.get("/api/v1/admin/events")

    assert listed.status_code == 200
    row = listed.json()["items"][0]
    assert row["branchName"] == "7Magic Jakarta"
    assert row["registrationCount"] == 0


def test_events_can_be_filtered_by_branch(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _event(api, first["id"], name="Tour Jakarta")
    _event(api, second["id"], name="Tour Bali")

    listed = api.client.get(f"/api/v1/admin/events?branchId={second['id']}")

    assert [row["name"] for row in listed.json()["items"]] == ["Tour Bali"]


def test_a_branch_scoped_user_sees_only_its_events(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _event(api, first["id"], name="Tour Jakarta")
    _event(api, second["id"], name="Tour Bali")

    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", second["id"]),)))
    listed = api.client.get("/api/v1/admin/events")

    assert [row["name"] for row in listed.json()["items"]] == ["Tour Bali"]


def test_a_branch_scoped_user_cannot_create_an_event_for_another_branch(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")

    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", second["id"]),)))
    response = api.client.post(
        "/api/v1/admin/events", json={"branchId": first["id"], "name": "Sneaky"}
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "branch_forbidden"


def test_a_branch_scoped_user_cannot_create_an_all_branch_event(api) -> None:
    branch = _branch(api)

    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", branch["id"]),)))
    response = api.client.post("/api/v1/admin/events", json={"branchId": None, "name": "Company-wide"})

    assert response.status_code == 403
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_event_admin_api.py -q`
Expected: FAIL — the event routes 404.

- [ ] **Step 3: Write the router**

Create `apps/api/app/api/v1/admin/events.py`:

```python
"""Event admin routes. Registrations live in event_registrations.py and email
templates in event_emails.py -- one resource family per module."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.api.v1.admin._shared import (
    BranchScope,
    CurrentUser,
    DbSession,
    forbidden_branch,
    not_found,
)
from app.domains.branches.access import EVENT_READ, EVENT_WRITE, AccessSet
from app.domains.events.models import Event
from app.domains.events.schemas import EventCreate, EventResponse, EventUpdate
from app.domains.events.service import EventNotFoundError, event_service

router = APIRouter()


def _payload(event: Event, registration_count: int = 0, head_count: int = 0) -> dict:
    response = EventResponse.model_validate(event).model_dump(by_alias=True, mode="json")
    response["branchName"] = event.branch.name if event.branch else None
    response["registrationCount"] = registration_count
    response["headCount"] = head_count
    return response


@router.get("/events")
async def list_events(
    session: DbSession,
    scope: BranchScope,
    branch_id: int | None = Query(default=None, alias="branchId"),
):
    if not scope.has(EVENT_READ):
        return forbidden_branch()

    permitted = scope.branches_with(EVENT_READ)
    if branch_id is not None:
        try:
            scope.assert_branch(EVENT_READ, branch_id)
        except AccessSet.BranchForbidden:
            return forbidden_branch()
        permitted = [branch_id]

    rows = await event_service.list(session, branch_ids=permitted)
    return {"items": [_payload(event, count, heads) for event, count, heads in rows]}


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate, session: DbSession, scope: BranchScope, user: CurrentUser
):
    # branch_id None is a company-wide event, so only an org-wide grant may create it.
    try:
        scope.assert_branch(EVENT_WRITE, payload.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    event = await event_service.create(session, payload, created_by_user_id=user.id)
    return {"data": _payload(event)}


@router.get("/events/{event_id}")
async def get_event(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    heads = await event_service.head_count(session, event.id)
    return {"data": _payload(event, head_count=heads)}


@router.patch("/events/{event_id}")
async def update_event(
    event_id: int, payload: EventUpdate, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
        if "branch_id" in payload.model_dump(exclude_unset=True):
            scope.assert_branch(EVENT_WRITE, payload.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    event = await event_service.update(session, event_id, payload)
    return {"data": _payload(event)}


@router.delete("/events/{event_id}")
async def delete_event(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    await event_service.delete(session, event_id)
    return {"data": {"deleted": True}}
```

- [ ] **Step 4: Mount it**

In `apps/api/app/api/v1/router.py`, add `events as admin_events` to the `app.api.v1.admin` import and include it the same way as `admin_branches`:

```python
api_router.include_router(
    admin_events.router,
    prefix="/admin",
    tags=["admin-events"],
    dependencies=[Depends(require_admin_user)],
)
```

- [ ] **Step 5: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_event_admin_api.py -q`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/api/v1/admin/events.py apps/api/app/api/v1/router.py apps/api/tests/test_event_admin_api.py
git commit -m "feat(api): expose event admin routes scoped to the caller's branches"
```

---

### Task 10: Registrations router with attendance and CSV export

**Files:**
- Create: `apps/api/app/api/v1/admin/event_registrations.py`
- Modify: `apps/api/app/api/v1/router.py`
- Test: `apps/api/tests/test_event_registration_api.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_event_registration_api.py`:

```python
from __future__ import annotations

import csv
import io

from tests.conftest import admin_user


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    return api.client.post(
        "/api/v1/admin/branches",
        json={"slug": slug, "name": name, "timezone": "Asia/Jakarta"},
    ).json()["data"]


def _event(api, branch_id: int) -> dict:
    return api.client.post(
        "/api/v1/admin/events", json={"branchId": branch_id, "name": "Book a Tour"}
    ).json()["data"]


def _register(api, event_id: int, email="rina@example.test", guests=None) -> dict:
    return api.client.post(
        "/api/v1/admin/event-registrations",
        json={
            "eventId": event_id,
            "name": "Rina",
            "email": email,
            "mobile": "+628111111111",
            "guests": guests or [],
        },
    ).json()["data"]


def test_a_registration_created_in_the_cms_is_sourced_cms(api) -> None:
    event = _event(api, _branch(api)["id"])

    registration = _register(api, event["id"])

    assert registration["source"] == "cms"
    assert registration["status"] == "registered"


def test_party_size_counts_the_extra_guests(api) -> None:
    event = _event(api, _branch(api)["id"])

    registration = _register(api, event["id"], guests=[{"name": "Budi"}, {"name": "Sari"}])

    assert registration["partySize"] == 3
    assert [guest["name"] for guest in registration["guests"]] == ["Budi", "Sari"]


def test_marking_attended_stamps_the_time_and_the_user(api) -> None:
    event = _event(api, _branch(api)["id"])
    registration = _register(api, event["id"])

    updated = api.client.patch(
        f"/api/v1/admin/event-registrations/{registration['id']}",
        json={"status": "attended"},
    )

    assert updated.status_code == 200
    assert updated.json()["data"]["attendedAt"] is not None


def test_registrations_carry_the_branch_column(api) -> None:
    branch = _branch(api)
    event = _event(api, branch["id"])
    _register(api, event["id"])

    listed = api.client.get("/api/v1/admin/event-registrations")

    row = listed.json()["items"][0]
    assert row["branchName"] == "7Magic Jakarta"
    assert row["eventName"] == "Book a Tour"


def test_a_branch_scoped_user_never_sees_another_branch_registrations(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _register(api, _event(api, first["id"])["id"], email="jakarta@example.test")
    _register(api, _event(api, second["id"])["id"], email="bali@example.test")

    api.login(admin_user(roles=["branch_staff"], branch_grants=(("branch_staff", second["id"]),)))
    listed = api.client.get("/api/v1/admin/event-registrations")

    assert [row["email"] for row in listed.json()["items"]] == ["bali@example.test"]


def test_export_returns_csv_with_a_header_row(api) -> None:
    event = _event(api, _branch(api)["id"])
    _register(api, event["id"])

    response = api.client.get("/api/v1/admin/event-registrations/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    rows = list(csv.reader(io.StringIO(response.text)))
    assert rows[0] == [
        "Branch", "Event", "Name", "Email", "Mobile", "Party size",
        "Visit date", "Visit slot", "Status", "Follow up", "Source", "Registered at",
    ]
    assert rows[1][3] == "rina@example.test"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_event_registration_api.py -q`
Expected: FAIL — the registration routes 404.

- [ ] **Step 3: Write the router**

Create `apps/api/app/api/v1/admin/event_registrations.py`:

```python
"""Registration admin routes: list, create at the front desk, update, export."""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse
from pydantic import Field

from app.api.v1.admin._shared import (
    BranchScope,
    CurrentUser,
    DbSession,
    conflict,
    forbidden_branch,
    not_found,
)
from app.domains.branches.access import REGISTRATION_READ, REGISTRATION_WRITE, AccessSet
from app.domains.events.models import EventRegistration
from app.domains.events.schemas import (
    EventSchema,
    GuestInput,
    PublicRegistration,
    RegistrationResponse,
    RegistrationUpdate,
)
from app.domains.events.service import (
    EventNotFoundError,
    RegistrationBlocked,
    RegistrationNotFoundError,
    event_service,
)

router = APIRouter()

CSV_HEADER = [
    "Branch", "Event", "Name", "Email", "Mobile", "Party size",
    "Visit date", "Visit slot", "Status", "Follow up", "Source", "Registered at",
]


class CmsRegistrationCreate(EventSchema):
    event_id: int
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)
    visit_date: str | None = None
    visit_slot: str | None = Field(default=None, max_length=40)
    notes: str | None = None
    guests: list[GuestInput] = Field(default_factory=list)


def _payload(registration: EventRegistration) -> dict:
    response = RegistrationResponse.model_validate(registration).model_dump(
        by_alias=True, mode="json"
    )
    event = registration.event
    response["eventName"] = event.name if event else None
    response["branchId"] = event.branch_id if event else None
    response["branchName"] = event.branch.name if event and event.branch else None
    return response


async def _scoped_rows(session, scope, **filters) -> list[EventRegistration]:
    return await event_service.list_registrations(
        session, branch_ids=scope.branches_with(REGISTRATION_READ), **filters
    )


@router.get("/event-registrations")
async def list_registrations(
    session: DbSession,
    scope: BranchScope,
    event_id: int | None = Query(default=None, alias="eventId"),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
):
    if not scope.has(REGISTRATION_READ):
        return forbidden_branch()
    rows = await _scoped_rows(session, scope, event_id=event_id, status=status_filter, query=q)
    return {"items": [_payload(row) for row in rows]}


@router.post("/event-registrations", status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: CmsRegistrationCreate, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, payload.event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(REGISTRATION_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    public_payload = PublicRegistration.model_validate(
        {
            "name": payload.name,
            "email": payload.email,
            "mobile": payload.mobile,
            "visitDate": payload.visit_date,
            "visitSlot": payload.visit_slot,
            "guests": [guest.model_dump(by_alias=True) for guest in payload.guests],
        }
    )
    try:
        registration = await event_service.register(
            session,
            event=event,
            branch=event.branch,
            payload=public_payload,
            now=datetime.now(UTC),
            source="cms",
        )
    except RegistrationBlocked as blocked:
        return conflict(blocked.code, blocked.message)

    if payload.notes:
        registration.notes = payload.notes
        await session.commit()
        await session.refresh(registration)
    return {"data": _payload(registration)}


@router.patch("/event-registrations/{registration_id}")
async def update_registration(
    registration_id: int,
    payload: RegistrationUpdate,
    session: DbSession,
    scope: BranchScope,
    user: CurrentUser,
):
    try:
        registration = await event_service.get_registration(session, registration_id)
    except RegistrationNotFoundError:
        return not_found("registration_not_found", "Registration not found.")
    try:
        scope.assert_branch(REGISTRATION_WRITE, registration.event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    try:
        registration = await event_service.update_registration(
            session, registration_id, payload, acting_user_id=user.id
        )
    except RegistrationBlocked as blocked:
        return conflict(blocked.code, blocked.message)
    return {"data": _payload(registration)}


@router.get("/event-registrations/export")
async def export_registrations(
    session: DbSession,
    scope: BranchScope,
    event_id: int | None = Query(default=None, alias="eventId"),
    status_filter: str | None = Query(default=None, alias="status"),
):
    if not scope.has(REGISTRATION_READ):
        return forbidden_branch()
    rows = await _scoped_rows(session, scope, event_id=event_id, status=status_filter)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for row in rows:
        event = row.event
        writer.writerow(
            [
                event.branch.name if event and event.branch else "",
                event.name if event else "",
                row.guest_name,
                row.email,
                row.mobile or "",
                row.party_size,
                row.visit_date.isoformat() if row.visit_date else "",
                row.visit_slot or "",
                row.status,
                "yes" if row.follow_up else "no",
                row.source,
                row.created_at.isoformat() if row.created_at else "",
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="event-registrations.csv"'},
    )
```

Note the route order: `/event-registrations/export` is declared after `/event-registrations/{registration_id}` in file order but uses a distinct prefix path, so FastAPI matches it correctly. If a test shows `export` being captured as an id, move the export route above the `{registration_id}` route.

- [ ] **Step 4: Mount it**

Add `event_registrations as admin_event_registrations` to the `app.api.v1.admin` import in `apps/api/app/api/v1/router.py` and include it with prefix `/admin`, tags `["admin-event-registrations"]`, the same `dependencies=[Depends(require_admin_user)]`.

- [ ] **Step 5: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_event_registration_api.py -q`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/api/v1/admin/event_registrations.py apps/api/app/api/v1/router.py apps/api/tests/test_event_registration_api.py
git commit -m "feat(api): manage event registrations from the CMS with CSV export"
```

---

### Task 11: Event emails

**Files:**
- Create: `apps/api/app/domains/events/emails.py`
- Create: `apps/api/app/api/v1/admin/event_emails.py`
- Modify: `apps/api/app/api/v1/router.py`
- Test: `apps/api/tests/test_event_emails.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_event_emails.py`:

```python
from __future__ import annotations

from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.domains.branches.models import Branch, BranchSettings
from app.domains.events.emails import (
    build_replacements,
    default_template,
    notification_recipients,
    render_template,
)
from app.domains.events.models import Event, EventRegistration


@pytest_asyncio.fixture()
async def session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'event-emails.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


def test_placeholders_are_replaced() -> None:
    event = Event(name="Book a Tour", venue="7Magic Jakarta")
    registration = EventRegistration(
        guest_name="Rina Kartika", email="rina@example.test", visit_date=date(2026, 9, 7),
        visit_slot="10:00", party_size=2,
    )

    rendered = render_template(
        "Halo {first_name}, sampai jumpa di {event_name} pada {visit_date} pukul {visit_slot}.",
        build_replacements(event=event, registration=registration, branch_name="7Magic Jakarta"),
    )

    assert rendered == (
        "Halo Rina, sampai jumpa di Book a Tour pada 2026-09-07 pukul 10:00."
    )


def test_an_unknown_placeholder_is_left_alone_rather_than_raising() -> None:
    """An admin typo must not break a send."""
    event = Event(name="Book a Tour")
    registration = EventRegistration(guest_name="Rina", email="rina@example.test")

    rendered = render_template(
        "Halo {first_name}, {tidak_dikenal}",
        build_replacements(event=event, registration=registration, branch_name=None),
    )

    assert rendered == "Halo Rina, {tidak_dikenal}"


def test_every_kind_has_a_default_template() -> None:
    for kind in ("thank_you", "no_show", "cancel"):
        template = default_template(kind)
        assert template["subject"]
        assert "{first_name}" in template["body"]


@pytest.mark.asyncio
async def test_notification_recipients_come_from_the_branch_settings(session) -> None:
    branch = Branch(slug="jakarta", name="7Magic Jakarta", timezone="Asia/Jakarta")
    branch.settings = BranchSettings(
        tour_notification_recipients=["ops@7magic.test", " Sales@7magic.test "]
    )
    session.add(branch)
    await session.commit()

    assert notification_recipients(branch) == ["ops@7magic.test", "sales@7magic.test"]


@pytest.mark.asyncio
async def test_a_branch_with_no_recipients_yields_an_empty_list(session) -> None:
    branch = Branch(slug="bali", name="7Magic Bali", timezone="Asia/Makassar")
    session.add(branch)
    await session.commit()

    assert notification_recipients(branch) == []
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_event_emails.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domains.events.emails'`.

- [ ] **Step 3: Write the email module**

Create `apps/api/app/domains/events/emails.py`:

```python
"""Event email rendering and delivery.

Templates are plain text with `{placeholder}` tokens rather than a template
engine: they are edited by non-developers in a CMS textarea, and an unknown token
must render literally instead of raising mid-send.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch
from app.domains.events.models import Event, EventEmailTemplate, EventRegistration

logger = logging.getLogger(__name__)

PLACEHOLDERS = [
    "first_name",
    "event_name",
    "visit_date",
    "visit_slot",
    "venue",
    "branch_name",
    "party_size",
]

DEFAULT_TEMPLATES: dict[str, dict[str, str]] = {
    "thank_you": {
        "subject": "Terima kasih sudah berkunjung ke {branch_name}",
        "body": (
            "Halo {first_name},\n\n"
            "Terima kasih sudah meluangkan waktu untuk {event_name} di {branch_name}.\n"
            "Kalau ada pertanyaan soal tanggal, dekorasi, atau paket, balas email ini saja.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
    "no_show": {
        "subject": "Kami menunggu Anda di {branch_name}",
        "body": (
            "Halo {first_name},\n\n"
            "Kami tidak bertemu Anda pada {visit_date} pukul {visit_slot}.\n"
            "Mau kami jadwalkan ulang? Balas email ini dengan tanggal yang cocok.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
    "cancel": {
        "subject": "Kunjungan Anda ke {branch_name} dibatalkan",
        "body": (
            "Halo {first_name},\n\n"
            "Kunjungan Anda pada {visit_date} sudah kami batalkan.\n"
            "Kapan pun ingin menjadwalkan lagi, kami siap membantu.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
}


def default_template(kind: str) -> dict[str, str]:
    return dict(DEFAULT_TEMPLATES.get(kind, {"subject": "", "body": "{first_name}"}))


def build_replacements(
    *, event: Event, registration: EventRegistration | None, branch_name: str | None
) -> dict[str, str]:
    first_name = ""
    if registration and registration.guest_name:
        first_name = registration.guest_name.strip().split(" ")[0]
    return {
        "first_name": first_name,
        "event_name": event.name or "",
        "visit_date": registration.visit_date.isoformat()
        if registration and registration.visit_date
        else "",
        "visit_slot": (registration.visit_slot if registration else "") or "",
        "venue": event.venue or "",
        "branch_name": branch_name or "",
        "party_size": str(registration.party_size) if registration else "",
    }


def render_template(text: str, replacements: dict[str, str]) -> str:
    """`str.format` would raise KeyError on an unknown token; replace only the
    tokens we know and leave anything else exactly as typed."""
    rendered = text or ""
    for key, value in replacements.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def notification_recipients(branch: Branch | None) -> list[str]:
    if branch is None or branch.settings is None:
        return []
    seen: list[str] = []
    for raw in branch.settings.tour_notification_recipients or []:
        address = str(raw).strip().lower()
        if address and address not in seen:
            seen.append(address)
    return seen


async def template_for(
    session: AsyncSession, event_id: int, kind: str
) -> EventEmailTemplate | None:
    return await session.scalar(
        select(EventEmailTemplate).where(
            EventEmailTemplate.event_id == event_id, EventEmailTemplate.kind == kind
        )
    )


def registration_confirmation(
    *, event: Event, registration: EventRegistration, branch: Branch | None
) -> tuple[str, str]:
    """The always-on email a guest gets on submit. Distinct from the three admin
    templates, which are sent by hand after the visit."""
    replacements = build_replacements(
        event=event, registration=registration, branch_name=branch.name if branch else None
    )
    subject = render_template("Pendaftaran {event_name} diterima", replacements)
    body = render_template(
        "Halo {first_name},\n\n"
        "Pendaftaran Anda untuk {event_name} sudah kami terima.\n"
        "Tanggal: {visit_date}\nWaktu: {visit_slot}\nJumlah tamu: {party_size}\n"
        "Lokasi: {branch_name}\n\n"
        "Sampai jumpa!\nTim 7Magic",
        replacements,
    )
    return subject, body


def branch_alert(
    *, event: Event, registration: EventRegistration, branch: Branch | None
) -> tuple[str, str]:
    subject = f"Pendaftaran baru: {event.name}"
    lines = [
        f"Nama: {registration.guest_name}",
        f"Email: {registration.email}",
        f"HP: {registration.mobile or '-'}",
        f"Jumlah tamu: {registration.party_size}",
        f"Tanggal: {registration.visit_date.isoformat() if registration.visit_date else '-'}",
        f"Waktu: {registration.visit_slot or '-'}",
        f"Cabang: {branch.name if branch else '-'}",
        f"Sumber: {registration.source}",
    ]
    return subject, "\n".join(lines)
```

- [ ] **Step 4: Run the email tests**

Run: `cd apps/api && uv run pytest tests/test_event_emails.py -q`
Expected: 5 passed.

- [ ] **Step 5: Write the template router**

Create `apps/api/app/api/v1/admin/event_emails.py`:

```python
"""Per-event email templates: read, save, preview."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import Field

from app.api.v1.admin._shared import BranchScope, DbSession, conflict, forbidden_branch, not_found
from app.domains.branches.access import EVENT_READ, EVENT_WRITE, AccessSet
from app.domains.events.emails import (
    PLACEHOLDERS,
    build_replacements,
    default_template,
    render_template,
    template_for,
)
from app.domains.events.models import TEMPLATE_KINDS, EventEmailTemplate
from app.domains.events.schemas import EventSchema
from app.domains.events.service import EventNotFoundError, event_service

router = APIRouter()


class TemplateUpsert(EventSchema):
    subject: str = Field(default="", max_length=300)
    body: str = ""
    enabled: bool = False


def _template_payload(kind: str, row: EventEmailTemplate | None) -> dict:
    fallback = default_template(kind)
    return {
        "kind": kind,
        "subject": row.subject if row and row.subject else fallback["subject"],
        "body": row.body if row and row.body else fallback["body"],
        "enabled": bool(row.enabled) if row else False,
    }


@router.get("/events/{event_id}/email-templates")
async def list_email_templates(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    stored = {row.kind: row for row in event.email_templates}
    return {
        "data": {
            "placeholders": PLACEHOLDERS,
            "templates": [_template_payload(kind, stored.get(kind)) for kind in TEMPLATE_KINDS],
        }
    }


@router.put("/events/{event_id}/email-templates/{kind}")
async def upsert_email_template(
    event_id: int, kind: str, payload: TemplateUpsert, session: DbSession, scope: BranchScope
):
    if kind not in TEMPLATE_KINDS:
        return conflict("invalid_template_kind", f"Unknown template kind '{kind}'.")
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    row = await template_for(session, event_id, kind)
    if row is None:
        row = EventEmailTemplate(event_id=event_id, kind=kind)
        session.add(row)
    row.subject = payload.subject
    row.body = payload.body
    row.enabled = payload.enabled
    await session.commit()
    await session.refresh(row)
    return {"data": _template_payload(kind, row)}


@router.post("/events/{event_id}/email-templates/{kind}/preview")
async def preview_email_template(
    event_id: int, kind: str, payload: TemplateUpsert, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    # Preview against a real registration when one exists, so the team sees the
    # actual shape of a name and date rather than lorem ipsum.
    rows = await event_service.list_registrations(session, event_id=event_id)
    replacements = build_replacements(
        event=event,
        registration=rows[0] if rows else None,
        branch_name=event.branch.name if event.branch else None,
    )
    return {
        "data": {
            "subject": render_template(payload.subject, replacements),
            "body": render_template(payload.body, replacements),
        }
    }
```

- [ ] **Step 6: Mount it and add the router test**

Add `event_emails as admin_event_emails` to the `app.api.v1.admin` import in `apps/api/app/api/v1/router.py` and include it with prefix `/admin`, tags `["admin-event-emails"]`, `dependencies=[Depends(require_admin_user)]`.

Append to `apps/api/tests/test_event_admin_api.py`:

```python
def test_email_templates_fall_back_to_the_defaults(api) -> None:
    event = _event(api, _branch(api)["id"])

    response = api.client.get(f"/api/v1/admin/events/{event['id']}/email-templates")

    assert response.status_code == 200
    body = response.json()["data"]
    assert [row["kind"] for row in body["templates"]] == ["thank_you", "no_show", "cancel"]
    assert body["templates"][0]["enabled"] is False
    assert "first_name" in body["placeholders"]


def test_saving_then_previewing_a_template_substitutes_placeholders(api) -> None:
    event = _event(api, _branch(api)["id"])

    saved = api.client.put(
        f"/api/v1/admin/events/{event['id']}/email-templates/thank_you",
        json={"subject": "Terima kasih", "body": "Halo {first_name}", "enabled": True},
    )
    preview = api.client.post(
        f"/api/v1/admin/events/{event['id']}/email-templates/thank_you/preview",
        json={"subject": "Terima kasih", "body": "Halo {first_name}", "enabled": True},
    )

    assert saved.status_code == 200
    assert saved.json()["data"]["enabled"] is True
    assert preview.json()["data"]["body"] == "Halo "  # no registrations yet
```

- [ ] **Step 7: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_event_emails.py tests/test_event_admin_api.py -q`
Expected: 13 passed.

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/domains/events/emails.py apps/api/app/api/v1/admin/event_emails.py apps/api/app/api/v1/router.py apps/api/tests/test_event_emails.py apps/api/tests/test_event_admin_api.py
git commit -m "feat(api): render and manage per-event email templates"
```

---

### Task 12: Public Book a Tour endpoints

**Files:**
- Create: `apps/api/app/api/v1/public/__init__.py`
- Create: `apps/api/app/api/v1/public/tour.py`
- Modify: `apps/api/app/api/v1/router.py`
- Test: `apps/api/tests/test_public_tour_api.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_public_tour_api.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import app.api.v1.public.tour as tour_module


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    branch = api.client.post(
        "/api/v1/admin/branches",
        json={
            "slug": slug,
            "name": name,
            "timezone": "Asia/Jakarta",
            "publicEmail": f"{slug}@7magic.test",
        },
    ).json()["data"]
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={
            "items": [
                {"dayOfWeek": day, "opensAtLocal": "10:00:00", "closesAtLocal": "18:00:00"}
                for day in range(1, 7)
            ]
        },
    )
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/settings",
        json={"tourNotificationRecipients": ["ops@7magic.test"]},
    )
    return branch


def _open_event(api, branch_id: int, **overrides) -> dict:
    now = datetime.now(UTC)
    body = {
        "branchId": branch_id,
        "name": "Book a Tour",
        "descriptionHtml": "<p>Datang ya</p>",
        "registrationOpensAt": (now - timedelta(days=1)).isoformat(),
        "registrationClosesAt": (now + timedelta(days=30)).isoformat(),
        "eventStartAt": (now + timedelta(days=31)).isoformat(),
    }
    body.update(overrides)
    return api.client.post("/api/v1/admin/events", json=body).json()["data"]


def _next_weekday(offset_days: int = 7) -> str:
    """A date the branch is open on: Monday-Saturday."""
    candidate = (datetime.now(UTC) + timedelta(days=offset_days)).date()
    while candidate.isoweekday() == 7:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def test_branch_list_shows_only_active_bookable_branches(api) -> None:
    _branch(api)
    hidden = _branch(api, slug="bali", name="7Magic Bali")
    api.client.patch(f"/api/v1/admin/branches/{hidden['id']}", json={"bookable": False})

    response = api.client.get("/api/v1/public/tour/branches")

    assert response.status_code == 200
    assert [row["slug"] for row in response.json()["items"]] == ["jakarta"]


def test_branch_detail_carries_the_open_event_hours_and_closures(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])
    api.client.post(
        f"/api/v1/admin/branches/{branch['id']}/closures",
        json={
            "startsAtLocal": "2026-12-25T00:00:00",
            "endsAtLocal": "2026-12-25T23:59:00",
            "fullDay": True,
            "publicLabel": "Libur Natal",
        },
    )

    response = api.client.get("/api/v1/public/tour/branches/jakarta")

    body = response.json()["data"]
    assert body["branch"]["name"] == "7Magic Jakarta"
    assert body["event"]["registrationOpen"] is True
    assert [row["dayOfWeek"] for row in body["openingHours"]] == [1, 2, 3, 4, 5, 6]
    assert body["closedDates"] == ["2026-12-25"]


def test_registering_creates_the_row_and_sends_both_emails(api, monkeypatch) -> None:
    sent: list[dict] = []

    async def fake_send(**kwargs):
        sent.append(kwargs)

    monkeypatch.setattr(tour_module, "send_email", fake_send)

    branch = _branch(api)
    _open_event(api, branch["id"])

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={
            "name": "Rina Kartika",
            "email": "rina@example.test",
            "mobile": "+628111111111",
            "visitDate": _next_weekday(),
            "visitSlot": "10:00",
            "guests": [{"name": "Budi"}],
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["partySize"] == 2
    assert [call["to"] for call in sent] == [["rina@example.test"], ["ops@7magic.test"]]


def test_a_failing_email_still_returns_201(api, monkeypatch) -> None:
    """A Resend outage must not cost a lead."""

    async def exploding_send(**kwargs):
        raise RuntimeError("resend is down")

    monkeypatch.setattr(tour_module, "send_email", exploding_send)

    branch = _branch(api)
    _open_event(api, branch["id"])

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={"name": "Rina", "email": "rina@example.test", "visitDate": _next_weekday()},
    )

    assert response.status_code == 201

    listed = api.client.get("/api/v1/admin/event-registrations")
    assert [row["email"] for row in listed.json()["items"]] == ["rina@example.test"]


def test_registering_for_a_closed_window_returns_409(api, monkeypatch) -> None:
    async def fake_send(**kwargs):
        return None

    monkeypatch.setattr(tour_module, "send_email", fake_send)

    branch = _branch(api)
    now = datetime.now(UTC)
    _open_event(
        api,
        branch["id"],
        registrationOpensAt=(now - timedelta(days=10)).isoformat(),
        registrationClosesAt=(now - timedelta(days=1)).isoformat(),
    )

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={"name": "Rina", "email": "rina@example.test", "visitDate": _next_weekday()},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] in {"registration_closed", "no_open_event"}


def test_an_unknown_branch_slug_returns_404(api) -> None:
    response = api.client.get("/api/v1/public/tour/branches/tidak-ada")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "branch_not_found"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/api && uv run pytest tests/test_public_tour_api.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.api.v1.public'`.

- [ ] **Step 3: Check how mail is actually sent**

Run: `cd apps/api && grep -n "def .*send\|async def" app/services/email.py`

Use whatever async send function that module exposes. If it exposes only `render_lead_email` and an inline `httpx` post, add this thin wrapper to `apps/api/app/services/email.py` so the tour endpoint has one seam to patch:

```python
async def send_email(*, to: list[str], subject: str, text: str, reply_to: str | None = None) -> None:
    """Fire-and-forget plain-text send. Raises on transport failure; callers that
    must not fail the request catch it themselves."""
    settings = get_settings()
    if not settings.resend_api_key or not to:
        return
    payload = {
        "from": settings.resend_from_address,
        "to": to,
        "subject": subject,
        "text": text,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            RESEND_ENDPOINT,
            json=payload,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        )
        response.raise_for_status()
```

Match the setting names to what `app/core/config.py` actually defines — run `grep -n "resend" app/core/config.py` and use those exact attribute names.

- [ ] **Step 4: Write the public router**

Create `apps/api/app/api/v1/public/__init__.py` (empty) and `apps/api/app/api/v1/public/tour.py`:

```python
"""Public Book a Tour endpoints. No auth: these are the website's forms."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi import Depends

from app.core.database import get_db_session
from app.core.errors import error_response
from app.domains.branches.models import Branch
from app.domains.branches.service import BranchNotFoundError, branch_service
from app.domains.events.emails import branch_alert, notification_recipients, registration_confirmation
from app.domains.events.models import Event, EventRegistration
from app.domains.events.schemas import PublicRegistration
from app.domains.events.service import (
    RegistrationBlocked,
    branch_accepts_date,
    event_service,
    registration_block,
)
from app.services.email import send_email

logger = logging.getLogger(__name__)
router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# How far ahead the page advertises closures. Longer than any sane tour window and
# short enough to keep the payload small.
CLOSURE_HORIZON_DAYS = 120


def _branch_payload(branch: Branch) -> dict:
    return {
        "id": branch.id,
        "slug": branch.slug,
        "name": branch.name,
        "city": branch.city,
        "addressLine1": branch.address_line1,
        "addressLine2": branch.address_line2,
        "timezone": branch.timezone,
        "publicPhone": branch.public_phone,
        "publicEmail": branch.public_email,
        "whatsappNumber": branch.whatsapp_number,
        "websiteUrl": branch.website_url,
    }


def _event_payload(event: Event, now: datetime) -> dict:
    block = registration_block(event, now)
    return {
        "id": event.id,
        "publicId": str(event.public_id),
        "name": event.name,
        "descriptionHtml": event.description_html,
        "coverImageUrl": event.cover_image_url,
        "venue": event.venue,
        "eventStartAt": event.event_start_at.isoformat() if event.event_start_at else None,
        "eventEndAt": event.event_end_at.isoformat() if event.event_end_at else None,
        "registrationOpen": block is None,
        "registrationClosedReason": block[1] if block else None,
    }


def _closed_dates(branch: Branch, today: date) -> list[str]:
    horizon = today + timedelta(days=CLOSURE_HORIZON_DAYS)
    closed: list[str] = []
    for closure in branch.closures:
        if not closure.active:
            continue
        cursor = max(closure.starts_at_local.date(), today)
        last = min(closure.ends_at_local.date(), horizon)
        while cursor <= last:
            closed.append(cursor.isoformat())
            cursor += timedelta(days=1)
    return sorted(set(closed))


@router.get("/tour/branches")
async def list_tour_branches(session: DbSession):
    branches = await branch_service.list(session, active_only=True)
    return {"items": [_branch_payload(branch) for branch in branches if branch.bookable]}


@router.get("/tour/branches/{slug}")
async def get_tour_branch(slug: str, session: DbSession):
    try:
        branch = await branch_service.get_by_slug(session, slug)
    except BranchNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )
    if not branch.active or not branch.bookable:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )

    now = datetime.now(UTC)
    event = await event_service.open_tour_event(session, branch, now)
    return {
        "data": {
            "branch": _branch_payload(branch),
            "settings": {
                "tourIntroHtml": branch.settings.tour_intro_html if branch.settings else None,
                "arrivalInstructions": branch.settings.arrival_instructions
                if branch.settings
                else None,
                "parkingNotes": branch.settings.parking_notes if branch.settings else None,
            },
            "event": _event_payload(event, now) if event else None,
            "openingHours": [
                {
                    "dayOfWeek": row.day_of_week,
                    "opensAtLocal": row.opens_at_local.isoformat(),
                    "closesAtLocal": row.closes_at_local.isoformat(),
                }
                for row in branch.opening_hours
                if row.active
            ],
            "closedDates": _closed_dates(branch, now.date()),
        }
    }


@router.post("/tour/branches/{slug}/register", status_code=status.HTTP_201_CREATED)
async def register_for_tour(slug: str, payload: PublicRegistration, session: DbSession):
    try:
        branch = await branch_service.get_by_slug(session, slug)
    except BranchNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )

    now = datetime.now(UTC)
    event = await event_service.open_tour_event(session, branch, now)
    if event is None:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="no_open_event",
            message="This branch is not taking tour bookings right now.",
        )

    try:
        registration = await event_service.register(
            session, event=event, branch=branch, payload=payload, now=now, source="public"
        )
    except RegistrationBlocked as blocked:
        code = 422 if blocked.code == "validation_error" else status.HTTP_409_CONFLICT
        return error_response(status_code=code, code=blocked.code, message=blocked.message)

    await _notify(event=event, registration=registration, branch=branch)

    return {
        "data": {
            "id": registration.id,
            "publicId": str(registration.public_id),
            "partySize": registration.party_size,
            "visitDate": registration.visit_date.isoformat() if registration.visit_date else None,
            "visitSlot": registration.visit_slot,
            "branchName": branch.name,
        }
    }


async def _notify(*, event: Event, registration: EventRegistration, branch: Branch) -> None:
    """Sent after the row is committed, and never allowed to fail the request: a
    mail-provider outage must not cost a lead."""
    reply_to = branch.settings.reply_to_email if branch.settings else branch.public_email
    subject, body = registration_confirmation(
        event=event, registration=registration, branch=branch
    )
    try:
        await send_email(
            to=[registration.email], subject=subject, text=body, reply_to=reply_to
        )
    except Exception:  # noqa: BLE001 -- logged, never re-raised
        logger.exception("tour confirmation email failed for registration %s", registration.id)

    recipients = notification_recipients(branch)
    if not recipients:
        return
    alert_subject, alert_body = branch_alert(
        event=event, registration=registration, branch=branch
    )
    try:
        await send_email(to=recipients, subject=alert_subject, text=alert_body)
    except Exception:  # noqa: BLE001
        logger.exception("branch alert email failed for registration %s", registration.id)
```

- [ ] **Step 5: Mount it**

In `apps/api/app/api/v1/router.py`, add:

```python
from app.api.v1.public import tour as public_tour

api_router.include_router(public_tour.router, prefix="/public", tags=["public-tour"])
```

No auth dependency — these are public.

- [ ] **Step 6: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_public_tour_api.py -q`
Expected: 6 passed.

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/api/v1/public apps/api/app/api/v1/router.py apps/api/app/services/email.py apps/api/tests/test_public_tour_api.py
git commit -m "feat(api): add the public Book a Tour endpoints"
```

---

### Task 13: Migration

**Files:**
- Modify: `apps/api/migrations/env.py`
- Create: `apps/api/migrations/versions/<generated>_branches_and_events.py`
- Test: `apps/api/tests/test_branch_migration.py`

- [ ] **Step 1: Turn on batch mode for SQLite**

In `apps/api/migrations/env.py`, both `context.configure(...)` calls need `render_as_batch=True`. SQLite cannot `ALTER TABLE ... ADD CONSTRAINT`; batch mode rebuilds the table instead, and `user_roles.branch_id` is exactly that case.

```python
        context.configure(
            target_metadata=target_metadata,
            render_as_batch=True,
            ...  # keep the existing keyword arguments
        )
```

and

```python
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )
```

- [ ] **Step 2: Generate the revision**

Run: `cd apps/api && uv run alembic revision --autogenerate -m "branches and events"`
Expected: a new file under `migrations/versions/` creating eight tables and altering `user_roles`.

- [ ] **Step 3: Review and fix the generated file**

Read it and confirm:
- No `JSONB` and no `ARRAY` — `tour_notification_recipients` must be `sa.JSON()`.
- The `user_roles` change is wrapped in `with op.batch_alter_table("user_roles") as batch_op:`. If autogenerate emitted a bare `op.add_column` / `op.drop_constraint`, rewrite it:

```python
    with op.batch_alter_table("user_roles") as batch_op:
        batch_op.add_column(sa.Column("branch_id", sa.Integer(), nullable=True))
        batch_op.drop_constraint("uq_user_roles_user_role", type_="unique")
        batch_op.create_unique_constraint(
            "uq_user_roles_user_role_branch", ["user_id", "role_id", "branch_id"]
        )
        batch_op.create_foreign_key(
            "fk_user_roles_branch_id_branches", "branches", ["branch_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_index("ix_user_roles_branch_id", ["branch_id"])
```

- [ ] **Step 4: Add the data migration**

Append to the generated `upgrade()`, after the schema changes. It seeds a default branch so `/tour` has somewhere to land, and gives it a settings row:

```python
    # A default branch so /tour resolves on day one. Existing role rows already
    # have branch_id NULL, which means org-wide -- today's admins keep full access
    # with no backfill needed.
    branches = sa.table(
        "branches",
        sa.column("id", sa.Integer),
        sa.column("public_id", sa.Uuid),
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("address_line1", sa.String),
        sa.column("city", sa.String),
        sa.column("country_code", sa.String),
        sa.column("timezone", sa.String),
        sa.column("active", sa.Boolean),
        sa.column("bookable", sa.Boolean),
        sa.column("is_default", sa.Boolean),
    )
    op.bulk_insert(
        branches,
        [
            {
                "public_id": uuid.uuid4(),
                "slug": "jakarta",
                "name": "7Magic Jakarta",
                "address_line1": "",
                "city": "jakarta",
                "country_code": "ID",
                "timezone": "Asia/Jakarta",
                "active": True,
                "bookable": True,
                "is_default": True,
            }
        ],
    )
    connection = op.get_bind()
    branch_id = connection.execute(
        sa.text("SELECT id FROM branches WHERE slug = 'jakarta'")
    ).scalar_one()
    op.bulk_insert(
        sa.table(
            "branch_settings",
            sa.column("branch_id", sa.Integer),
            sa.column("tour_notification_recipients", sa.JSON),
        ),
        [{"branch_id": branch_id, "tour_notification_recipients": []}],
    )
```

Add `import uuid` at the top of the migration file.

In `downgrade()`, drop the eight tables and reverse the `user_roles` change inside `batch_alter_table`.

- [ ] **Step 5: Write the migration test**

Create `apps/api/tests/test_branch_migration.py`:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]


def test_migrations_run_on_a_fresh_sqlite_database(tmp_path) -> None:
    """Guards the SQLite-compatibility rules: JSONB, ARRAY or a bare ALTER on
    user_roles all fail here rather than in production."""
    database = tmp_path / "migration-test.db"
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=API_ROOT,
        env={
            **dict(__import__("os").environ),
            "DATABASE_URL": f"sqlite+aiosqlite:///{database}",
        },
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert database.exists()
```

- [ ] **Step 6: Run it**

Run: `cd apps/api && uv run pytest tests/test_branch_migration.py -q`
Expected: 1 passed.

- [ ] **Step 7: Apply it locally**

Run: `cd apps/api && uv run alembic upgrade head`
Expected: no error; `7magic.db` gains the new tables.

- [ ] **Step 8: Commit**

```bash
git add apps/api/migrations apps/api/tests/test_branch_migration.py
git commit -m "feat(api): migrate in branches, events and branch-scoped roles"
```

---

### Task 14: Document the rule that keeps routers thin

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add the section**

In `CLAUDE.md`, immediately after the existing `**API layout**:` paragraph in "How the domain fits together", add:

```markdown
**Branches and events live in domain packages.** `app/domains/branches/` and
`app/domains/events/` each own their models, schemas, service and (for events)
email rendering. Articles, venues and showcases predate this and stay in the flat
`app/models|services|schemas` layout; do not migrate them opportunistically.

**Routers are one resource each, and hold no queries.** `app/api/v1/admin/` has a
module per resource (`branches.py`, `events.py`, `event_registrations.py`,
`event_emails.py`) carrying HTTP concerns only — validation, status codes,
response shaping, permission checks. Every query and business rule belongs in the
domain's `service.py`. Split a router by resource when it passes ~400 lines. The
platform this was ported from let one admin module absorb every resource and it
reached 7,842 lines; the resource-per-module rule is what prevents that, and the
line count is only the alarm.

**Permissions are branch-scoped.** A `user_roles` row with `branch_id IS NULL` is
org-wide; a row with a branch is scoped to it. Routers never read role rows —
they depend on `BranchScope` from `app/api/v1/admin/_shared.py` and call
`scope.assert_branch(permission, branch_id)` before any write, and pass
`scope.branches_with(permission)` to the service on any list. `branches_with`
returning `None` means *unbounded*, not *none*.

**Opening hours are ISO days: Monday = 1, Sunday = 7.**
```

- [ ] **Step 2: Run the full suite and the linter**

Run: `cd apps/api && uv run pytest -q && uv run ruff check .`
Expected: all tests pass, `All checks passed!`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: record the branch, router and permission rules for the new modules"
```

---

## Done means

- `cd apps/api && uv run pytest -q` is green, including the seven new test files.
- `uv run ruff check .` is clean.
- `uv run alembic upgrade head` runs on a fresh SQLite file and on Postgres.
- No file created by this plan exceeds ~400 lines. Check with:
  `find apps/api/app/domains apps/api/app/api/v1/admin apps/api/app/api/v1/public -name '*.py' | xargs wc -l | sort -n`

Plan 2 (`docs/superpowers/plans/2026-08-11-branches-events-ui.md`) builds the CMS screens and the public tour pages on top of these endpoints.
