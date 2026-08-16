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
    branch_alert,
    build_replacements,
    default_template,
    notification_recipients,
    registration_confirmation,
    render_template,
)
from app.domains.events.models import Event, EventRegistration
from app.models import Venue


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

    # The date is prose, not ISO: this text goes to a guest, and 2026-09-07 reads
    # as machine output. Indonesian is the default when no locale is given.
    assert rendered == "Halo Rina, sampai jumpa di Book a Tour pada 7 September 2026 pukul 10:00."


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


def test_the_confirmation_names_the_venue_as_the_location() -> None:
    """A venue tour visits the venue. This read "Location: {branch_name}", which
    sent couples to the office instead of to the place they asked to see."""
    event = Event(name="Book a Tour", venue="a label on the event")
    registration = EventRegistration(
        guest_name="Rina Putri",
        email="rina@example.test",
        party_size=2,
        venue_name="Villa Uluwatu Cliffside",
    )

    _subject, body = registration_confirmation(
        event=event, registration=registration, branch=Branch(name="7Magic Jakarta")
    )

    assert "Venue: Villa Uluwatu Cliffside" in body
    assert "Location: 7Magic Jakarta" not in body


def test_the_event_label_is_only_a_fallback_for_the_venue() -> None:
    """event.venue is a label on the event itself, not where this guest is going.
    It stands in only when the registration names nothing."""
    event = Event(name="Open House", venue="7Magic Jakarta")
    registration = EventRegistration(guest_name="Budi", email="budi@example.test", party_size=1)

    replacements = build_replacements(
        event=event, registration=registration, branch_name="7Magic Jakarta"
    )

    assert replacements["venue"] == "7Magic Jakarta"


def test_the_branch_alert_names_the_venue_and_city() -> None:
    event = Event(name="Book a Tour")
    registration = EventRegistration(
        guest_name="Budi",
        email="budi@example.test",
        party_size=2,
        venue_name="Some Hall",
        city="bandung",
        source="public",
    )

    _subject, body = branch_alert(
        event=event, registration=registration, branch=Branch(name="7Magic Jakarta")
    )

    assert "Venue: Some Hall" in body
    assert "City: bandung" in body


# --- Guest language and the venue block ---------------------------------------
# The confirmation is the one email every guest gets, so it is the one that has
# to arrive in the language they booked in, with enough detail to find the venue.


def test_the_confirmation_defaults_to_indonesian() -> None:
    """Indonesian is canonical. A caller that says nothing about language gets
    it, which also covers any direct API caller that predates the parameter."""
    subject, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina Pratiwi",
            email="dina@example.test",
            visit_date=date(2026, 5, 17),
            party_size=2,
        ),
        branch=Branch(name="7Magic Jakarta"),
    )

    # The event name carries the noun, so the subject does not prefix "Booking" --
    # an event called "Book a Tour" rendered "Booking Book a Tour Anda".
    assert subject == "Venue Tour Anda sudah dikonfirmasi"
    assert "Halo Dina," in body
    assert "Jumlah tamu: 2" in body


def test_the_confirmation_renders_in_english_when_asked() -> None:
    subject, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina Pratiwi",
            email="dina@example.test",
            visit_date=date(2026, 5, 17),
            party_size=2,
        ),
        branch=Branch(name="7Magic Jakarta"),
        locale="en",
    )

    assert subject == "Your Venue Tour booking is confirmed"
    assert "Hi Dina," in body
    assert "Guests: 2" in body


def test_the_visit_date_is_written_in_the_guests_language() -> None:
    registration = EventRegistration(
        guest_name="Dina", email="dina@example.test", visit_date=date(2026, 5, 17), party_size=1
    )

    _s, indonesian = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=None, locale="id"
    )
    _s, english = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=None, locale="en"
    )

    assert "17 Mei 2026" in indonesian
    assert "17 May 2026" in english


def test_a_region_tagged_locale_is_accepted() -> None:
    """Browsers and Accept-Language send en-GB, not en."""
    _subject, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina", email="dina@example.test", visit_date=date(2026, 5, 17)
        ),
        branch=None,
        locale="en-GB",
    )

    assert "Hi Dina," in body


def test_an_unknown_locale_falls_back_rather_than_failing() -> None:
    """A booking must never fail over the language of its receipt."""
    _subject, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina", email="dina@example.test", visit_date=date(2026, 5, 17)
        ),
        branch=None,
        locale="klingon",
    )

    assert "Halo Dina," in body


def test_the_confirmation_carries_the_venue_address() -> None:
    """'Where do I go' is the most important line in a tour confirmation."""
    venue = Venue(
        name="The Ritz-Carlton Pacific Place",
        slug="ritz-carlton-pacific-place",
        address="Jl. Jend. Sudirman Kav. 52-53",
        district="Kebayoran Baru",
        city="jakarta",
    )
    registration = EventRegistration(
        guest_name="Dina", email="dina@example.test", visit_date=date(2026, 5, 17), party_size=2
    )
    registration.venue = venue

    _subject, body = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=None, locale="id"
    )

    assert "Venue: The Ritz-Carlton Pacific Place" in body
    # One line, one `Label: value` pair -- the HTML layout emphasises the value
    # after the colon, and a bare continuation line has no label to anchor to.
    # City is stored lowercased, so it needs casing back for prose.
    assert (
        "Alamat: Jl. Jend. Sudirman Kav. 52-53, Kebayoran Baru, Jakarta" in body
    )


