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

    await branch_service.update(
        session, second.id, BranchUpdate.model_validate({"isDefault": True})
    )

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
