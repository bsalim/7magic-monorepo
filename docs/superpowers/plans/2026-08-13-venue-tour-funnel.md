# Venue Tour Funnel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the branch-picker funnel at `/tour` with a single venue-tour booking form reachable three ways — venue preselected, free-text venue + city, or branch-scoped by slug.

**Architecture:** The API gains a generic (branch-less) pair of public tour endpoints alongside the existing branch-scoped pair; `event_service` grows city-to-branch resolution so a lead with no branch in the URL still lands on a real event and a real notification inbox. `event_registrations` gains two nullable columns (`venue_name`, `city`) so a venue outside the published catalogue can still be booked. The web app collapses its two tour pages onto one shared `TourForm.svelte`.

**Tech Stack:** FastAPI + SQLAlchemy 2.0 async + Alembic (Python 3.12, `uv`), SvelteKit 5 runes + Tailwind + Paraglide i18n, pytest and vitest.

**Spec:** `docs/superpowers/specs/2026-08-13-venue-tour-funnel-design.md`

---

## File Structure

**API — `apps/api/`**

| File | Responsibility |
|---|---|
| `app/domains/events/models.py` | Modify: two columns on `EventRegistration`. |
| `migrations/versions/<new>_tour_registration_venue_name_and_city.py` | Create: the migration for those columns. |
| `app/domains/events/schemas.py` | Modify: `venue_name` + `city` on `PublicRegistration`; `city` on `RegistrationResponse`. |
| `app/domains/events/service.py` | Modify: city→branch/event resolution; persist and match the new fields in `register`. |
| `app/domains/events/emails.py` | Modify: the venue becomes the location in guest mail; the branch alert names it. |
| `app/api/v1/public/tour.py` | Modify: two new branch-less routes; the new fields on the branch-scoped register. |
| `app/api/v1/admin/event_registrations.py` | Modify: `venue_name` coalesce in the detail payload and the CSV. |
| `tests/test_event_service.py`, `tests/test_public_tour_api.py`, `tests/test_event_emails.py`, `tests/test_model_metadata.py` | Modify: the tests for all of the above. |

**Web — `apps/web/`**

| File | Responsibility |
|---|---|
| `src/lib/components/TourForm.svelte` | Create: the whole booking form. The only place the fields exist. |
| `src/lib/components/TourPitch.svelte` | Create: the sales copy block, so both entry points render it identically. |
| `src/routes/tour/+page.server.ts` / `+page.svelte` | Modify: generic entry point; branch grid deleted. |
| `src/routes/tour/[slug]/+page.server.ts` / `+page.svelte` | Modify: branch-scoped entry point, now rendering `TourForm`. |
| `src/lib/components/PublicHeader.svelte` | Modify: one nav entry. |
| `messages/{id,en}.json` | Modify: nav label, seven copy strings, two field labels. |

**CMS — `apps/cms/`**

| File | Responsibility |
|---|---|
| `src/routes/events/[id]/+page.svelte` | Modify: a Venue column on the registrations table. |

---

## Task 1: Registration columns and migration

**Files:**
- Modify: `apps/api/app/domains/events/models.py:74-82`
- Create: `apps/api/migrations/versions/<generated>_tour_registration_venue_name_and_city.py`
- Test: `apps/api/tests/test_model_metadata.py`

- [ ] **Step 1: Write the failing test**

Append to `apps/api/tests/test_model_metadata.py`:

```python
def test_event_registration_records_an_uncatalogued_venue() -> None:
    """The network is wider than the published venue table, so a tour can be booked
    at a venue with no row here. The typed name and the city are what the team gets
    in that case, and the city is also what routes the lead to a branch."""
    from app.domains.events.models import EventRegistration

    columns = EventRegistration.__table__.columns

    assert columns["venue_name"].nullable is True
    assert columns["venue_name"].type.length == 300
    assert columns["city"].nullable is True
    assert columns["city"].type.length == 80
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd apps/api && uv run pytest tests/test_model_metadata.py::test_event_registration_records_an_uncatalogued_venue -v
```

Expected: FAIL with `KeyError: 'venue_name'`.

- [ ] **Step 3: Add the columns**

In `apps/api/app/domains/events/models.py`, directly after the `venue_id` column (line 74-76), add:

```python
    # The venue as the guest typed it. Kept when it is not one of ours: the tour
    # network is wider than the published catalogue, so a booking must not require
    # a venues row. `venue_id` still wins when both are set.
    venue_name: Mapped[str | None] = mapped_column(String(300))
    # Where the tour happens. Stored alongside venue_id rather than derived from it,
    # because it is what routes a branch-less booking to a branch and it has to
    # survive the venue later being retired (venue_id is ON DELETE SET NULL).
    city: Mapped[str | None] = mapped_column(String(80))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd apps/api && uv run pytest tests/test_model_metadata.py::test_event_registration_records_an_uncatalogued_venue -v
```

Expected: PASS.

- [ ] **Step 5: Generate the migration**

```bash
cd apps/api && uv run alembic revision -m "tour registration venue name and city"
```

This prints the new file path. Open it and replace the generated body so it reads exactly:

```python
"""tour registration venue name and city

Revision ID: <keep the generated id>
Revises: 3c88ae63f480
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "<keep the generated id>"
down_revision = "3c88ae63f480"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Both nullable, so no backfill: every existing registration came through the
    # branch-scoped form, which always had a venues row to point at.
    op.add_column("event_registrations", sa.Column("venue_name", sa.String(length=300)))
    op.add_column("event_registrations", sa.Column("city", sa.String(length=80)))


def downgrade() -> None:
    op.drop_column("event_registrations", "city")
    op.drop_column("event_registrations", "venue_name")
```

- [ ] **Step 6: Apply and verify the migration**

```bash
cd apps/api && uv run alembic upgrade head && uv run alembic current
```

Expected: `alembic current` prints the new revision id followed by `(head)`.

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/domains/events/models.py apps/api/migrations/versions apps/api/tests/test_model_metadata.py
git commit -m "feat(api): record the typed venue and city on a tour registration"
```

---

## Task 2: Accept and persist the new fields

**Files:**
- Modify: `apps/api/app/domains/events/schemas.py:71-83`, `:95-109`
- Modify: `apps/api/app/domains/events/service.py:241-251`
- Test: `apps/api/tests/test_event_service.py`

- [ ] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_event_service.py`:

