# DB Sessions + Argon2 Auth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hand-rolled JWT bearer auth with opaque, revocable, server-side DB sessions, and replace PBKDF2 password hashing with argon2id.

**Architecture:** The API issues a random opaque token at login and stores only its SHA-256 in a new `sessions` table (sliding 14-day expiry, extension throttled to once per hour). The CMS keeps owning the httpOnly cookie and forwarding the token as a Bearer header — only the token format changes. All JWT code and the signing secret are deleted.

**Tech Stack:** FastAPI + SQLAlchemy 2 async + Alembic (`apps/api`, managed with `uv`), SvelteKit (`apps/cms`), `argon2-cffi`.

**Spec:** `docs/superpowers/specs/2026-06-12-session-auth-design.md`

**Note on CLAUDE.md GitNexus rules:** GitNexus MCP tools are not connected in this session, so `gitnexus_impact`/`gitnexus_detect_changes` cannot be run. As a substitute, each task lists exactly which symbols it touches; the full test suite is the verification gate. Callers of every modified symbol are enumerated in Task 4 (they are all inside `apps/api/app/api/v1/` and the two test files).

**Test command:** `cd apps/api && uv run pytest` (run from repo root: `cd /Users/bsalim/C/7magic-monorepo/apps/api`).

---

### Task 1: Argon2 password hashing in `app/core/security.py`

Replaces PBKDF2 with argon2id and adds session-token helpers. The JWT functions (`sign_auth_token`, `decode_auth_token`, `_base64url_*`) **stay for now** — they are still imported by the endpoints until Task 4. Existing auth contract tests keep passing because they hash fresh passwords through `hash_password`.

**Files:**
- Modify: `apps/api/pyproject.toml` (via `uv add`)
- Modify: `apps/api/app/core/security.py`
- Create: `apps/api/tests/test_security.py`

- [ ] **Step 1: Add the argon2-cffi dependency**

```bash
cd apps/api && uv add argon2-cffi
```

Expected: `argon2-cffi` appears in `pyproject.toml` dependencies and `uv.lock` updates.

- [ ] **Step 2: Write the failing tests**

Create `apps/api/tests/test_security.py`:

```python
from __future__ import annotations

from argon2 import PasswordHasher

from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    password_needs_rehash,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    password_hash = hash_password("Admin123")

    assert password_hash.startswith("$argon2id$")
    assert verify_password("Admin123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_verify_password_rejects_malformed_hash() -> None:
    assert not verify_password("anything", "not-a-hash")
    assert not verify_password("anything", "")


def test_password_needs_rehash_detects_weak_parameters() -> None:
    weak_hash = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash("pw")

    assert password_needs_rehash(weak_hash)
    assert not password_needs_rehash(hash_password("pw"))
    assert password_needs_rehash("not-a-hash")


def test_session_tokens_are_unique_and_hash_to_hex_sha256() -> None:
    token_a = generate_session_token()
    token_b = generate_session_token()

    assert token_a != token_b
    assert len(token_a) >= 43
    assert hash_session_token(token_a) == hash_session_token(token_a)
    assert hash_session_token(token_a) != hash_session_token(token_b)
    assert len(hash_session_token(token_a)) == 64
    assert all(c in "0123456789abcdef" for c in hash_session_token(token_a))
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_security.py -v`
Expected: FAIL — `ImportError: cannot import name 'generate_session_token'` (and friends).

- [ ] **Step 4: Implement the argon2 functions**

In `apps/api/app/core/security.py`, **delete** the PBKDF2 code (`PBKDF2_ALGORITHM`, `PBKDF2_ITERATIONS`, `SALT_BYTES` constants and the bodies of `hash_password`/`verify_password`) and replace with the code below. **Keep** `sign_auth_token`, `decode_auth_token`, `TOKEN_ALGORITHM`, and `_base64url_encode`/`_base64url_decode` untouched at the bottom of the file (they are removed in Task 4).

```python
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

TOKEN_ALGORITHM = "HS256"
SESSION_TOKEN_BYTES = 32

_password_hasher = PasswordHasher()

# Verified against when a login email has no account, so response timing does
# not reveal whether an email is registered.
DUMMY_PASSWORD_HASH = _password_hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def generate_session_token() -> str:
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
```

