from __future__ import annotations

from tests.conftest import admin_user


def _branch(api, slug="jakarta", name="7Magic Jakarta") -> dict:
    return api.client.post(
        "/api/v1/admin/branches",
        json={"slug": slug, "name": name, "timezone": "Asia/Jakarta"},
    ).json()["data"]


def _event(api, branch_id: int | None, name="Book a Tour") -> dict:
    return api.client.post(
        "/api/v1/admin/events",
        json={"branchId": branch_id, "name": name, "descriptionHtml": "<p>Datang ya</p>"},
    ).json()["data"]


def test_create_event_sanitizes_its_description(api) -> None:
    branch = _branch(api)

    created = api.client.post(
        "/api/v1/admin/events",
        json={
            "branchId": branch["id"],
            "name": "Book a Tour",
            "descriptionHtml": "<p>Halo</p><script>alert(1)</script>",
        },
    )

    assert created.status_code == 201
    assert created.json()["data"]["descriptionHtml"] == "<p>Halo</p>"


def test_list_events_carries_the_branch_name_for_the_branch_column(api) -> None:
    branch = _branch(api)
    _event(api, branch["id"])

    listed = api.client.get("/api/v1/admin/events")

    assert listed.status_code == 200
    row = listed.json()["items"][0]
    assert row["branchName"] == "7Magic Jakarta"
    assert row["registrationCount"] == 0


def test_events_can_be_filtered_by_branch(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _event(api, first["id"], name="Tour Jakarta")
    _event(api, second["id"], name="Tour Bali")

    listed = api.client.get(f"/api/v1/admin/events?branchId={second['id']}")

    assert [row["name"] for row in listed.json()["items"]] == ["Tour Bali"]


def test_a_branch_scoped_user_sees_only_its_events(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")
    _event(api, first["id"], name="Tour Jakarta")
    _event(api, second["id"], name="Tour Bali")

    api.login(
        admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", second["id"]),))
    )
    listed = api.client.get("/api/v1/admin/events")

    assert [row["name"] for row in listed.json()["items"]] == ["Tour Bali"]


def test_a_branch_scoped_user_cannot_create_an_event_for_another_branch(api) -> None:
    first = _branch(api)
    second = _branch(api, slug="bali", name="7Magic Bali")

    api.login(
        admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", second["id"]),))
    )
    response = api.client.post(
        "/api/v1/admin/events", json={"branchId": first["id"], "name": "Sneaky"}
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "branch_forbidden"


def test_a_branch_scoped_user_cannot_create_an_all_branch_event(api) -> None:
    branch = _branch(api)

    api.login(
        admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", branch["id"]),))
    )
    response = api.client.post(
        "/api/v1/admin/events", json={"branchId": None, "name": "Company-wide"}
    )

    assert response.status_code == 403


def test_email_templates_fall_back_to_the_defaults(api) -> None:
    event = _event(api, _branch(api)["id"])

    response = api.client.get(f"/api/v1/admin/events/{event['id']}/email-templates")

    assert response.status_code == 200
    body = response.json()["data"]
    assert [row["kind"] for row in body["templates"]] == ["thank_you", "no_show", "cancel"]
    assert body["templates"][0]["enabled"] is False
    assert "first_name" in body["placeholders"]


def test_saving_then_previewing_a_template_substitutes_placeholders(api) -> None:
    event = _event(api, _branch(api)["id"])

    saved = api.client.put(
        f"/api/v1/admin/events/{event['id']}/email-templates/thank_you",
        json={"subject": "Terima kasih", "body": "Halo {first_name}", "enabled": True},
    )
    preview = api.client.post(
        f"/api/v1/admin/events/{event['id']}/email-templates/thank_you/preview",
        json={"subject": "Terima kasih", "body": "Halo {first_name}", "enabled": True},
    )

    assert saved.status_code == 200
    assert saved.json()["data"]["enabled"] is True
    assert preview.json()["data"]["body"] == "Halo "  # no registrations yet
