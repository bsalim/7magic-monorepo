"""Contact and venue-pricing leads.

Both the /contact form and the venue "See venue pricing" modal land here. Leads
are written to the `contact_leads` table first, then the 7Magic inbox is
notified -- in that order, so a provider outage costs a notification, never the
lead itself. The previous implementation appended to an in-memory list, so every
submission was lost when the API restarted.

Two notifications go out per lead, over separate providers: an email through
Resend and a WhatsApp alert through Bird. Both are best-effort and neither can
fail the request, so an outage at one still leaves the other and the row itself.

The wedding tools' lead gate writes here too, as `tool_<tool>` rows, and the CMS
leads page reads every source back through `list_leads` / `export_leads`.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import ContactLead, Venue
from app.schemas.content import (
    AdminLead,
    AdminLeadListResponse,
    ContactLeadCreate,
    ContactLeadResponse,
    Pagination,
    ToolLeadCreate,
    VenuePricingRequest,
)
from app.services.email import EmailNotifier
from app.services.whatsapp import WhatsAppNotifier, join_contact

logger = logging.getLogger(__name__)

# How the inbox and the WhatsApp alert name each tool's leads.
TOOL_LABELS = {"mahar": "Mahar", "hashtag": "Hashtag"}

LEADS_PAGE_SIZE = 50

# The team works in Jakarta, so a date filter means a Jakarta day: a lead that
# arrived at 01:00 WIB belongs to that date, not to the previous UTC one.
LEAD_TIMEZONE = ZoneInfo("Asia/Jakarta")


def _lead_label(message: str | None) -> str | None:
    """`Paket Sangjit` from a message whose first line is `LEAD: Paket Sangjit`."""
    first_line = (message or "").strip().splitlines()[0:1]
    if first_line and first_line[0].upper().startswith("LEAD:"):
        return first_line[0][5:].strip()[:80] or None
    return None


class LeadService:
    def __init__(self) -> None:
        self._notifier = EmailNotifier(get_settings())
        self._whatsapp = WhatsAppNotifier(get_settings())

    async def create_contact_lead(
        self, session: AsyncSession, payload: ContactLeadCreate
    ) -> ContactLeadResponse:
        venue_id = await self._venue_id_for_slug(session, payload.venue_slug)

        lead = ContactLead(
            full_name=payload.name,
            email=payload.email,
            mobile=payload.phone,
            message=payload.message,
            source="contact_form",
            venue_id=venue_id,
            metadata_json={
                "source_path": payload.source_path,
                "venue_slug": payload.venue_slug,
            },
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)

        # Landing-page forms open their message with "LEAD: <what>". Surfacing it
        # lets the inbox tell a sangjit quote request from a general question
        # without opening the mail.
        label = _lead_label(payload.message)
        await self._notifier.send_lead_notification(
            subject=(
                f"{label}: request from {payload.name}"
                if label
                else f"New website enquiry from {payload.name}"
            ),
            heading=f"{label} request" if label else "New contact enquiry",
            fields={
                "Name": payload.name,
                "Email": payload.email,
                "Phone": payload.phone,
                "Venue": payload.venue_slug,
                "Page": payload.source_path,
                "Message": payload.message,
            },
            reply_to=payload.email,
        )
        await self._whatsapp.send_lead_alert(
            name=payload.name,
            contact=join_contact(payload.phone, payload.email),
            page=payload.venue_slug or payload.source_path,
            message=payload.message,
        )

        return self._response(lead)

    async def create_venue_pricing_request(
        self, session: AsyncSession, payload: VenuePricingRequest
    ) -> ContactLeadResponse:
        """A couple asking for pricing on a specific venue. Prices are not shown
        publicly, so this is the only way they can get them."""
        venue = None
        if payload.venue_id is not None:
            venue = await session.get(Venue, payload.venue_id)
        if venue is None and payload.venue_slug:
            # Fall back to the slug so the lead still links to the venue when
            # the client only knows the URL it came from.
            venue = await session.scalar(
                select(Venue).where(Venue.slug == payload.venue_slug)
            )

        lead = ContactLead(
            full_name=payload.name,
            email=payload.email,
            mobile=payload.whatsapp,
            message=f"Venue pricing request for {venue.name if venue else 'a venue'}.",
            source="venue_pricing",
            venue_id=venue.id if venue else None,
            metadata_json={
                "wedding_date": payload.wedding_date,
                "best_time_to_reach": payload.best_time_to_reach,
                "venue_name": venue.name if venue else payload.venue_name,
                "venue_slug": payload.venue_slug,
            },
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)

        venue_label = venue.name if venue else (payload.venue_name or "a venue")
        await self._notifier.send_lead_notification(
            subject=f"Venue pricing request — {venue_label}",
            heading="Venue pricing request",
            fields={
                "Venue": venue_label,
                "Name": payload.name,
                "WhatsApp": payload.whatsapp,
                "Email": payload.email,
                "Wedding date": payload.wedding_date,
                "Best time to reach": payload.best_time_to_reach,
            },
            reply_to=payload.email,
        )
        # The venue is the lead here, so it takes the page slot; the two timing
        # fields are what the team needs to act on, so they become the message.
        await self._whatsapp.send_lead_alert(
            name=payload.name,
            contact=join_contact(payload.whatsapp, payload.email),
            page=venue_label,
            message=join_contact(
                f"Tanggal nikah: {payload.wedding_date}" if payload.wedding_date else "",
                f"Waktu dihubungi: {payload.best_time_to_reach}"
                if payload.best_time_to_reach
                else "",
            ),
        )

        return self._response(lead)

    async def create_tool_lead(self, session: AsyncSession, payload: ToolLeadCreate) -> None:
        """The lead gate on a wedding tool. A filled honeypot stores and sends
        nothing; the caller still answers success so a bot learns nothing."""
        if payload.website:
            return

        label = f"Wedding tool: {TOOL_LABELS.get(payload.tool, payload.tool)}"
        lead = ContactLead(
            full_name=payload.names,
            email=payload.email,
            mobile=payload.phone,
            source=f"tool_{payload.tool}",
            metadata_json={
                "source_path": payload.source_path,
                "tool": payload.tool,
                "inputs": payload.inputs,
                "consent_at": datetime.now(UTC).isoformat(),
            },
        )
        session.add(lead)
        await session.commit()

        who = payload.names or payload.email
        inputs = _inputs_line(payload.inputs)
        # Wrapped, unlike the contact paths: the row is already saved, and an error
        # here would withhold the card the visitor just paid for with their
        # details -- they would leave rather than retry.
        try:
            await self._notifier.send_lead_notification(
                subject=f"{label}: lead from {who}",
                heading=label,
                fields={
                    "Name": payload.names,
                    "Email": payload.email,
                    "WhatsApp": payload.phone,
                    "Page": payload.source_path,
                    "Inputs": inputs,
                },
                reply_to=payload.email,
            )
        except Exception:  # noqa: BLE001 -- logged, never re-raised
            logger.exception("tool lead email failed for lead %s", lead.id)
        try:
            await self._whatsapp.send_lead_alert(
                name=who,
                contact=join_contact(payload.phone, payload.email),
                page=label,
                message=inputs,
            )
        except Exception:  # noqa: BLE001 -- logged, never re-raised
            logger.exception("tool lead whatsapp alert failed for lead %s", lead.id)

    async def list_leads(
        self,
        session: AsyncSession,
        *,
        source: str | None = None,
        query: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = LEADS_PAGE_SIZE,
    ) -> AdminLeadListResponse:
        statement = _filtered_leads(source, query, date_from, date_to)
        total = await session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        rows = await session.scalars(
            statement.order_by(ContactLead.created_at.desc(), ContactLead.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return AdminLeadListResponse(
            items=[_admin_lead(row) for row in rows],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=(total + page_size - 1) // page_size if total else 0,
            ),
        )

    async def export_leads(
        self,
        session: AsyncSession,
        *,
        source: str | None = None,
        query: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AdminLead]:
        """Every lead matching the filters, unpaged, newest first."""
        rows = await session.scalars(
            _filtered_leads(source, query, date_from, date_to).order_by(
                ContactLead.created_at.desc(), ContactLead.id.desc()
            )
        )
        return [_admin_lead(row) for row in rows]

    async def count(self, session: AsyncSession) -> int:
        return await session.scalar(select(func.count()).select_from(ContactLead)) or 0

    async def _venue_id_for_slug(
        self, session: AsyncSession, slug: str | None
    ) -> int | None:
        if not slug:
            return None
        return await session.scalar(select(Venue.id).where(Venue.slug == slug))

    def _response(self, lead: ContactLead) -> ContactLeadResponse:
        return ContactLeadResponse(
            id=lead.id,
            status="received",
            message="Lead received.",
            created_at=lead.created_at.isoformat() if lead.created_at else "",
        )


def _inputs_line(inputs: dict) -> str:
    """`method: akad / variant: dmy / amount: 20092026` -- one line, so it fits the
    single message slot of the WhatsApp template."""
    return join_contact(*(f"{key}: {value}" for key, value in inputs.items() if value is not None))


def _jakarta_day_start(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=LEAD_TIMEZONE).astimezone(UTC)


def _filtered_leads(
    source: str | None, query: str | None, date_from: date | None, date_to: date | None
) -> Select[tuple[ContactLead]]:
    statement = select(ContactLead)
    if source:
        statement = statement.where(ContactLead.source == source)
    if query and query.strip():
        pattern = f"%{query.strip().lower()}%"
        statement = statement.where(
            func.lower(ContactLead.full_name).like(pattern)
            | func.lower(ContactLead.email).like(pattern)
            | func.lower(ContactLead.mobile).like(pattern)
            | func.lower(ContactLead.message).like(pattern)
        )
    if date_from:
        statement = statement.where(ContactLead.created_at >= _jakarta_day_start(date_from))
    if date_to:
        # Half-open on the next day's start, so the whole of `date_to` is included
        # whatever the time precision of the column.
        statement = statement.where(
            ContactLead.created_at < _jakarta_day_start(date_to + timedelta(days=1))
        )
    return statement


def _admin_lead(lead: ContactLead) -> AdminLead:
    metadata = lead.metadata_json or {}
    created_at = lead.created_at
    if created_at is not None:
        # SQLite hands timestamps back naive; they were written as UTC.
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        created_at = created_at.astimezone(LEAD_TIMEZONE)
    return AdminLead(
        id=lead.id,
        created_at=created_at.isoformat() if created_at else None,
        source=lead.source,
        full_name=lead.full_name,
        email=lead.email,
        mobile=lead.mobile,
        message=lead.message,
        source_path=metadata.get("source_path"),
        venue_id=lead.venue_id,
        metadata=metadata,
    )


lead_service = LeadService()
