from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.html import sanitize_html
from app.domains.branches.models import Branch
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


def branch_accepts_date(branch: Branch, visit_date: date) -> bool:
    """A date works if the branch has active opening hours for that ISO weekday and
    no active closure covers it."""
    iso_day = visit_date.isoweekday()
    if not any(row.day_of_week == iso_day and row.active for row in branch.opening_hours):
        return False
    for closure in branch.closures:
        if not closure.active:
            continue
        if closure.starts_at_local.date() <= visit_date <= closure.ends_at_local.date():
            return False
    return True


async def _ensure_schedule_loaded(session: AsyncSession, branch: Branch) -> None:
    """`branch_accepts_date` walks opening_hours and closures synchronously, so both
    must already be in memory. A branch fetched through branch_service has them via
    selectin; one built in-session may not, and touching an unloaded collection
    under asyncio raises MissingGreenlet instead of quietly emitting a SELECT."""
    unloaded = inspect(branch).unloaded
    missing = [name for name in ("opening_hours", "closures") if name in unloaded]
    if missing:
        await session.refresh(branch, missing)


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
                Event.branch_id.in_([branch.id, None]),
            )
            .order_by(Event.event_start_at.is_(None), Event.event_start_at)
        )
        for event in candidates:
            if registration_block(event, now) is None:
                return event
        return None

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

        if payload.visit_date is not None and branch is not None:
            await _ensure_schedule_loaded(session, branch)
            if not branch_accepts_date(branch, payload.visit_date):
                raise RegistrationBlocked(
                    "branch_closed", "This branch is closed on the date you chose."
                )

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

        heads = 1 + len(payload.guests)
        if event.capacity is not None:
            taken = await self.head_count(session, event.id)
            if taken + heads > event.capacity:
                raise RegistrationBlocked("event_full", "This event is fully booked.")

        registration = EventRegistration(
            event_id=event.id,
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
