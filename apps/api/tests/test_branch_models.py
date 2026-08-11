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
    assert stored.settings.tour_notification_recipients == [
        "ops@7magic.test",
        "jakarta@7magic.test",
    ]
    assert stored.opening_hours[0].day_of_week == 1
    assert stored.closures[0].public_label == "Libur Natal"
