"""Contact and venue-pricing leads.

Both the /contact form and the venue "See venue pricing" modal land here. Leads
are written to the `contact_leads` table first, then the 7Magic inbox is
notified -- in that order, so a provider outage costs a notification, never the
lead itself. The previous implementation appended to an in-memory list, so every
submission was lost when the API restarted.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import ContactLead, Venue
from app.schemas.content import (
    ContactLeadCreate,
    ContactLeadResponse,
    VenuePricingRequest,
)
from app.services.email import EmailNotifier


class LeadService:
    def __init__(self) -> None:
        self._notifier = EmailNotifier(get_settings())

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

        await self._notifier.send_lead_notification(
            subject=f"New website enquiry from {payload.name}",
            heading="New contact enquiry",
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

        return self._response(lead)

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


lead_service = LeadService()
