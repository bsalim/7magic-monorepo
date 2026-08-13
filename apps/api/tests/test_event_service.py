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
from app.models.venue import Venue

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


def _venue(**overrides) -> Venue:
    """`address` and `district` are the only venue columns without a default, so
    they are all a test row needs beyond what it is actually asserting on."""
    fields = {
        "name": "Hotel Mulia",
        "slug": "hotel-mulia",
        "address": "Jl. Asia Afrika",
        "district": "Senayan",
        "city": "jakarta",
        "status": "active",
    }
    fields.update(overrides)
    return Venue(**fields)


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
async def test_a_company_wide_event_is_found_for_any_branch(session) -> None:
    """branch_id NULL means "every branch". This was written as
    `branch_id IN (branch.id, NULL)`, and a NULL inside an IN list matches nothing
    in SQL, so company-wide events were silently invisible to every branch."""
    branch, _ = await _branch_with_event(session)
    session.add(
        Event(branch_id=None, name="Book a Tour", is_active=True)
    )
    await session.commit()

    other = Branch(slug="bali", name="7Magic Bali", timezone="Asia/Makassar")
    session.add(other)
    await session.commit()

    found = await event_service.open_tour_event(session, other, NOW)

    assert found is not None
    assert found.branch_id is None


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
async def test_a_branch_closure_does_not_block_a_venue_tour(session) -> None:
    """A venue tour happens at a venue, not at the branch office, so the branch's
    own closed dates are not a reason to refuse. Was the opposite rule until the
    tour became venue-based; the form now offers a plain calendar, and a booking it
    allows has to be one the API accepts."""
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

    registration = await event_service.register(
        session, event=event, branch=branch, payload=_registration(), now=NOW, source="public"
    )

    assert registration.status == "registered"


@pytest.mark.asyncio
async def test_a_day_the_branch_has_no_hours_for_is_still_accepted(session) -> None:
    branch, event = await _branch_with_event(session)

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(visit_date="2026-09-13"),  # a Sunday, day 7, no hours
        now=NOW,
        source="public",
    )

    assert registration.visit_date.isoformat() == "2026-09-13"


@pytest.mark.asyncio
async def test_the_chosen_venue_and_head_count_are_recorded(session) -> None:
    branch, event = await _branch_with_event(session)
    venue = Venue(
        name="Grand Ballroom",
        slug="grand-ballroom",
        city="jakarta",
        address="Jl. Test 1",
        district="Menteng",
    )
    session.add(venue)
    await session.flush()

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(venue_id=venue.id, party_size=4),
        now=NOW,
        source="public",
    )

    assert registration.venue_id == venue.id
    # The total the guest typed, not one-plus-named-companions.
    assert registration.party_size == 4


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


@pytest.mark.asyncio
async def test_register_keeps_a_typed_venue_name(session) -> None:
    """A venue we do not publish is still bookable, and the typed name is all the
    team gets."""
    branch, event = await _branch_with_event(session)

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(venue_name="Villa Uluwatu Cliffside", city="Bali"),
        now=NOW,
        source="public",
    )

    assert registration.venue_name == "Villa Uluwatu Cliffside"
    # Lowercased on write: it is matched against branch.city, which is a slug-ish
    # lowercase value on the row.
    assert registration.city == "bali"
    assert registration.venue_id is None


@pytest.mark.asyncio
async def test_register_links_a_typed_name_that_matches_a_catalogued_venue(session) -> None:
    """Typed by hand rather than picked from the suggestions, but it is one of ours
    -- so the FK is linked and the CMS can filter on it."""
    branch, event = await _branch_with_event(session)
    venue = _venue(name="The Ritz-Carlton Pacific Place", slug="ritz-carlton-pacific-place")
    session.add(venue)
    await session.commit()

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        # Different case, same venue.
        payload=_registration(venue_name="the ritz-carlton pacific place", city="jakarta"),
        now=NOW,
        source="public",
    )

    assert registration.venue_id == venue.id
    assert registration.venue_name == "the ritz-carlton pacific place"


@pytest.mark.asyncio
async def test_a_draft_venue_is_not_matched_by_name(session) -> None:
    """Only active venues are suggested, so only active venues earn the FK. Linking
    a draft row would surface it in the CMS as though it were published."""
    branch, event = await _branch_with_event(session)
    session.add(_venue(name="Secret Villa", slug="secret-villa", city="bali", status="draft"))
    await session.commit()

    registration = await event_service.register(
        session,
        event=event,
        branch=branch,
        payload=_registration(venue_name="Secret Villa", city="bali"),
        now=NOW,
        source="public",
    )

    assert registration.venue_id is None
    assert registration.venue_name == "Secret Villa"


@pytest.mark.asyncio
async def test_a_city_picks_the_branch_that_serves_it(session) -> None:
    jakarta, _ = await _branch_with_event(session)
    bali = Branch(slug="bali", name="7Magic Bali", city="bali", timezone="Asia/Makassar")
    session.add(bali)
    await session.flush()
    session.add(
        Event(
            branch_id=bali.id,
            name="Book a Tour Bali",
            registration_opens_at=NOW - timedelta(days=7),
            registration_closes_at=NOW + timedelta(days=7),
        )
    )
    await session.commit()

    branch, event = await event_service.resolve_tour_target(session, "bali", NOW)

    assert branch is not None
    assert branch.slug == "bali"
    assert event is not None
    assert event.branch_id == bali.id


@pytest.mark.asyncio
async def test_a_city_with_no_branch_still_lands_on_an_event(session) -> None:
    """Most cities have no branch of their own today. The booking still has to go
    somewhere, and the branch it names is who gets the alert -- a company-wide event
    has branch_id NULL, and notification_recipients(None) is empty."""
    jakarta, _ = await _branch_with_event(session)

    branch, event = await event_service.resolve_tour_target(session, "bandung", NOW)

    assert event is not None
    assert branch is not None
    assert branch.id == jakarta.id


@pytest.mark.asyncio
async def test_the_default_branch_takes_a_city_nobody_serves(session) -> None:
    """Not merely the lowest id: whoever the CMS marked as the default is who the
    org-wide leads belong to."""
    await _branch_with_event(session)
    bali = Branch(
        slug="bali", name="7Magic Bali", city="bali", timezone="Asia/Makassar", is_default=True
    )
    session.add(bali)
    await session.flush()
    session.add(
        Event(
            branch_id=None,
            name="Company-wide open house",
            registration_opens_at=NOW - timedelta(days=7),
            registration_closes_at=NOW + timedelta(days=7),
        )
    )
    await session.commit()

    branch, event = await event_service.resolve_tour_target(session, "bandung", NOW)

    assert branch is not None
    assert branch.slug == "bali"
    assert event is not None


@pytest.mark.asyncio
async def test_no_open_event_anywhere_resolves_to_no_event(session) -> None:
    branch = Branch(slug="jakarta", name="7Magic Jakarta", timezone="Asia/Jakarta")
    session.add(branch)
    await session.commit()

    resolved, event = await event_service.resolve_tour_target(session, "jakarta", NOW)

    assert event is None
    assert resolved is not None


@pytest.mark.asyncio
async def test_an_unbookable_branch_never_takes_a_lead(session) -> None:
    jakarta, _ = await _branch_with_event(session)
    jakarta.bookable = False
    await session.commit()

    branch, event = await event_service.resolve_tour_target(session, "jakarta", NOW)

    assert branch is None
    assert event is None