def test_the_address_label_follows_the_locale() -> None:
    venue = Venue(
        name="Hotel Indonesia Kempinski",
        slug="hotel-indonesia-kempinski",
        address="Jl. M.H. Thamrin No. 1",
        district="Menteng",
        city="jakarta",
    )
    registration = EventRegistration(guest_name="Dina", email="dina@example.test")
    registration.venue = venue

    _s, body = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=None, locale="en"
    )

    assert "Address: Jl. M.H. Thamrin No. 1" in body


def test_a_venue_we_do_not_publish_degrades_to_its_name() -> None:
    """The guest typed a venue with no catalogue row, so there is no address to
    show -- the block must not render an empty 'Alamat:' line."""
    registration = EventRegistration(
        guest_name="Dina",
        email="dina@example.test",
        venue_name="Gedung Serbaguna Kelurahan",
        visit_date=date(2026, 5, 17),
    )

    _subject, body = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=None, locale="id"
    )

    assert "Venue: Gedung Serbaguna Kelurahan" in body
    assert "Alamat:" not in body


def test_the_confirmation_is_signed_by_the_branch() -> None:
    """A guest should hear from the branch that will actually follow up, not from
    the company in the abstract."""
    registration = EventRegistration(
        guest_name="Dina", email="dina@example.test", visit_date=date(2026, 5, 17)
    )
    branch = Branch(name="7Magic Jakarta")

    _s, indonesian = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=branch, locale="id"
    )
    _s, english = registration_confirmation(
        event=Event(name="Venue Tour"), registration=registration, branch=branch, locale="en"
    )

    assert indonesian.endswith("Tim 7Magic Jakarta")
    assert english.endswith("The 7Magic Jakarta team")


def test_an_unrouted_booking_is_signed_by_the_company() -> None:
    """No branch means no branch name, and "Tim " with a gap after it would look
    like a bug to the guest."""
    _s, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(guest_name="Dina", email="dina@example.test"),
        branch=None,
        locale="id",
    )

    assert body.endswith("Tim 7Magic")


def test_the_branch_alert_is_not_translated() -> None:
    """It goes to the team, not the couple, so it stays in one language whatever
    the guest chose."""
    registration = EventRegistration(
        guest_name="Dina", email="dina@example.test", party_size=2, source="public"
    )

    _subject, body = branch_alert(
        event=Event(name="Venue Tour"),
        registration=registration,
        branch=Branch(name="7Magic Jakarta"),
    )

    assert "Name: Dina" in body


# --- Values that are missing, or that try to forge a row ----------------------


def test_a_booking_with_no_date_renders_no_date_line() -> None:
    """visit_date is optional on the public payload and nothing server-side
    requires it, so a null one produced a bare "Tanggal:" with nothing after --
    the same defect 1b0089e removed for the Time line."""
    _s, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(guest_name="Dina", email="dina@example.test", party_size=2),
        branch=Branch(name="7Magic Jakarta"),
        locale="id",
    )

    assert "Tanggal:" not in body
    # The lines that are known still render.
    assert "Jumlah tamu: 2" in body


def test_a_newline_in_a_name_cannot_forge_a_row_in_the_confirmation() -> None:
    """Each detail renders as a Label: value row, so an unescaped newline adds a
    row that looks exactly like a real field."""
    _s, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina\nJumlah tamu: 99",
            email="dina@example.test",
            party_size=2,
            visit_date=date(2026, 5, 17),
        ),
        branch=Branch(name="7Magic Jakarta"),
        locale="id",
    )

    assert "Jumlah tamu: 99" not in body
    assert "Jumlah tamu: 2" in body


def test_a_newline_in_a_name_cannot_forge_a_row_in_the_branch_alert() -> None:
    """The alert is what the team acts on, so a forged Email row there is worse
    than a cosmetic problem."""
    _subject, body = branch_alert(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="John\nEmail: attacker@evil.test",
            email="real@example.test",
            party_size=1,
            source="public",
        ),
        branch=Branch(name="7Magic Jakarta"),
    )

    assert "attacker@evil.test" not in body.splitlines()[1]
    assert body.splitlines()[1] == "Email: real@example.test"


def test_a_venue_typed_with_newlines_is_collapsed() -> None:
    _s, body = registration_confirmation(
        event=Event(name="Venue Tour"),
        registration=EventRegistration(
            guest_name="Dina",
            email="dina@example.test",
            venue_name="Some Hall\nTanggal: 1 Januari 2000",
            visit_date=date(2026, 5, 17),
        ),
        branch=None,
        locale="id",
    )

    lines = body.splitlines()
    # Collapsed onto the venue's own line, so it is visibly part of that value
    # rather than a row of its own. What matters is that it cannot *become* a
    # row: the renderer styles one row per line, so a line is the unit of trust.
    assert not any(line.startswith("Tanggal: 1 Januari 2000") for line in lines)
    assert "Tanggal: 17 Mei 2026" in lines