(The `base64`/`hmac`/`json`/`datetime`/`Any` imports are still needed by the JWT functions kept below until Task 4.)

- [ ] **Step 5: Run the full suite**

Run: `cd apps/api && uv run pytest`
Expected: ALL PASS — `test_security.py` passes, and `test_auth_contracts.py` still passes because both seeding and verification now use argon2.

- [ ] **Step 6: Commit**

```bash
git add apps/api/pyproject.toml apps/api/uv.lock apps/api/app/core/security.py apps/api/tests/test_security.py
git commit -m "feat(api): replace PBKDF2 with argon2id password hashing"
```

---

### Task 2: `UserSession` model, drop `RefreshToken`, Alembic migration

**Files:**
- Create: `apps/api/app/models/session.py`
- Modify: `apps/api/app/models/user.py` (remove `RefreshToken` class + relationship, add `sessions` relationship)
- Modify: `apps/api/app/models/__init__.py`
- Create: `apps/api/migrations/versions/d4e5f6a7b8c9_replace_refresh_tokens_with_sessions.py`

- [ ] **Step 1: Create the model**

Create `apps/api/app/models/session.py`:

```python
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="sessions")
```

- [ ] **Step 2: Update `apps/api/app/models/user.py`**

Delete the entire `RefreshToken` class (lines ~66-81), the `refresh_tokens` relationship on `User`, and the now-unused `import uuid`. Add the `sessions` relationship. The `User` class relationships section becomes:

```python
    articles: Mapped[list[Article]] = relationship(back_populates="author")
    article_images: Mapped[list[ArticleImage]] = relationship(back_populates="user")
    roles: Mapped[list[UserRole]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list[UserSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
```

And the `TYPE_CHECKING` block becomes:

```python
if TYPE_CHECKING:
    from app.models.article import Article, ArticleImage
    from app.models.session import UserSession
```

- [ ] **Step 3: Update `apps/api/app/models/__init__.py`**

```python
from app.models.article import Article, ArticleCategory, ArticleImage, ArticleTag
from app.models.audit import AuditEvent, ContactLead
from app.models.media import MediaAsset
from app.models.session import UserSession
from app.models.user import Role, User, UserRole
from app.models.venue import Venue, VenuePhoto

__all__ = [
    "Article",
    "ArticleCategory",
    "ArticleImage",
    "ArticleTag",
    "AuditEvent",
    "ContactLead",
    "MediaAsset",
    "Role",
    "User",
    "UserRole",
    "UserSession",
    "Venue",
    "VenuePhoto",
]
```

- [ ] **Step 4: Verify nothing else references `RefreshToken`**

Run: `grep -rn "RefreshToken\|refresh_tokens" apps/api/app apps/api/tests apps/api/scripts`
Expected: no matches outside the migration files. If anything else matches, fix it before continuing.

- [ ] **Step 5: Create the migration**

Create `apps/api/migrations/versions/d4e5f6a7b8c9_replace_refresh_tokens_with_sessions.py`:

```python
"""replace refresh_tokens with sessions

Creates the ``sessions`` table for opaque server-side auth sessions
(token stored as sha256 hex) and drops the unused ``refresh_tokens``
table left over from the initial schema.

Revision ID: d4e5f6a7b8c9
Revises: b2f1a7c9d3e4
Create Date: 2026-06-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "b2f1a7c9d3e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_token_hash"), "sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_sessions_expires_at"), "sessions", ["expires_at"])
    op.drop_table("refresh_tokens")


def downgrade() -> None:
    op.drop_index(op.f("ix_sessions_expires_at"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_token_hash"), table_name="sessions")
    op.drop_table("sessions")
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_token", sa.String(length=512), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
```

Do NOT run `alembic upgrade head` yet — the live DB is applied in Task 7.

- [ ] **Step 6: Run the full suite**

