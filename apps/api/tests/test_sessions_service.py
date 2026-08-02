from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
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


def test_resolve_session_rejects_session_past_max_lifetime(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            record = (await db.execute(select(UserSession))).scalar_one()
            record.created_at = datetime.now(UTC) - timedelta(days=31)
            record.expires_at = datetime.now(UTC) + timedelta(days=7)
            await db.commit()

            resolved = await resolve_session(
                db,
                token=token,
                ttl_seconds=TTL_SECONDS,
                max_lifetime_seconds=60 * 60 * 24 * 30,
            )

            assert resolved is None
            remaining = (await db.execute(select(UserSession))).scalars().all()
            assert remaining == []

    asyncio.run(scenario())


def test_sliding_expiry_never_extends_past_max_lifetime(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)
            record = (await db.execute(select(UserSession))).scalar_one()
            created_at = datetime.now(UTC) - timedelta(days=29)
            record.created_at = created_at
            record.last_seen_at = datetime.now(UTC) - timedelta(
                seconds=SESSION_REFRESH_INTERVAL_SECONDS + 60
            )
            await db.commit()

            resolved = await resolve_session(
                db,
                token=token,
                ttl_seconds=TTL_SECONDS,
                max_lifetime_seconds=60 * 60 * 24 * 30,
            )

            assert resolved is not None
            hard_deadline = created_at + timedelta(days=30)
            assert resolved.expires_at.replace(tzinfo=UTC) <= hard_deadline

    asyncio.run(scenario())


def test_revoke_session_deletes_row_and_is_idempotent(db_factory) -> None:
    async def scenario() -> None:
        async with db_factory() as db:
            token = await create_session(db, user_id=1, ttl_seconds=TTL_SECONDS)

            await revoke_session(db, token=token)
            assert await resolve_session(db, token=token, ttl_seconds=TTL_SECONDS) is None

            await revoke_session(db, token=token)

    asyncio.run(scenario())
