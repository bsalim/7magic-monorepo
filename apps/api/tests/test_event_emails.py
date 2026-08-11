from __future__ import annotations

from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy import select
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
        guest_name="Rina Kartika",
        email="rina@example.test",
        visit_date=date(2026, 9, 7),
        visit_slot="10:00",
        party_size=2,
    )

    rendered = render_template(
        "Halo {first_name}, sampai jumpa di {event_name} pada {visit_date} pukul {visit_slot}.",
        build_replacements(event=event, registration=registration, branch_name="7Magic Jakarta"),
    )

    assert rendered == "Halo Rina, sampai jumpa di Book a Tour pada 2026-09-07 pukul 10:00."


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
    session.add(Branch(slug="bali", name="7Magic Bali", timezone="Asia/Makassar"))
    await session.commit()

    # Fetched rather than reused: notification_recipients reads branch.settings,
    # and only a queried branch has it loaded by selectin -- which is how every
    # real caller gets one.
    branch = await session.scalar(select(Branch).where(Branch.slug == "bali"))

    assert notification_recipients(branch) == []
