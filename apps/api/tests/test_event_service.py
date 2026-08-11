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
            BranchOpeningHour(
                day_of_week=day, opens_at_local=time(10, 0), closes_at_local=time(18, 0)
            )
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
        "visit_date": "2026-09-07",  # a Monday
        "visit_slot": "10:00",
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
    branch, event = await _branch_with_event(
        session, registration_closes_at=NOW - timedelta(days=1)
    )

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
    # Added through the session rather than branch.closures: the collection was
    # never loaded, and appending to it would lazy-load under asyncio.
    session.add(
        BranchClosure(
            branch_id=branch.id,
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
            payload=_registration(visit_date="2026-09-13"),  # a Sunday, day 7, no hours
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
