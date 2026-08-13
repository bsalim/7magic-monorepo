from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.html import sanitize_html
from app.domains.branches.models import Branch
from app.domains.branches.service import branch_service
from app.domains.events.models import (
    REGISTRATION_STATUSES,
    Event,
    EventRegistration,
    EventRegistrationGuest,
)
from app.domains.events.schemas import (
    EventCreate,
    EventUpdate,
    PublicRegistration,
    RegistrationUpdate,
)
from app.models.venue import Venue

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

    async def open_tour_event(
        self, session: AsyncSession, branch: Branch, now: datetime
    ) -> Event | None:
        """The event a visitor to this branch's tour page should see: an active
        event for this branch (or a company-wide one) that is currently open,
        soonest first."""
        candidates = await session.scalars(
            select(Event)
            .where(
                Event.deleted_at.is_(None),
                Event.is_active.is_(True),
                # or_ with IS NULL, not `in_([branch.id, None])`: in SQL a NULL
                # inside an IN list matches nothing, so the company-wide events
                # this is meant to include were silently never found.
                or_(Event.branch_id == branch.id, Event.branch_id.is_(None)),
            )
            .order_by(Event.event_start_at.is_(None), Event.event_start_at)
        )
        for event in candidates:
            if registration_block(event, now) is None:
                return event
        return None

    async def open_tour_scope(
        self, session: AsyncSession, now: datetime
    ) -> tuple[bool, set[int]]:
        """Which branches have a tour event open, as
        `(any_branch, branch_ids_with_their_own)`.

        One query for every branch, rather than open_tour_event per branch: the
        public branch list needs this for all of them at once, and a branch with no
        open event has to be left off it -- being active and bookable is not enough
        to accept a registration, and advertising one anyway sends guests to a page
        that only says "not taking bookings right now".
        """
        candidates = await session.scalars(
            select(Event).where(Event.deleted_at.is_(None), Event.is_active.is_(True))
        )
        any_branch = False
        branch_ids: set[int] = set()
        for event in candidates:
            if registration_block(event, now) is not None:
                continue
            if event.branch_id is None:
                any_branch = True
            else:
                branch_ids.add(event.branch_id)
        return any_branch, branch_ids

    async def resolve_tour_target(
        self, session: AsyncSession, city: str | None, now: datetime
    ) -> tuple[Branch | None, Event | None]:
        """Which branch and event a booking with no branch in the URL belongs to.

        Returns `(notify_branch, event)`. The two are resolved separately on
        purpose: a company-wide event has `branch_id IS NULL`, and
        `notification_recipients(None)` is empty, so pairing that event with no
        branch would accept the lead and tell nobody about it.

        Branches come from branch_service, which selectin-loads opening_hours,
        closures and settings. A branch reaching notification_recipients any other
        way raises MissingGreenlet instead of emitting a SELECT.
        """
        branches = [
            branch
            for branch in await branch_service.list(session, active_only=True)
            if branch.bookable
        ]
        branches.sort(key=lambda branch: branch.id)

        wanted = (city or "").strip().lower()
        for branch in branches:
            if branch.city.strip().lower() == wanted:
                event = await self.open_tour_event(session, branch, now)
                if event is not None:
                    return branch, event

        # Nobody serves that city, so fall back to whichever branch the CMS marked
        # as the default and let its inbox take the lead.
        fallback = next(
            (branch for branch in branches if branch.is_default),
            branches[0] if branches else None,
        )
        if fallback is not None:
            event = await self.open_tour_event(session, fallback, now)
            if event is not None:
                return fallback, event
        return fallback, None

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

        # The visit date is deliberately not checked against the branch's opening
        # hours or closed dates. A venue tour is arranged at a venue rather than at
        # the branch office, so any future date is a legitimate request and the team
        # confirms a time when they follow up. The hours remain in the CMS as the
        # team's own schedule; they no longer gate a booking, which is why the form
        # offers a plain calendar with no slots.
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

        # An explicit party_size wins: the public form asks for a total head count
        # rather than each companion's name. Falling back to the named guests keeps
        # the CMS front-desk path, which does collect names, counting correctly.
        heads = payload.party_size or 1 + len(payload.guests)
        if event.capacity is not None:
            taken = await self.head_count(session, event.id)
            if taken + heads > event.capacity:
                raise RegistrationBlocked("event_full", "This event is fully booked.")

        # A name typed by hand that happens to be one of ours still earns the FK:
        # the couple should not lose the catalogue link for not using the
        # suggestions. Active only, because that is all the form ever suggests.
        venue_id = payload.venue_id
        typed_name = (payload.venue_name or "").strip()
        if venue_id is None and typed_name:
            venue_id = await session.scalar(
                select(Venue.id).where(
                    func.lower(Venue.name) == typed_name.lower(), Venue.status == "active"
                )
            )

        registration = EventRegistration(
            event_id=event.id,
            venue_id=venue_id,
            venue_name=typed_name or None,
            # Lowercased on write: it is compared against branch.city, which is a
            # slug-ish lowercase value on the row.
            city=(payload.city or "").strip().lower() or None,
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

    async def get_registration(
        self, session: AsyncSession, registration_id: int
    ) -> EventRegistration:
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
