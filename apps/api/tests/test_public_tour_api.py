from __future__ import annotations

from datetime import UTC, datetime, timedelta

import app.api.v1.public.tour as tour_module


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    branch = api.client.post(
        "/api/v1/admin/branches",
        json={
            "slug": slug,
            "name": name,
            "timezone": "Asia/Jakarta",
            "public_email": f"{slug}@7magic.test",
        },
    ).json()["data"]
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={
            "items": [
                {"day_of_week": day, "opens_at_local": "10:00:00", "closes_at_local": "18:00:00"}
                for day in range(1, 7)
            ]
        },
    )
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/settings",
        json={"tour_notification_recipients": ["ops@7magic.test"]},
    )
    return branch


def _open_event(api, branch_id: int, **overrides) -> dict:
    now = datetime.now(UTC)
    body = {
        "branch_id": branch_id,
        "name": "Book a Tour",
        "description_html": "<p>Datang ya</p>",
        "registration_opens_at": (now - timedelta(days=1)).isoformat(),
        "registration_closes_at": (now + timedelta(days=30)).isoformat(),
        "event_start_at": (now + timedelta(days=31)).isoformat(),
    }
    body.update(overrides)
    return api.client.post("/api/v1/admin/events", json=body).json()["data"]


def _next_weekday(offset_days: int = 7) -> str:
    """A date the branch is open on: Monday-Saturday."""
    candidate = (datetime.now(UTC) + timedelta(days=offset_days)).date()
    while candidate.isoweekday() == 7:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def test_branch_list_shows_only_active_bookable_branches(api) -> None:
    listed = _branch(api)
    _open_event(api, listed["id"])
    hidden = _branch(api, slug="bali", name="7Magic Bali")
    _open_event(api, hidden["id"])
    api.client.patch(f"/api/v1/admin/branches/{hidden['id']}", json={"bookable": False})

    response = api.client.get("/api/v1/public/tour/branches")

    assert response.status_code == 200
    assert [row["slug"] for row in response.json()["items"]] == ["jakarta"]


def test_a_branch_with_no_open_event_is_not_listed(api) -> None:
    """Active and bookable is not enough. A registration hangs off an event, so a
    branch without one would show a form that only says "not taking bookings"."""
    _branch(api)

    response = api.client.get("/api/v1/public/tour/branches")

    assert response.json()["items"] == []


def test_a_company_wide_event_makes_every_branch_bookable(api) -> None:
    """branch_id NULL is how one standing "Book a Tour" covers every branch,
    including ones added after it."""
    _branch(api)
    _branch(api, slug="bali", name="7Magic Bali")
    _open_event(api, None)

    response = api.client.get("/api/v1/public/tour/branches")

    assert sorted(row["slug"] for row in response.json()["items"]) == ["bali", "jakarta"]


def test_branch_detail_carries_the_open_event_hours_and_closures(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])
    # Relative to today, not a fixed date: closures are only advertised inside
    # CLOSURE_HORIZON_DAYS, so a hardcoded date makes the test pass or fail
    # depending on when it runs.
    closed_on = (datetime.now(UTC) + timedelta(days=30)).date().isoformat()
    api.client.post(
        f"/api/v1/admin/branches/{branch['id']}/closures",
        json={
            "starts_at_local": f"{closed_on}T00:00:00",
            "ends_at_local": f"{closed_on}T23:59:00",
            "full_day": True,
            "public_label": "Libur Natal",
        },
    )

    response = api.client.get("/api/v1/public/tour/branches/jakarta")

    body = response.json()["data"]
    assert body["branch"]["name"] == "7Magic Jakarta"
    assert body["event"]["registration_open"] is True
    assert [row["day_of_week"] for row in body["opening_hours"]] == [1, 2, 3, 4, 5, 6]
    assert body["closed_dates"] == [closed_on]


