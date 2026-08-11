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
            "publicEmail": f"{slug}@7magic.test",
        },
    ).json()["data"]
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={
            "items": [
                {"dayOfWeek": day, "opensAtLocal": "10:00:00", "closesAtLocal": "18:00:00"}
                for day in range(1, 7)
            ]
        },
    )
    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/settings",
        json={"tourNotificationRecipients": ["ops@7magic.test"]},
    )
    return branch


def _open_event(api, branch_id: int, **overrides) -> dict:
    now = datetime.now(UTC)
    body = {
        "branchId": branch_id,
        "name": "Book a Tour",
        "descriptionHtml": "<p>Datang ya</p>",
        "registrationOpensAt": (now - timedelta(days=1)).isoformat(),
        "registrationClosesAt": (now + timedelta(days=30)).isoformat(),
        "eventStartAt": (now + timedelta(days=31)).isoformat(),
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
    _branch(api)
    hidden = _branch(api, slug="bali", name="7Magic Bali")
    api.client.patch(f"/api/v1/admin/branches/{hidden['id']}", json={"bookable": False})

    response = api.client.get("/api/v1/public/tour/branches")

    assert response.status_code == 200
    assert [row["slug"] for row in response.json()["items"]] == ["jakarta"]


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
            "startsAtLocal": f"{closed_on}T00:00:00",
            "endsAtLocal": f"{closed_on}T23:59:00",
            "fullDay": True,
            "publicLabel": "Libur Natal",
        },
    )

    response = api.client.get("/api/v1/public/tour/branches/jakarta")

    body = response.json()["data"]
    assert body["branch"]["name"] == "7Magic Jakarta"
    assert body["event"]["registrationOpen"] is True
    assert [row["dayOfWeek"] for row in body["openingHours"]] == [1, 2, 3, 4, 5, 6]
    assert body["closedDates"] == [closed_on]


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
            "visitDate": _next_weekday(),
            "visitSlot": "10:00",
            "guests": [{"name": "Budi"}],
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["partySize"] == 2
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
        json={"name": "Rina", "email": "rina@example.test", "visitDate": _next_weekday()},
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
        registrationOpensAt=(now - timedelta(days=10)).isoformat(),
        registrationClosesAt=(now - timedelta(days=1)).isoformat(),
    )

    response = api.client.post(
        "/api/v1/public/tour/branches/jakarta/register",
        json={"name": "Rina", "email": "rina@example.test", "visitDate": _next_weekday()},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] in {"registration_closed", "no_open_event"}


def test_an_unknown_branch_slug_returns_404(api) -> None:
    response = api.client.get("/api/v1/public/tour/branches/tidak-ada")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "branch_not_found"
