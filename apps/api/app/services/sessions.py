from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_session_token, hash_session_token
from app.models import UserSession

# Sliding-window extension is throttled to at most one DB write per session
# per this interval.
SESSION_REFRESH_INTERVAL_SECONDS = 3600

# Default hard cap on total session age regardless of activity; mirrors the
# session_max_lifetime_seconds setting.
SESSION_MAX_LIFETIME_SECONDS = 60 * 60 * 24 * 30


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


async def resolve_session(
    db: AsyncSession,
    *,
    token: str,
    ttl_seconds: int,
    max_lifetime_seconds: int = SESSION_MAX_LIFETIME_SECONDS,
) -> UserSession | None:
    result = await db.execute(
        select(UserSession).where(UserSession.token_hash == hash_session_token(token))
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None

    now = datetime.now(UTC)
    hard_deadline = _as_utc(record.created_at) + timedelta(seconds=max_lifetime_seconds)
    if _as_utc(record.expires_at) < now or hard_deadline < now:
        await db.delete(record)
        await db.commit()
        return None

    if (now - _as_utc(record.last_seen_at)).total_seconds() >= SESSION_REFRESH_INTERVAL_SECONDS:
        record.last_seen_at = now
        record.expires_at = min(now + timedelta(seconds=ttl_seconds), hard_deadline)
        await db.commit()

    return record


async def revoke_session(db: AsyncSession, *, token: str) -> None:
    await db.execute(delete(UserSession).where(UserSession.token_hash == hash_session_token(token)))
    await db.commit()


async def revoke_other_sessions(db: AsyncSession, *, user_id: int, keep_token: str) -> int:
    result = await db.execute(
        delete(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.token_hash != hash_session_token(keep_token),
        )
    )
    await db.commit()
    return result.rowcount or 0


def _as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes even for timezone-aware columns.
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