Run: `cd apps/api && uv run pytest`
Expected: ALL PASS (test fixtures use `Base.metadata.create_all`, which now creates `sessions` and no longer creates `refresh_tokens`).

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/models/ apps/api/migrations/versions/d4e5f6a7b8c9_replace_refresh_tokens_with_sessions.py
git commit -m "feat(api): add sessions table, drop unused refresh_tokens"
```

---

### Task 3: Session lifecycle service

**Files:**
- Create: `apps/api/app/services/sessions.py`
- Create: `apps/api/tests/test_sessions_service.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/api/tests/test_sessions_service.py`:

```python
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401  (registers all tables on Base.metadata)
from app.core.database import Base
from app.models import User, UserSession
from app.services.sessions import (
    SESSION_REFRESH_INTERVAL_SECONDS,
    create_session,
    resolve_session,
    revoke_session,
)

TTL_SECONDS = 60 * 60 * 24 * 14


@pytest.fixture()
def db_factory(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'sessions-test.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def setup() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with factory() as db:
            db.add(User(id=1, email="admin@example.com", password_hash="x"))
            await db.commit()

    asyncio.run(setup())
    yield factory
    asyncio.run(engine.dispose())


def test_create_session_stores_hash_not_raw_token(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            record = (await db.execute(select(UserSession))).scalar_one()

            assert record.user_id == 1
            assert record.token_hash != token
            assert len(record.token_hash) == 64
            assert record.expires_at > record.created_at

    asyncio.run(scenario())


def test_resolve_session_returns_record_for_valid_token(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)

            record = await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS)
            assert record is not None
            assert record.user_id == 1

            assert await resolve_session(db, token="unknown-token", ttl_seconds=TTL_SECONDS) is None

    asyncio.run(scenario())


def test_resolve_session_deletes_expired_session(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            record = (await db.execute(select(UserSession))).scalar_one()
            record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
            await db.commit()

            assert await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS) is None
            remaining = (await db.execute(select(UserSession))).scalars().all()
            assert remaining == []

    asyncio.run(scenario())


def test_resolve_session_slides_expiry_when_stale(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            record = (await db.execute(select(UserSession))).scalar_one()
            stale = datetime.now(UTC) - timedelta(seconds=SESSION_REFRESH_INTERVAL_SECONDS + 60)
            record.last_seen_at = stale
            old_expiry = record.expires_at
            await db.commit()

            resolved = await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS)

            assert resolved is not None
            assert resolved.last_seen_at > stale
            assert resolved.expires_at.replace(tzinfo=UTC) > old_expiry.replace(tzinfo=UTC)

    asyncio.run(scenario())


def test_resolve_session_does_not_write_when_fresh(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            before = (await db.execute(select(UserSession))).scalar_one()
            last_seen_before = before.last_seen_at

            resolved = await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS)

            assert resolved is not None
            assert resolved.last_seen_at == last_seen_before

    asyncio.run(scenario())


def test_revoke_session_deletes_row_and_is_idempotent(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)

            await revoke_session(db, token=token)
            assert await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS) is None

            await revoke_session(db, token=token)  # second call must not raise

    asyncio.run(scenario())
```

- [ ] **Step 2: Run to verify failure**

Run: `cd apps/api && uv run pytest tests/test_sessions_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.sessions'`.

- [ ] **Step 3: Implement the service**

Create `apps/api/app/services/sessions.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_session_token, hash_session_token
from app.models import UserSession

# Sliding-window extension is throttled to at most one DB write per session
# per this interval.
SESSION_REFRESH_INTERVAL_SECONDS = 3600


async def create_session(db: AsyncSession, *, user_id: int, ttl_seconds: int) -> str:
    token = generate_session_token()
    now = datetime.now(UTC)
    db.add(
        UserSession(
            token_hash=hash_session_token(token),
            user_id=user_id,
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
    )
    await db.commit()
    return token


async def resolve_session(db: AsyncSession, *, token: str, ttl_seconds: int) -> UserSession | None:
    result = await db.execute(
        select(UserSession).where(UserSession.token_hash == hash_session_token(token))
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None

    now = datetime.now(UTC)
    if _as_utc(record.expires_at) < now:
        await db.delete(record)
        await db.commit()
        return None

    if (now - _as_utc(record.last_seen_at)).total_seconds() >= SESSION_REFRESH_INTERVAL_SECONDS:
        record.last_seen_at = now
        record.expires_at = now + timedelta(seconds=ttl_seconds)
        await db.commit()

    return record


async def revoke_session(db: AsyncSession, *, token: str) -> None:
    await db.execute(delete(UserSession).where(UserSession.token_hash == hash_session_token(token)))
    await db.commit()


def _as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes even for timezone-aware columns.
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
```

