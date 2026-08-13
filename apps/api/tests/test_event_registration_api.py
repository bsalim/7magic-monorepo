from __future__ import annotations

import csv
import io

from tests.conftest import admin_user


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    return api.client.post(
        "/api/v1/admin/branches",
        json={"slug": slug, "name": name, "timezone": "Asia/Jakarta"},
    ).json()["data"]


def _event(api, branch_id: int) -> dict:
    return api.client.post(
        "/api/v1/admin/events", json={"branch_id": branch_id, "name": "Book a Tour"}
    ).json()["data"]


def _register(api, event_id: int, email="rina@example.test", guests=None) -> dict:
    return api.client.post(
        "/api/v1/admin/event-registrations",
        json={
            "event_id": event_id,
            "name": "Rina",
            "email": email,
            "mobile": "+628111111111",
            "guests": guests or [],
        },
    ).json()["data"]


def test_a_registration_created_in_the_cms_is_sourced_cms(api) -> None:
    event = _event(api, _branch(api)["id"])

    registration = _register(api, event["id"])

    assert registration["source"] == "cms"
    assert registration["status"] == "registered"


def test_party_size_counts_the_extra_guests(api) -> None:
    event = _event(api, _branch(api)["id"])

    registration = _register(api, event["id"], guests=[{"name": "Budi"}, {"name": "Sari"}])

    assert registration["party_size"] == 3
    assert [guest["name"] for guest in registration["guests"]] == ["Budi", "Sari"]


def test_marking_attended_stamps_the_time_and_the_user(api) -> None:
    event = _event(api, _branch(api)["id"])
    registration = _register(api, event["id"])

    updated = api.client.patch(
        f"/api/v1/admin/event-registrations/{registration['id']}",
        json={"status": "attended"},
    )

    assert updated.status_code == 200
    assert updated.json()["data"]["attended_at"] is not None


def test_registrations_carry_the_branch_column(api) -> None:
    branch = _branch(api)
    event = _event(api, branch["id"])
    _register(api, event["id"])

    listed = api.client.get("/api/v1/admin/event-registrations")

    row = listed.json()["items"][0]
    assert row["branch_name"] == "7Magic Jakarta"
    assert row["event_name"] == "Book a Tour"


def test_a_branch_scoped_user_never_sees_another_branch_registrations(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _register(api, _event(api, first["id"])["id"], email="jakarta@example.test")
    _register(api, _event(api, second["id"])["id"], email="bali@example.test")

    api.login(admin_user(roles=["branch_staff"], branch_grants=(("branch_staff", second["id"]),)))
    listed = api.client.get("/api/v1/admin/event-registrations")

    assert [row["email"] for row in listed.json()["items"]] == ["bali@example.test"]


def test_export_returns_csv_with_a_header_row(api) -> None:
    event = _event(api, _branch(api)["id"])
    _register(api, event["id"])

    response = api.client.get("/api/v1/admin/event-registrations/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    rows = list(csv.reader(io.StringIO(response.text)))
    assert rows[0] == [
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
    # By header name, not a fixed index: inserting a column ahead of it should fail
    # on the header assertion above, not silently here.
    assert rows[1][rows[0].index("Email")] == "rina@example.test"


def test_an_uncatalogued_venue_still_shows_a_name(api) -> None:
    """venue_name means "the venue, named" -- the catalogue row when there is one,
    the guest's own words otherwise. A blank column would read as "no venue chosen"
    for a booking that named one perfectly clearly."""
    branch = _branch(api)
    event = _event(api, branch["id"])
    api.client.post(
        f"/api/v1/public/tour/branches/{branch['slug']}/register",
        json={
            "name": "Rina",
            "email": "rina@example.test",
            "venue_name": "Villa Uluwatu Cliffside",
            "city": "bali",
        },
    )

    rows = api.client.get(f"/api/v1/admin/event-registrations?event_id={event['id']}").json()[
        "items"
    ]

    assert rows[0]["venue_name"] == "Villa Uluwatu Cliffside"
    assert rows[0]["city"] == "bali"

    export = api.client.get(f"/api/v1/admin/event-registrations/export?event_id={event['id']}")
    assert "Villa Uluwatu Cliffside" in export.text
    assert "bali" in export.text