```python
def test_register_keeps_a_typed_venue_name(api) -> None:
    """A venue we do not publish is still bookable, and the typed name is all the
    team gets."""
    branch = _branch(api)
    event = _open_event(api, branch["id"])

    response = api.client.post(
        f"/api/v1/public/tour/branches/{branch['slug']}/register",
        json={
            "name": "Rina",
            "email": "rina@example.com",
            "venue_name": "Villa Uluwatu Cliffside",
            "city": "bali",
            "visit_date": _next_weekday(),
            "party_size": 2,
        },
    )

    assert response.status_code == 201
    row = _registration_row(api, event["id"])
    assert row.venue_name == "Villa Uluwatu Cliffside"
    assert row.city == "bali"
    assert row.venue_id is None


def test_register_links_a_typed_name_that_matches_a_catalogued_venue(api) -> None:
    """Typed by hand rather than picked from the suggestions, but it is one of ours
    -- so the FK is linked and the CMS can filter on it."""
    branch = _branch(api)
    _open_event(api, branch["id"])
    venue_id = _venue(api, name="The Ritz-Carlton Pacific Place", city="jakarta")

    api.client.post(
        f"/api/v1/public/tour/branches/{branch['slug']}/register",
        json={
            "name": "Budi",
            "email": "budi@example.com",
            # Different case, same venue.
            "venue_name": "the ritz-carlton pacific place",
            "city": "jakarta",
            "visit_date": _next_weekday(),
        },
    )

    row = _registration_row(api, _open_event_id(api))
    assert row.venue_id == venue_id
    assert row.venue_name == "the ritz-carlton pacific place"
```

Add these helpers near the top of the same file, below the existing imports:

```python
def _venue(api, *, name: str, city: str) -> int:
    """An active venue row, created straight through the session: the venue admin
    API is not what these tests are exercising."""
    from app.models.venue import Venue

    holder: dict[str, int] = {}

    async def seed(session) -> None:
        venue = Venue(name=name, slug=name.lower().replace(" ", "-"), city=city, status="active")
        session.add(venue)
        await session.flush()
        holder["id"] = venue.id

    api.seed(seed)
    return holder["id"]


def _registration_row(api, event_id: int):
    """The single registration on an event, reloaded so the new columns are read
    from the database rather than from the response body."""
    from sqlalchemy import select

    from app.domains.events.models import EventRegistration

    holder: dict[str, object] = {}

    async def load(session) -> None:
        holder["row"] = await session.scalar(
            select(EventRegistration).where(EventRegistration.event_id == event_id)
        )

    api.seed(load)
    return holder["row"]


def _open_event_id(api) -> int:
    return api.client.get("/api/v1/admin/events").json()["items"][0]["id"]
```

If `_branch`, `_open_event` or `_next_weekday` are not already defined in `test_event_service.py`, copy them verbatim from `tests/test_public_tour_api.py:8-53`.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && uv run pytest tests/test_event_service.py -k "typed_venue_name or matches_a_catalogued" -v
```

Expected: FAIL — `venue_name` is rejected or silently dropped, so `row.venue_name` is `None`.

- [ ] **Step 3: Add the schema fields**

In `apps/api/app/domains/events/schemas.py`, inside `PublicRegistration` directly after `venue_id` (line 77):

```python
    # The venue as typed, for one we do not publish. Sent alongside venue_id, never
    # instead of it: the form fills venue_id in too when a suggestion was picked.
    venue_name: str | None = Field(default=None, max_length=300)
    # Routes the booking to a branch when the URL carries no slug.
    city: str | None = Field(default=None, max_length=80)
```

And in `RegistrationResponse`, directly after `venue_name` (line 103):

```python
    city: str | None = None
```

- [ ] **Step 4: Persist them in the service**

In `apps/api/app/domains/events/service.py`, replace the `registration = EventRegistration(...)` construction (lines 241-251) with:

```python
        # A name typed by hand that happens to be one of ours still earns the FK:
        # the couple should not lose the catalogue link for not using the dropdown.
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
            city=(payload.city or "").strip().lower() or None,
            guest_name=payload.name.strip(),
            email=email,
            mobile=payload.mobile,
            party_size=heads,
            visit_date=payload.visit_date,
            visit_slot=payload.visit_slot,
            source=source,
        )
```

Add the import at the top of the file, after the `app.domains.events.schemas` import block:

```python
from app.models.venue import Venue
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd apps/api && uv run pytest tests/test_event_service.py -v
```

Expected: PASS, and every pre-existing test in the file still passes.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/domains/events/schemas.py apps/api/app/domains/events/service.py apps/api/tests/test_event_service.py
git commit -m "feat(api): accept a typed venue name and city on a tour registration"
```

---

## Task 3: Resolve a branch from a city

**Files:**
- Modify: `apps/api/app/domains/events/service.py` (new method after `open_tour_scope`, line 183)
- Test: `apps/api/tests/test_event_service.py`

An org-wide event has `branch_id IS NULL`, and `notification_recipients(None)` returns `[]` — so a booking that falls back to an org-wide event would alert nobody internally. The event and the notified branch are therefore resolved separately.

- [ ] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_event_service.py`:

```python
def test_city_picks_the_branch_that_serves_it(api) -> None:
    jakarta = _branch(api, slug="jakarta", name="7Magic Jakarta")
    bali = _branch(api, slug="bali", name="7Magic Bali")
    api.client.patch(f"/api/v1/admin/branches/{bali['id']}", json={"city": "bali"})
    _open_event(api, jakarta["id"])
    bali_event = _open_event(api, bali["id"])

    response = api.client.post(
        "/api/v1/public/tour/register",
        json={
            "name": "Sari",
            "email": "sari@example.com",
            "venue_name": "Villa Uluwatu",
            "city": "bali",
            "visit_date": _next_weekday(),
        },
    )

    assert response.status_code == 201
    row = _registration_row(api, bali_event["id"])
    assert row is not None


def test_a_city_with_no_branch_falls_back_to_the_company_wide_event(api) -> None:
    """Most cities have no branch of their own today. The booking still has to land
    somewhere, and a branch_id NULL event is the standing catch-all."""
    _branch(api, slug="jakarta", name="7Magic Jakarta")
    org_event = _open_event(api, None)

    response = api.client.post(
        "/api/v1/public/tour/register",
        json={
            "name": "Dewi",
            "email": "dewi@example.com",
            "venue_name": "Some Hall",
            "city": "bandung",
            "visit_date": _next_weekday(),
        },
    )

    assert response.status_code == 201
    assert _registration_row(api, org_event["id"]) is not None