def test_registering_creates_the_row_and_sends_both_emails(api, monkeypatch) -> None:
    sent: list[dict] = []

    async def fake_send(**kwargs):
        sent.append(kwargs)

    monkeypatch.setattr(tour_module, "send_email", fake_send)

    branch = _branch(api)
    _open_event(api, branch["id"])

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={
            "name": "Rina Kartika",
            "email": "rina@example.test",
            "mobile": "+628111111111",
            "visit_date": _next_weekday(),
            "visit_slot": "10:00",
            "guests": [{"name": "Budi"}],
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["party_size"] == 2
    assert [call["to"] for call in sent] == [["rina@example.test"], ["ops@7magic.test"]]


def test_a_failing_email_still_returns_201(api, monkeypatch) -> None:
    """A Resend outage must not cost a lead."""

    async def exploding_send(**kwargs):
        raise RuntimeError("resend is down")

    monkeypatch.setattr(tour_module, "send_email", exploding_send)

    branch = _branch(api)
    _open_event(api, branch["id"])

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={"name": "Rina", "email": "rina@example.test", "visit_date": _next_weekday()},
    )

    assert response.status_code == 201

    listed = api.client.get("/api/v1/admin/event-registrations")
    assert [row["email"] for row in listed.json()["items"]] == ["rina@example.test"]


def test_registering_for_a_closed_window_returns_409(api, monkeypatch) -> None:
    async def fake_send(**kwargs):
        return None

    monkeypatch.setattr(tour_module, "send_email", fake_send)

    branch = _branch(api)
    now = datetime.now(UTC)
    _open_event(
        api,
        branch["id"],
        registration_opens_at=(now - timedelta(days=10)).isoformat(),
        registration_closes_at=(now - timedelta(days=1)).isoformat(),
    )

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={"name": "Rina", "email": "rina@example.test", "visit_date": _next_weekday()},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] in {"registration_closed", "no_open_event"}


def test_an_unknown_branch_slug_returns_404(api) -> None:
    response = api.client.get("/api/v1/public/tour/branches/tidak-ada")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "branch_not_found"


def _venue(api, *, name: str, slug: str, city: str, status: str = "active") -> int:
    """`address` and `district` are the only venue columns without a default."""
    from app.models.venue import Venue

    holder: dict[str, int] = {}

    async def seed(session) -> None:
        venue = Venue(
            name=name,
            slug=slug,
            address="Jl. Test",
            district="Test",
            city=city,
            status=status,
        )
        session.add(venue)
        await session.flush()
        holder["id"] = venue.id

    api.seed(seed)
    return holder["id"]


def test_generic_tour_payload_lists_venues_and_their_cities(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])
    _venue(api, name="Hotel Mulia", slug="hotel-mulia", city="jakarta")
    _venue(api, name="Ayana Resort", slug="ayana-resort", city="bali")

    response = api.client.get("/api/v1/public/tour")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["open"] is True
    # Ordered by city then name, which is how the venue query already returns them.
    assert [row["name"] for row in body["venues"]] == ["Ayana Resort", "Hotel Mulia"]
    assert body["cities"] == ["bali", "jakarta"]


def test_generic_tour_payload_is_closed_when_no_event_is_open(api) -> None:
    """The page renders "not taking bookings" off this flag, so it has to be false
    before the form is ever drawn."""
    _branch(api)

    assert api.client.get("/api/v1/public/tour").json()["data"]["open"] is False


def test_a_draft_venue_is_never_suggested(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])
    _venue(api, name="Secret Villa", slug="secret-villa", city="bali", status="draft")

    body = api.client.get("/api/v1/public/tour").json()["data"]

    assert body["venues"] == []
    assert body["cities"] == []


def test_booking_without_a_branch_in_the_url_is_accepted(api) -> None:
    branch = _branch(api)
    _open_event(api, branch["id"])

    response = api.client.post(
        "/api/v1/public/tour/register",
        json={
            "name": "Dewi",
            "email": "dewi@example.com",
            "venue_name": "Villa Uluwatu Cliffside",
            "city": "bandung",
            "visit_date": _next_weekday(),
            "party_size": 2,
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["branch_name"] == "7Magic Jakarta"


def test_booking_without_a_branch_is_a_conflict_when_nothing_is_open(api) -> None:
    _branch(api)

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