- [ ] **Step 4: Run the tests**

Run: `cd apps/api && uv run pytest tests/test_sessions_service.py -v`
Expected: ALL PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services/sessions.py apps/api/tests/test_sessions_service.py
git commit -m "feat(api): add session lifecycle service with sliding expiry"
```

---

### Task 4: Rewire auth endpoints + dependencies; delete JWT

This is the cutover task. Symbols modified: `authenticate_admin_user`, `resolve_admin_token_user` (renamed `resolve_admin_user_by_id`), `require_admin_user`, `login`, `me`, `logout`, `Settings`. Their only callers are `apps/api/app/api/v1/endpoints/{auth,admin}.py`, `apps/api/app/api/v1/dependencies.py`, and the two auth test files — all updated in this task.

**Files:**
- Modify: `apps/api/tests/test_auth_contracts.py`
- Modify: `apps/api/app/services/auth.py`
- Modify: `apps/api/app/api/v1/dependencies.py:28-68` (`require_admin_user` body)
- Modify: `apps/api/app/api/v1/endpoints/auth.py`
- Modify: `apps/api/app/core/security.py` (delete JWT remnants)
- Modify: `apps/api/app/core/config.py:12-13`
- Modify: `.env.example`

- [ ] **Step 1: Add the new failing contract tests**

In `apps/api/tests/test_auth_contracts.py`, add these imports at the top (alongside existing ones):

```python
from datetime import UTC, datetime, timedelta

from app.models import UserSession
from app.services.sessions import SESSION_REFRESH_INTERVAL_SECONDS
```

Append these tests at the end of the file:

```python
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
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd apps/api && uv run pytest tests/test_auth_contracts.py -v`
Expected: the three new tests FAIL (logout currently revokes nothing; no `UserSession` rows are created by login). Existing tests still pass.

- [ ] **Step 3: Update `apps/api/app/services/auth.py`**

Replace `authenticate_admin_user` and `resolve_admin_token_user` with:

```python
async def authenticate_admin_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> AuthenticatedUser:
    user = await _get_user_by_email(session, email)
    if user is None:
        # Burn the same argon2 work as a real check so timing does not
        # reveal whether the email exists.
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
```

Update the imports at the top of the file:

```python
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    password_needs_rehash,
    verify_password,
)
```

Also delete the now-unused `from typing import Any` import (claims dicts are gone). `InvalidTokenSubjectError` stays — it now means "session points at a deleted user".

- [ ] **Step 4: Update `require_admin_user` in `apps/api/app/api/v1/dependencies.py`**

Replace the body after the `missing_token` check (the `decode_auth_token` block and the `resolve_admin_token_user` call) with:

```python
    record = await resolve_session(
        session, token=token, ttl_seconds=settings.session_ttl_seconds
    )
    if record is None:
        raise AuthError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_token",
            message="Session token is invalid or expired.",
        )

    try:
        return await resolve_admin_user_by_id(session, user_id=record.user_id)
```

The three `except` clauses (`InvalidTokenSubjectError`, `InactiveUserError`, `AdminRequiredError`) stay exactly as they are. Update the imports: remove `from app.core.security import decode_auth_token`, change `resolve_admin_token_user` to `resolve_admin_user_by_id` in the `app.services.auth` import, and add:

```python
from app.services.sessions import resolve_session
```

- [ ] **Step 5: Rewrite `apps/api/app/api/v1/endpoints/auth.py`**

Full new content:

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import extract_bearer_token, require_admin_user
from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.core.errors import error_response
from app.schemas.auth import AuthUserResponse, LoginRequest, LoginResponse
from app.services.auth import (
    AdminRequiredError,
    AuthenticatedUser,
    InactiveUserError,
    InvalidCredentialsError,
    authenticate_admin_user,
)
from app.services.sessions import create_session, revoke_session

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    try:
        user = await authenticate_admin_user(session, email=payload.email, password=payload.password)
    except InvalidCredentialsError:
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

    access_token = await create_session(
        session, user_id=user.id, ttl_seconds=settings.session_ttl_seconds
    )
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.session_ttl_seconds,
        user=AuthUserResponse(**user.__dict__),
    )


@router.get("/me", response_model=AuthUserResponse)
async def me(user: Annotated[AuthenticatedUser, Depends(require_admin_user)]):
    return AuthUserResponse(**user.__dict__)


@router.post("/logout")
async def logout(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    token = extract_bearer_token(authorization)
    if token:
        await revoke_session(session, token=token)
    return {"status": "ok"}
```