def test_no_open_event_anywhere_is_a_conflict(api) -> None:
    _branch(api, slug="jakarta", name="7Magic Jakarta")

    response = api.client.post(
        "/api/v1/public/tour/register",
        json={
            "name": "Andi",
            "email": "andi@example.com",
            "venue_name": "Some Hall",
            "city": "jakarta",
            "visit_date": _next_weekday(),
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "no_open_event"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && uv run pytest tests/test_event_service.py -k "city_picks or falls_back or no_open_event_anywhere" -v
```

Expected: FAIL with 404 — `/api/v1/public/tour/register` does not exist yet.

- [ ] **Step 3: Add the resolver**

In `apps/api/app/domains/events/service.py`, add this method to `EventService` directly after `open_tour_scope` (after line 183):

```python
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

        # No branch serves that city, so fall back to a company-wide event and let
        # the default branch's inbox take the lead.
        fallback = next(
            (branch for branch in branches if branch.is_default),
            branches[0] if branches else None,
        )
        if fallback is not None:
            event = await self.open_tour_event(session, fallback, now)
            if event is not None:
                return fallback, event
        return fallback, None
```

Add the import at the top of the file, after the `app.domains.branches.models` import:

```python
from app.domains.branches.service import branch_service
```

- [ ] **Step 4: Run tests to verify they still fail on the missing route**

```bash
cd apps/api && uv run pytest tests/test_event_service.py -k "city_picks" -v
```

Expected: still FAIL with 404. The resolver exists; Task 4 wires the route that calls it.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/domains/events/service.py
git commit -m "feat(api): resolve a tour branch and event from a city"
```

---

## Task 4: The branch-less public endpoints

**Files:**
- Modify: `apps/api/app/api/v1/public/tour.py`
- Test: `apps/api/tests/test_public_tour_api.py`, `apps/api/tests/test_event_service.py` (the three from Task 3 now pass)

- [ ] **Step 1: Write the failing test**

Append to `apps/api/tests/test_public_tour_api.py`:

```python
def test_generic_tour_payload_lists_venues_and_their_cities(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])
    _venue(api, name="Hotel Mulia", city="jakarta")
    _venue(api, name="Ayana Resort", city="bali")

    response = api.client.get("/api/v1/public/tour")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["open"] is True
    assert [row["name"] for row in body["venues"]] == ["Ayana Resort", "Hotel Mulia"]
    assert body["cities"] == ["bali", "jakarta"]


def test_generic_tour_payload_is_closed_when_no_event_is_open(api) -> None:
    """The page renders "not taking bookings" off this flag, so it has to be false
    before the form is ever drawn."""
    _branch(api)

    assert api.client.get("/api/v1/public/tour").json()["data"]["open"] is False
```

Copy the `_venue` helper from Task 2 into this file as well.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && uv run pytest tests/test_public_tour_api.py -k generic_tour -v
```

Expected: FAIL with 404.

- [ ] **Step 3: Add the routes**

In `apps/api/app/api/v1/public/tour.py`, add directly above `@router.get("/tour/branches")` (line 104):

```python
@router.get("/tour")
async def tour_form_payload(session: DbSession):
    """Everything the branch-less form needs: what to suggest, what to route by,
    and whether anyone is taking bookings at all."""
    venues = await _tourable_venues(session)
    any_branch, branch_ids = await event_service.open_tour_scope(session, datetime.now(UTC))
    return {
        "data": {
            "venues": venues,
            # Distinct, already ordered by the venue query. dict.fromkeys rather
            # than a set: the dropdown order has to be stable across requests.
            "cities": list(dict.fromkeys(row["city"] for row in venues)),
            "open": any_branch or bool(branch_ids),
        }
    }


@router.post("/tour/register", status_code=status.HTTP_201_CREATED)
async def register_without_a_branch(payload: PublicRegistration, session: DbSession):
    """The nav entry point: the guest named a venue and a city, and the city is what
    decides whose event and whose inbox this lead belongs to."""
    now = datetime.now(UTC)
    branch, event = await event_service.resolve_tour_target(session, payload.city, now)
    if event is None:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="no_open_event",
            message="We are not taking tour bookings right now.",
        )

    try:
        registration = await event_service.register(
            session, event=event, branch=branch, payload=payload, now=now, source="public"
        )
    except RegistrationBlocked as blocked:
        code = 422 if blocked.code == "validation_error" else status.HTTP_409_CONFLICT
        return error_response(status_code=code, code=blocked.code, message=blocked.message)

    await _notify(event=event, registration=registration, branch=branch)

    return {
        "data": {
            "id": registration.id,
            "public_id": str(registration.public_id),
            "party_size": registration.party_size,
            "visit_date": registration.visit_date.isoformat() if registration.visit_date else None,
            "visit_slot": registration.visit_slot,
            "branch_name": branch.name if branch else None,
        }
    }
```

- [ ] **Step 4: Run the whole API suite**

```bash
cd apps/api && uv run pytest -v
```

Expected: PASS, including the three Task 3 tests that were failing on the missing route.

- [ ] **Step 5: Lint**

```bash
cd apps/api && uv run ruff check .
```

Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/api/v1/public/tour.py apps/api/tests/test_public_tour_api.py
git commit -m "feat(api): public tour endpoints that need no branch in the URL"
```

---

## Task 5: The venue is the location, not the branch

**Files:**
- Modify: `apps/api/app/domains/events/emails.py:20-28`, `:66-82`, `:121-155`
- Test: `apps/api/tests/test_event_emails.py`

The confirmation email currently reads `Location: {branch_name}`, which sends the couple to the office. `{venue}` resolves from `event.venue` — a free-text string on the event — not from the registration at all.

- [ ] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_event_emails.py`:

```python
def test_the_confirmation_names_the_venue_as_the_location() -> None:
    """A venue tour visits the venue. Naming the branch here sent couples to the
    office instead."""
    from app.domains.branches.models import Branch
    from app.domains.events.emails import registration_confirmation
    from app.domains.events.models import Event, EventRegistration

    event = Event(name="Book a Tour", venue="ignored event venue")
    registration = EventRegistration(
        guest_name="Rina Putri", email="rina@example.com", party_size=2, venue_name="Villa Uluwatu"
    )
    branch = Branch(name="7Magic Jakarta")

    _subject, body = registration_confirmation(
        event=event, registration=registration, branch=branch
    )

    assert "Venue: Villa Uluwatu" in body
    assert "Location: 7Magic Jakarta" not in body


def test_the_branch_alert_names_the_venue_and_city() -> None:
    from app.domains.branches.models import Branch
    from app.domains.events.emails import branch_alert
    from app.domains.events.models import Event, EventRegistration

    event = Event(name="Book a Tour")
    registration = EventRegistration(
        guest_name="Budi",
        email="budi@example.com",
        party_size=2,
        venue_name="Some Hall",
        city="bandung",
        source="public",
    )

    _subject, body = branch_alert(event=event, registration=registration, branch=Branch(name="HQ"))

    assert "Venue: Some Hall" in body
    assert "City: bandung" in body
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd apps/api && uv run pytest tests/test_event_emails.py -k "names_the_venue" -v
```

Expected: FAIL — `Venue:` appears in neither body.

- [ ] **Step 3: Make the venue resolve from the registration**

In `apps/api/app/domains/events/emails.py`, replace the `"venue"` line in `build_replacements` (line 79) with:

```python
        # The registration's venue, not the event's: a venue tour visits the venue
        # the guest chose, and event.venue is only a label on the event itself.
        "venue": _venue_label(registration) or event.venue or "",
```

Add this helper directly above `build_replacements` (line 66):

```python
def _venue_label(registration: EventRegistration | None) -> str:
    """The venue, named. The FK wins when there is one; otherwise the guest's own
    words, because the tour network is wider than the published catalogue."""
    if registration is None:
        return ""
    if registration.venue is not None:
        return registration.venue.name
    return registration.venue_name or ""
```

- [ ] **Step 4: Fix the confirmation body**

Replace the `body = render_template(...)` call in `registration_confirmation` (lines 130-137) with:

```python
    body = render_template(
        "Hi {first_name},\n\n"
        "We have received your booking for {event_name}.\n"
        "Venue: {venue}\nDate: {visit_date}\nTime: {visit_slot}\nGuests: {party_size}\n\n"
        "{branch_name} will be in touch to confirm the time.\n\n"
        "See you soon!\nThe 7Magic team",
        replacements,
    )
```

- [ ] **Step 5: Add the venue and city to the branch alert**

In `branch_alert`, replace the `lines` list (lines 145-154) with:

```python
    lines = [
        f"Name: {registration.guest_name}",
        f"Email: {registration.email}",
        f"Mobile: {registration.mobile or '-'}",
        f"Venue: {_venue_label(registration) or '-'}",
        f"City: {registration.city or '-'}",
        f"Guests: {registration.party_size}",
        f"Date: {registration.visit_date.isoformat() if registration.visit_date else '-'}",
        f"Time: {registration.visit_slot or '-'}",
        f"Branch: {branch.name if branch else '-'}",
        f"Source: {registration.source}",
    ]
```

- [ ] **Step 6: Run the email tests**

```bash
cd apps/api && uv run pytest tests/test_event_emails.py -v
```

Expected: PASS. `_venue_label` reads `registration.venue`, a `selectin` relationship, so a detached row is safe.

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/domains/events/emails.py apps/api/tests/test_event_emails.py
git commit -m "fix(api): tour emails name the venue rather than the branch office"
```

---

## Task 6: The venue, named, in the CMS payload and export

**Files:**
- Modify: `apps/api/app/api/v1/admin/event_registrations.py:68-77`, `:116-134`, `:38-53`
- Test: `apps/api/tests/test_event_registration_api.py`

- [ ] **Step 1: Write the failing test**

Append to `apps/api/tests/test_event_registration_api.py`:

```python
def test_an_uncatalogued_venue_still_shows_a_name(api) -> None:
    """venue_name means "the venue, named" -- the FK when there is one, the guest's
    own words otherwise. A blank column would read as "no venue chosen"."""
    branch = _branch(api)
    event = _open_event(api, branch["id"])
    api.client.post(
        f"/api/v1/public/tour/branches/{branch['slug']}/register",
        json={
            "name": "Rina",
            "email": "rina@example.com",
            "venue_name": "Villa Uluwatu Cliffside",
            "city": "bali",
            "visit_date": _next_weekday(),
        },
    )

    row = api.client.get(f"/api/v1/admin/event-registrations?event_id={event['id']}").json()[
        "items"
    ][0]

    assert row["venue_name"] == "Villa Uluwatu Cliffside"
    assert row["city"] == "bali"

    export = api.client.get(f"/api/v1/admin/event-registrations/export?event_id={event['id']}")
    assert "Villa Uluwatu Cliffside" in export.text
    assert "bali" in export.text
```

If `_branch`, `_open_event` and `_next_weekday` are not in this file, copy them verbatim from `tests/test_public_tour_api.py:8-53`.

- [ ] **Step 2: Run test to verify it fails**

```bash
cd apps/api && uv run pytest tests/test_event_registration_api.py::test_an_uncatalogued_venue_still_shows_a_name -v
```

Expected: FAIL — `row["venue_name"]` is `None`.

- [ ] **Step 3: Coalesce in the detail payload**

In `apps/api/app/api/v1/admin/event_registrations.py`, replace line 76 with:

```python
    # The venue, named: the catalogue row when there is one, the guest's own words
    # otherwise. The tour network is wider than the published venue table.
    response["venue_name"] = (
        registration.venue.name if registration.venue else registration.venue_name
    )
```

- [ ] **Step 4: Add the city to the CSV**

Replace `CSV_HEADER` (lines 38-53) so it reads exactly:

```python
CSV_HEADER = [
    "Branch",
    "Event",
    "Venue",
    "City",
    "Name",
    "Email",
    "Mobile",
    "Party size",
    "Visit date",
    "Visit slot",
    "Status",
    "Follow up",
    "Source",
    "Registered at",
]
```

`"City"` is the only new entry; every other string is unchanged and in its existing order.

Then in the export loop replace line 122 with:

```python
                row.venue.name if row.venue else (row.venue_name or ""),
                row.city or "",
```

- [ ] **Step 5: Run the test**

```bash
cd apps/api && uv run pytest tests/test_event_registration_api.py -v
```

Expected: PASS.

- [ ] **Step 6: Full suite and lint**

```bash
cd apps/api && uv run pytest && uv run ruff check .
```

Expected: all tests pass, `All checks passed!`.

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/api/v1/admin/event_registrations.py apps/api/tests/test_event_registration_api.py
git commit -m "feat(api): name an uncatalogued venue in the CMS payload and export"
```

---

## Task 7: Message catalogue

**Files:**
- Modify: `apps/web/messages/id.json`, `apps/web/messages/en.json`

Indonesian is canonical. `nav_free_venue_tour` is deliberately the same English phrase in both files — the brand uses it untranslated.

- [ ] **Step 1: Add the Indonesian strings**

Add to `apps/web/messages/id.json`, keeping the file's existing key ordering convention (alphabetical within its groups if that is what the file does; otherwise append beside the other `tour_` keys):

```json
  "nav_free_venue_tour": "Free Venue Tour",
  "tour_pitch_title": "Kami yang kenal venue-nya. Anda yang dapat penawarannya.",
  "tour_pitch_body": "7Magic bekerja langsung dengan ratusan venue di Jakarta, Bali, Bogor, Tangerang, Batam dan Singapura. Kami yang mengatur semuanya dengan pihak venue, dan kami ikut menemani Anda saat survei.",
  "tour_pitch_venue": "Kami sudah bekerja dengan {venue}. Beri tahu kami kapan Anda ingin datang, dan sisanya kami yang urus.",
  "tour_pitch_1_title": "Kami yang mengatur, bukan Anda yang menelepon.",
  "tour_pitch_1_body": "Kami hubungi venue-nya, sesuaikan jadwalnya dengan Anda, dan pastikan tim mereka sudah siap menyambut. Tidak perlu mengejar formulir kontak atau menunggu balasan yang tak kunjung datang.",
  "tour_pitch_2_title": "Hubungan baik kami, keuntungan Anda.",
  "tour_pitch_2_body": "Karena kami membawa banyak pasangan ke venue yang sama setiap tahun, kami tahu ruang mana yang masih bisa dinegosiasikan dan apa yang bisa diminta.",
  "tour_pitch_3_title": "Gratis, dan tanpa ikatan.",
  "tour_pitch_3_body": "Survei venue tidak dipungut biaya sepeser pun, dan Anda tidak wajib memesan apa pun setelahnya.",
  "tour_field_venue_name": "Venue yang ingin Anda kunjungi",
  "tour_field_venue_hint": "Venue belum ada di daftar? Tulis saja namanya — jaringan kami lebih luas dari yang tampil di situs.",
  "tour_field_city": "Kota",
  "tour_field_city_choose": "Pilih kota",
  "tour_venue_locked": "Kunjungan ke {venue}",
  "tour_venue_change": "Ganti venue"
```

- [ ] **Step 2: Add the English strings**

Add the matching keys to `apps/web/messages/en.json`:

```json
  "nav_free_venue_tour": "Free Venue Tour",
  "tour_pitch_title": "We know the venues. You get the deal.",
  "tour_pitch_body": "7Magic works directly with hundreds of venues across Jakarta, Bali, Bogor, Tangerang, Batam and Singapore. We arrange everything with the venue, and we come with you on the visit.",
  "tour_pitch_venue": "We already work with {venue}. Tell us when you'd like to visit and we'll handle the rest.",
  "tour_pitch_1_title": "We arrange it — you don't chase it.",
  "tour_pitch_1_body": "We contact the venue, fit the date around you, and make sure their team is expecting you. No contact forms, no waiting on a reply that never comes.",
  "tour_pitch_2_title": "Our relationship, your advantage.",
  "tour_pitch_2_body": "Because we bring couples to the same venues year after year, we know where there's room to negotiate and what's worth asking for.",
  "tour_pitch_3_title": "Free, with no strings.",
  "tour_pitch_3_body": "The visit costs nothing, and you're under no obligation to book anything afterwards.",
  "tour_field_venue_name": "Venue you'd like to tour",
  "tour_field_venue_hint": "Venue not on the list? Just type its name — our network is wider than what's shown on the site.",
  "tour_field_city": "City",
  "tour_field_city_choose": "Choose a city",
  "tour_venue_locked": "Touring {venue}",
  "tour_venue_change": "Change venue"
```

- [ ] **Step 3: Compile and typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web check
```

Expected: no errors. Paraglide regenerates `apps/web/src/lib/paraglide/` (gitignored) as part of the check.

- [ ] **Step 4: Commit**

```bash
git add apps/web/messages/id.json apps/web/messages/en.json
git commit -m "feat(web): copy for the venue tour form and its nav entry"
```

---

## Task 8: The pitch block

**Files:**
- Create: `apps/web/src/lib/components/TourPitch.svelte`

- [ ] **Step 1: Write the component**

```svelte
<script lang="ts">
  import CalendarCheckIcon from '@lucide/svelte/icons/calendar-check';
  import HandshakeIcon from '@lucide/svelte/icons/handshake';
  import PhoneCallIcon from '@lucide/svelte/icons/phone-call';

  import * as m from '$lib/paraglide/messages';

  // The venue the guest arrived with, if any. Named here rather than described
  // generically: a couple who already chose a venue is a different reader.
  let { venueName = null }: { venueName?: string | null } = $props();

  const points = [
    { icon: PhoneCallIcon, title: m.tour_pitch_1_title(), body: m.tour_pitch_1_body() },
    { icon: HandshakeIcon, title: m.tour_pitch_2_title(), body: m.tour_pitch_2_body() },
    { icon: CalendarCheckIcon, title: m.tour_pitch_3_title(), body: m.tour_pitch_3_body() }
  ];
</script>

<section class="mt-6">
  <h2 class="text-xl font-semibold">{m.tour_pitch_title()}</h2>
  <p class="mt-3 max-w-2xl text-muted-foreground">
    {venueName ? m.tour_pitch_venue({ venue: venueName }) : m.tour_pitch_body()}
  </p>

  <div class="mt-6 grid gap-5 sm:grid-cols-3">
    {#each points as point (point.title)}
      <div>
        <point.icon class="size-5 text-muted-foreground" />
        <h3 class="mt-2 text-sm font-semibold">{point.title}</h3>
        <p class="mt-1 text-sm text-muted-foreground">{point.body}</p>
      </div>
    {/each}
  </div>
</section>
```

- [ ] **Step 2: Typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web check
```

Expected: no errors. If `@lucide/svelte/icons/handshake` or `/phone-call` does not resolve, substitute icons that exist in the installed version — `users` and `phone` are safe fallbacks.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/lib/components/TourPitch.svelte
git commit -m "feat(web): the venue tour pitch block"
```

---

## Task 9: The shared tour form

**Files:**
- Create: `apps/web/src/lib/components/TourForm.svelte`

This is the only place the form fields exist. Both entry points render it, so they cannot drift.

- [ ] **Step 1: Export the venue type from `$lib/tour`**

The form and both loaders share one wire shape. Add to `apps/web/src/lib/tour.ts`, below the `TourBranch` type:

```ts
/** A venue the form can suggest, as `/api/v1/public/tour` returns it. */
export type TourVenue = { id: number; name: string; city: string };
```

- [ ] **Step 2: Write the component**

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';

  import DateField from '$lib/components/DateField.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as m from '$lib/paraglide/messages';
  // Imported, never redeclared: `export type` is invalid in a Svelte instance
  // script, and $lib/tour is where the wire shape already lives.
  import type { TourVenue } from '$lib/tour';

  let {
    venues,
    cities,
    lockedVenue = null,
    changeVenueHref = null
  }: {
    venues: TourVenue[];
    cities: string[];
    /** Set when the guest arrived from a venue page, so the form does not ask. */
    lockedVenue?: TourVenue | null;
    /** Clears ?venue= and reveals the fields. Null when there is nothing to clear. */
    changeVenueHref?: string | null;
  } = $props();

  let venueName = $state('');
  let city = $state('');
  let visitDate = $state('');
  let guests = $state(2);

  // The id only survives when the typed name still matches the suggestion it came
  // from. Editing the text after picking means the guest meant something else, and
  // silently keeping the old FK would book the wrong venue.
  const matched = $derived(
    venues.find((venue) => venue.name.toLowerCase() === venueName.trim().toLowerCase()) ?? null
  );

  // A matched venue knows its own city, so the dropdown stops being a question.
  const effectiveCity = $derived(lockedVenue?.city ?? matched?.city ?? city);

  const today = new Date().toISOString().slice(0, 10);

  const canSubmit = $derived(
    Boolean(visitDate) && (lockedVenue ? true : Boolean(venueName.trim()) && Boolean(effectiveCity))
  );

  const cityLabel = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);