Note `/me` now delegates to `require_admin_user`; the `AuthError` exception handler in `app/main.py` produces the identical error envelope, so the contract tests for `missing_token`/`invalid_token`/`admin_required` on `/me` keep passing.

- [ ] **Step 6: Delete JWT remnants from `apps/api/app/core/security.py`**

Delete `sign_auth_token`, `decode_auth_token`, `_base64url_encode`, `_base64url_decode`, `TOKEN_ALGORITHM`, and the now-unused imports `base64`, `hmac`, `json`, `timedelta`, `Any`, and `datetime`/`UTC` if nothing else in the file uses them. The file's final import block is:

```python
from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
```

- [ ] **Step 7: Update settings and env example**

In `apps/api/app/core/config.py`, replace lines 12-13:

```python
    auth_token_secret: str = "dev-change-me"
    auth_token_ttl_seconds: int = 60 * 60 * 8
```

with:

```python
    session_ttl_seconds: int = 60 * 60 * 24 * 14
```

In `.env.example` (repo root), replace:

```
AUTH_TOKEN_SECRET=replace-with-a-long-random-secret
AUTH_TOKEN_TTL_SECONDS=28800
```

with:

```
SESSION_TTL_SECONDS=1209600
```

Then verify nothing still references the removed names:

Run: `grep -rn "auth_token_secret\|auth_token_ttl\|AUTH_TOKEN" apps/api/app apps/api/tests apps/api/scripts apps/api/.env .env.example`
Expected: no matches (check `apps/api/.env` manually and delete stale `AUTH_TOKEN_*` lines if present).

- [ ] **Step 8: Run the full suite**

Run: `cd apps/api && uv run pytest`
Expected: ALL PASS, including the three new contract tests.

- [ ] **Step 9: Commit**

```bash
git add apps/api/app apps/api/tests .env.example
git commit -m "feat(api): cut auth over to DB sessions, delete JWT and signing secret"
```

---

### Task 5: Admin password reset script

**Files:**
- Create: `apps/api/scripts/reset_admin_passwords.py`

- [ ] **Step 1: Write the script**

Create `apps/api/scripts/reset_admin_passwords.py` (mirrors the structure of the existing `scripts/seed_admin_user.py`):

```python
"""Pre-launch utility: reset every admin password to Admin123 (argon2)
and revoke all sessions. Do NOT run after launch."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Role, User, UserRole, UserSession

NEW_PASSWORD = "Admin123"


async def main() -> None:
    async with AsyncSessionLocal() as session:
        admins = (
            (
                await session.execute(
                    select(User)
                    .join(UserRole, UserRole.user_id == User.id)
                    .join(Role, Role.id == UserRole.role_id)
                    .where(Role.name == "admin")
                )
            )
            .scalars()
            .unique()
            .all()
        )
        for user in admins:
            user.password_hash = hash_password(NEW_PASSWORD)
        await session.execute(delete(UserSession))
        await session.commit()

    emails = ", ".join(user.email for user in admins) or "<none>"
    print(f"Reset {len(admins)} admin password(s) to {NEW_PASSWORD!r}: {emails}")
    print("All sessions revoked.")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Smoke-test against a throwaway SQLite DB**

```bash
cd apps/api && DATABASE_URL="sqlite+aiosqlite:///./reset-smoke.db" uv run python - <<'EOF'
import asyncio
from app.core.database import Base, engine, AsyncSessionLocal
from app.services.user_seed import seed_admin_user
from app import models  # noqa: F401

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session, email="smoke@example.com", password="old-password")

asyncio.run(main())
EOF
DATABASE_URL="sqlite+aiosqlite:///./reset-smoke.db" uv run python scripts/reset_admin_passwords.py
rm -f reset-smoke.db
```

Expected output: `Reset 1 admin password(s) to 'Admin123': smoke@example.com` then `All sessions revoked.`
(Note: `get_settings` is `lru_cache`d per process, so `DATABASE_URL` must be set as an env var when the process starts, as above.)

- [ ] **Step 3: Commit**

```bash
git add apps/api/scripts/reset_admin_passwords.py
git commit -m "feat(api): add pre-launch admin password reset script"
```

---

### Task 6: CMS — slide the browser cookie with the session

**Files:**
- Modify: `apps/cms/src/lib/server/session.ts`
- Modify: `apps/cms/src/hooks.server.ts`

- [ ] **Step 1: Add the max-age constant**

`apps/cms/src/lib/server/session.ts` becomes:

```typescript
import { dev } from '$app/environment';

export const sessionCookieName = 'cms_session';

// Keep in sync with the API's SESSION_TTL_SECONDS (default 14 days).
export const sessionCookieMaxAgeSeconds = 60 * 60 * 24 * 14;

export const sessionCookieOptions = {
  path: '/',
  httpOnly: true,
  sameSite: 'lax' as const,
  secure: !dev
};
```

- [ ] **Step 2: Re-set the cookie on each authenticated request**

In `apps/cms/src/hooks.server.ts`, update the import and the success path of the `try` block:

```typescript
import { sessionCookieMaxAgeSeconds, sessionCookieName, sessionCookieOptions } from '$lib/server/session';
```

```typescript
  if (token) {
    try {
      event.locals.user = await apiFetch<AuthUser>('/api/v1/auth/me', { token });
      // Slide the browser cookie along with the server-side session.
      event.cookies.set(sessionCookieName, token, {
        ...sessionCookieOptions,
        maxAge: sessionCookieMaxAgeSeconds
      });
    } catch (error) {
      // ... unchanged catch block ...
    }
  }
```

- [ ] **Step 3: Type-check the CMS**

Run: `pnpm --filter cms check` (if that filter name fails, run `cd apps/cms && pnpm check`)
Expected: 0 errors (warnings that already existed are acceptable).

- [ ] **Step 4: Commit**

```bash
git add apps/cms/src/lib/server/session.ts apps/cms/src/hooks.server.ts
git commit -m "feat(cms): slide session cookie max-age with server session"
```

---

### Task 7: Migrate the live DB, reset admins, end-to-end verification

**Files:** none created — this task applies the migration and verifies the whole stack.

- [ ] **Step 1: Apply the migration to the dev/live Postgres DB**

```bash
cd apps/api && uv run alembic upgrade head
```

Expected: `Running upgrade b2f1a7c9d3e4 -> d4e5f6a7b8c9, replace refresh_tokens with sessions`.

- [ ] **Step 2: Reset admin passwords**

```bash
cd apps/api && uv run python scripts/reset_admin_passwords.py
```

Expected: `Reset N admin password(s) to 'Admin123': <emails>` with N ≥ 1.

- [ ] **Step 3: Full API test suite**

Run: `cd apps/api && uv run pytest`
Expected: ALL PASS.

- [ ] **Step 4: End-to-end login through the running stack**

Start the stack with `./rundev.sh` (or the API alone: `cd apps/api && uv run uvicorn app.main:app --port 8003`), then:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8003/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "<seeded-admin-email>", "password": "Admin123"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
curl -s http://127.0.0.1:8003/api/v1/auth/me -H "Authorization: Bearer $TOKEN"   # expect user JSON
curl -s -X POST http://127.0.0.1:8003/api/v1/auth/logout -H "Authorization: Bearer $TOKEN"  # expect {"status":"ok"}
curl -s http://127.0.0.1:8003/api/v1/auth/me -H "Authorization: Bearer $TOKEN"   # expect invalid_token 401
```

Also log in through the CMS UI (port 5181) with the reset credentials and confirm the venues admin pages load.

- [ ] **Step 5: Final commit (if anything changed) and wrap-up**

```bash
git status   # confirm clean or commit leftovers from verification config
```

Then use superpowers:finishing-a-development-branch / requesting-code-review as appropriate.