</script>

<form method="POST" use:enhance class="mt-8 grid gap-4 sm:grid-cols-2">
  {#if lockedVenue}
    <input type="hidden" name="venue_id" value={lockedVenue.id} />
    <input type="hidden" name="venue_name" value={lockedVenue.name} />
    <input type="hidden" name="city" value={lockedVenue.city} />
    <div class="sm:col-span-2 flex flex-wrap items-center gap-3 rounded-xl border border-border/60 p-4">
      <span class="font-medium">{m.tour_venue_locked({ venue: lockedVenue.name })}</span>
      <span class="text-sm text-muted-foreground">{cityLabel(lockedVenue.city)}</span>
      {#if changeVenueHref}
        <a class="ml-auto text-sm underline" href={changeVenueHref}>{m.tour_venue_change()}</a>
      {/if}
    </div>
  {:else}
    <div class="grid gap-2 sm:col-span-2">
      <Label for="venue_name">{m.tour_field_venue_name()}</Label>
      <!-- A datalist, not a select: the network is wider than the catalogue, so an
           unlisted venue has to be typeable. Picking a suggestion fills the same
           input, which is how `matched` recovers the id. -->
      <Input id="venue_name" name="venue_name" list="tour-venues" bind:value={venueName} required />
      <datalist id="tour-venues">
        {#each venues as venue (venue.id)}
          <option value={venue.name}>{cityLabel(venue.city)}</option>
        {/each}
      </datalist>
      <p class="text-xs text-muted-foreground">{m.tour_field_venue_hint()}</p>
      {#if matched}
        <input type="hidden" name="venue_id" value={matched.id} />
      {/if}
    </div>

    <div class="grid gap-2 sm:col-span-2">
      <Label for="city">{m.tour_field_city()}</Label>
      <select
        id="city"
        name="city"
        value={effectiveCity}
        onchange={(event) => (city = event.currentTarget.value)}
        required
        class="h-10 rounded-lg border border-border/60 bg-background px-3 text-sm"
      >
        <option value="">{m.tour_field_city_choose()}</option>
        {#each cities as option (option)}
          <option value={option}>{cityLabel(option)}</option>
        {/each}
      </select>
    </div>
  {/if}

  <div class="grid gap-2">
    <Label for="name">{m.tour_field_name()}</Label>
    <Input id="name" name="name" required />
  </div>
  <div class="grid gap-2">
    <Label for="email">{m.tour_field_email()}</Label>
    <Input id="email" name="email" type="email" required />
  </div>
  <div class="grid gap-2">
    <Label for="mobile">{m.tour_field_mobile()}</Label>
    <Input id="mobile" name="mobile" />
  </div>
  <div class="grid gap-2">
    <Label for="visit_date">{m.tour_field_date()}</Label>
    <!-- Any future day, no slots: the team confirms a time when they follow up,
         so there is nothing here to grey out. -->
    <DateField name="visit_date" bind:value={visitDate} min={today} />
  </div>
  <div class="grid gap-2">
    <Label for="party_size">{m.tour_field_guests_total()}</Label>
    <Input id="party_size" name="party_size" type="number" min="1" max="20" bind:value={guests} />
    <p class="text-xs text-muted-foreground">{m.tour_guests_hint()}</p>
  </div>

  <div class="sm:col-span-2">
    <Button type="submit" disabled={!canSubmit}>{m.tour_submit()}</Button>
  </div>
</form>
```

- [ ] **Step 3: Typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web check
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/TourForm.svelte apps/web/src/lib/tour.ts
git commit -m "feat(web): one tour form shared by every entry point"
```

---

## Task 10: `/tour` becomes the form

**Files:**
- Modify: `apps/web/src/routes/tour/+page.server.ts` (replace the file)
- Modify: `apps/web/src/routes/tour/+page.svelte` (replace the file)

- [ ] **Step 1: Add the generic loader**

Replace `apps/web/src/routes/tour/+page.server.ts` entirely with:

```ts
import { fail } from '@sveltejs/kit';

import { fetchJson, getApiBaseUrl } from '$lib/api';
import type { TourVenue } from '$lib/tour';

import type { Actions, PageServerLoad } from './$types';

type TourFormPayload = { venues: TourVenue[]; cities: string[]; open: boolean };

export const load: PageServerLoad = async ({ fetch, url }) => {
  let payload: TourFormPayload = { venues: [], cities: [], open: false };
  try {
    const data = await fetchJson<{ data: TourFormPayload }>('/api/v1/public/tour', fetch);
    payload = data.data;
  } catch {
    // An empty, closed payload rather than a 500: the page renders "not taking
    // bookings" from `open`, which is a better failure than a broken funnel.
  }

  const requested = url.searchParams.get('venue');
  const lockedVenue = requested
    ? (payload.venues.find((venue) => String(venue.id) === requested) ?? null)
    : null;

  return { ...payload, lockedVenue };
};

export const actions: Actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();
    const partySize = Number(form.get('party_size') ?? 1);
    const venueId = String(form.get('venue_id') ?? '').trim();

    const response = await fetch(`${getApiBaseUrl()}/api/v1/public/tour/register`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        name: String(form.get('name') ?? '').trim(),
        email: String(form.get('email') ?? '').trim(),
        mobile: String(form.get('mobile') ?? '').trim() || null,
        venue_id: venueId ? Number(venueId) : null,
        venue_name: String(form.get('venue_name') ?? '').trim() || null,
        city: String(form.get('city') ?? '').trim() || null,
        visit_date: String(form.get('visit_date') ?? '') || null,
        // Clamped rather than trusted: the input has min/max, but a hand-rolled
        // POST does not have to honour them.
        party_size: Number.isFinite(partySize)
          ? Math.min(Math.max(Math.trunc(partySize), 1), 20)
          : 1
      })
    });

    if (response.ok) {
      return { ok: true, code: '' };
    }

    const payload = (await response.json().catch(() => ({}))) as { error?: { code?: string } };
    return fail(response.status === 422 ? 422 : 409, {
      ok: false,
      code: payload.error?.code ?? 'generic'
    });
  }
};
```

- [ ] **Step 2: Replace the page**

Replace `apps/web/src/routes/tour/+page.svelte` entirely with:

```svelte
<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import TourForm from '$lib/components/TourForm.svelte';
  import TourPitch from '$lib/components/TourPitch.svelte';
  import * as m from '$lib/paraglide/messages';
  import { localizeHref } from '$lib/paraglide/runtime';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const ERROR_MESSAGES: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    event_full: m.tour_error_full
  };

  const errorMessage = $derived(
    form && form.ok === false ? (ERROR_MESSAGES[form.code] ?? m.tour_error_generic)() : ''
  );
</script>

<svelte:head>
  <title>{m.tour_meta_title()}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-3xl px-4 py-12">
  <h1 class="text-3xl font-semibold">{m.tour_title()}</h1>

  <TourPitch venueName={data.lockedVenue?.name ?? null} />

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.open}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <TourForm
      venues={data.venues}
      cities={data.cities}
      lockedVenue={data.lockedVenue}
      changeVenueHref={data.lockedVenue ? localizeHref('/tour') : null}
    />
  {/if}
</main>

<PublicFooter />
```

- [ ] **Step 3: Typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web check
```

Expected: no errors.

- [ ] **Step 4: Verify both entry states by hand**

Start the stack with `./rundev.sh`, then open:
- `https://7magic.localhost/tour` — expect the pitch, a free-text venue input with a suggestion list, and a city dropdown.
- `https://7magic.localhost/tour?venue=<id of any active venue>` — expect the locked venue line naming it, no venue or city fields, and a working "Ganti venue" link back to `/tour`.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/routes/tour/+page.server.ts apps/web/src/routes/tour/+page.svelte
git commit -m "feat(web): /tour books a venue tour instead of picking a branch"
```

---

## Task 11: `/tour/[slug]` renders the shared form

**Files:**
- Modify: `apps/web/src/routes/tour/[slug]/+page.svelte:1-133`
- Modify: `apps/web/src/routes/tour/[slug]/+page.server.ts:37-49`, `:52-76`

- [ ] **Step 1: Add cities and the locked venue to the loader**

In `apps/web/src/routes/tour/[slug]/+page.server.ts`, replace the `return` inside `load` (line 45) with:

```ts
    const requested = url.searchParams.get('venue');
    return {
      ...data.data,
      // Distinct venue cities, so the branch page offers the same city list as the
      // generic one. The branch's own city is not it: the venue may be elsewhere.
      cities: [...new Set(data.data.venues.map((venue) => venue.city))].sort(),
      lockedVenue: requested
        ? (data.data.venues.find((venue) => String(venue.id) === requested) ?? null)
        : null
    };
```

- [ ] **Step 2: Send the new fields from the action**

In the same file, add these two lines to the POST body inside `actions.default`, directly after the `venue_id` line (line 70):

```ts
          venue_name: String(form.get('venue_name') ?? '').trim() || null,
          city: String(form.get('city') ?? '').trim() || null,
```

- [ ] **Step 3: Replace the page's inline form**

Replace `apps/web/src/routes/tour/[slug]/+page.svelte` entirely with:

```svelte
<script lang="ts">
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import TourForm from '$lib/components/TourForm.svelte';
  import TourPitch from '$lib/components/TourPitch.svelte';
  import * as m from '$lib/paraglide/messages';
  import { localizeHref } from '$lib/paraglide/runtime';

  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const ERROR_MESSAGES: Record<string, () => string> = {
    already_registered: m.tour_error_already,
    event_full: m.tour_error_full
  };

  const errorMessage = $derived(
    form && form.ok === false ? (ERROR_MESSAGES[form.code] ?? m.tour_error_generic)() : ''
  );
</script>

<svelte:head>
  <title>{`${m.tour_title()} · ${data.branch.name}`}</title>
  <meta name="description" content={m.tour_meta_description()} />
</svelte:head>

<PublicHeader />

<main class="mx-auto w-full max-w-3xl px-4 py-12">
  <!-- No branch address: the visit happens at the venue the guest names below, so
       showing head office's street would point them at the wrong place. -->
  <h1 class="text-3xl font-semibold">{data.branch.name}</h1>

  {#if data.settings.tour_intro_html}
    <!-- A branch that wrote its own pitch replaces the default one rather than
         stacking a second one under it. Sanitized on write; see core/html.py. -->
    <div class="prose mt-4">{@html data.settings.tour_intro_html}</div>
  {:else}
    <TourPitch venueName={data.lockedVenue?.name ?? null} />
  {/if}

  {#if form?.ok}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_success()}</p>
  {:else if !data.event || !data.event.registration_open}
    <p class="mt-8 rounded-xl border border-border/60 p-4">{m.tour_closed()}</p>
  {:else}
    {#if errorMessage}
      <p class="mt-6 text-sm text-destructive">{errorMessage}</p>
    {/if}

    <TourForm
      venues={data.venues}
      cities={data.cities}
      lockedVenue={data.lockedVenue}
      changeVenueHref={data.lockedVenue ? localizeHref(`/tour/${data.branch.slug}`) : null}
    />
  {/if}

  {#if data.settings.arrival_instructions || data.settings.parking_notes}
    <div class="mt-10 grid gap-2 text-sm text-muted-foreground">
      {#if data.settings.arrival_instructions}<p>{data.settings.arrival_instructions}</p>{/if}
      {#if data.settings.parking_notes}<p>{data.settings.parking_notes}</p>{/if}
    </div>
  {/if}
</main>

<PublicFooter />
```

- [ ] **Step 4: Typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web check
```

Expected: no errors.

- [ ] **Step 5: Verify by hand**

With `./rundev.sh` running, open `https://7magic.localhost/tour/jakarta` and submit a booking for a typed venue. Confirm the success panel renders and the row appears in the CMS at `https://cms.7magic.localhost/events/<id>`.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/routes/tour/\[slug\]/
git commit -m "feat(web): the branch tour page renders the shared form"
```

---

## Task 12: The nav entry

**Files:**
- Modify: `apps/web/src/lib/components/PublicHeader.svelte:36-43`
- Test: `apps/web/src/lib/components/PublicHeader.test.ts`

- [ ] **Step 1: Write the failing test**

In `apps/web/src/lib/components/PublicHeader.test.ts`, extend the `navLinks` filter (lines 16-20) to include `/tour`:

```ts
const navLinks = () =>
  screen.getAllByRole('link').filter((a) => {
    const href = a.getAttribute('href');
    return (
      href === '/wedding-venue/search' ||
      href === '/artikel' ||
      href === '/our-vendors' ||
      href === '/about' ||
      href === '/tour'
    );
  });
```

Then append this test inside the `describe` block:

```ts
  it('offers the free venue tour, under the same English label in both locales', () => {
    render(PublicHeader);
    const hrefs = navLinks().map((a) => a.getAttribute('href'));
    expect(hrefs).toContain('/tour');
    expect(screen.getAllByText('Free Venue Tour').length).toBeGreaterThan(0);
  });
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web test -- PublicHeader
```

Expected: FAIL — `hrefs` does not contain `/tour`.

- [ ] **Step 3: Add the nav entry**

In `apps/web/src/lib/components/PublicHeader.svelte`, append to the `links` array (after line 42):

```ts
    { href: '/about', label: m.nav_about() },
    // Last in `links`, which is what puts it in the mobile sheet for free -- the
    // sheet renders this same array. Untranslated on purpose: the brand uses the
    // English phrase in both locales.
    { href: '/tour', label: m.nav_free_venue_tour() }
```

(Replacing the existing `{ href: '/about', label: m.nav_about() }` line, which loses its trailing position.)

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm --filter @7magic/web test -- PublicHeader
```

Expected: PASS, all seven tests.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/PublicHeader.svelte apps/web/src/lib/components/PublicHeader.test.ts
git commit -m "feat(web): a Free Venue Tour entry in the public nav"
```

---

## Task 13: The venue column in the CMS

**Files:**
- Modify: `apps/cms/src/routes/events/[id]/+page.svelte:158-186`

The registrations table has no venue column at all today, so a front-desk staffer cannot see where a guest is going.

- [ ] **Step 1: Add the header cell**

In `apps/cms/src/routes/events/[id]/+page.svelte`, insert directly after the `Branch` head (line 162):

```svelte
        <Table.Head>Venue</Table.Head>
```

- [ ] **Step 2: Add the body cell**

Insert directly after the branch cell (line 177):

```svelte
          <Table.Cell>
            <div>{registration.venue_name ?? '—'}</div>
            <!-- The city only when there is no catalogue row behind the name: it is
                 how a staffer spots a venue we do not list yet. -->
            {#if registration.city && !registration.venue_id}
              <div class="text-xs text-muted-foreground">{registration.city}</div>
            {/if}
          </Table.Cell>
```

- [ ] **Step 3: Typecheck**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm check
```

Expected: no errors. If the registration type is declared locally in `+page.server.ts`, add `venue_name: string | null`, `venue_id: number | null` and `city: string | null` to it.

- [ ] **Step 4: Verify by hand**

Open `https://cms.7magic.localhost/events/<id>` and confirm the Venue column shows the typed name for the booking made in Task 11, with the city beneath it.

- [ ] **Step 5: Commit**

```bash
git add apps/cms/src/routes/events/\[id\]/+page.svelte
git commit -m "feat(cms): show the venue a tour registration is for"
```

---

## Task 14: Full verification

- [ ] **Step 1: Run everything**

```bash
cd /Users/bsalim/C/7magic-monorepo && pnpm test && pnpm check
cd apps/api && uv run pytest && uv run ruff check .
```

Expected: all suites pass, `All checks passed!`, no svelte-check errors.

- [ ] **Step 2: Walk the three entry points**

With `./rundev.sh` running:

1. `https://7magic.localhost/wedding-venue/<city>/<slug>` → "Book a tour" → lands on `/tour?venue=<id>` with the venue locked in. Submit; confirm the success panel.
2. `https://7magic.localhost/tour` from the nav link → type a venue that is *not* in the suggestions, pick a city, submit. Confirm 201 and a CMS row with the typed name.
3. `https://7magic.localhost/tour/jakarta` → confirm the branch intro renders and the form submits.

- [ ] **Step 3: Confirm the emails name the venue**

Check the API log or the mail sink for the confirmation sent in step 2. The body must contain `Venue: <the typed name>` and must not read `Location: 7Magic Jakarta`.

- [ ] **Step 4: Check the affected scope**

```bash
npx gitnexus analyze
```

Then run `gitnexus_detect_changes()` and confirm the affected symbols are the tour, event and registration paths only.
