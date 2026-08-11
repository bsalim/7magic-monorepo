from __future__ import annotations

from tests.conftest import admin_user


def _create_branch(api, slug="jakarta-pusat", name="7Magic Jakarta Pusat"):
    return api.client.post(
        "/api/v1/admin/branches",
        json={
            "slug": slug,
            "name": name,
            "address_line1": "Jl. Thamrin No. 1",
            "city": "jakarta",
            "country_code": "ID",
            "timezone": "Asia/Jakarta",
        },
    )


def test_create_and_list_branches(api) -> None:
    created = _create_branch(api)

    assert created.status_code == 201
    body = created.json()["data"]
    assert body["slug"] == "jakarta-pusat"
    assert body["is_default"] is True
    assert body["settings"]["tour_notification_recipients"] == []

    listed = api.client.get("/api/v1/admin/branches")
    assert listed.status_code == 200
    assert [row["slug"] for row in listed.json()["items"]] == ["jakarta-pusat"]


def test_duplicate_slug_returns_409(api) -> None:
    _create_branch(api)

    conflicted = _create_branch(api, name="Duplicate")

    assert conflicted.status_code == 409
    assert conflicted.json()["error"]["code"] == "branch_slug_conflict"


def test_branch_scoped_user_sees_only_its_branch(api) -> None:
    first = _create_branch(api).json()["data"]
    _create_branch(api, slug="bali", name="7Magic Bali")

    api.login(
        admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", first["id"]),))
    )
    listed = api.client.get("/api/v1/admin/branches")

    assert [row["slug"] for row in listed.json()["items"]] == ["jakarta-pusat"]


def test_branch_scoped_user_cannot_edit_another_branch(api) -> None:
    first = _create_branch(api).json()["data"]
    other = _create_branch(api, slug="bali", name="7Magic Bali").json()["data"]

    api.login(
        admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", first["id"]),))
    )
    response = api.client.patch(f"/api/v1/admin/branches/{other['id']}", json={"name": "Hijacked"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "branch_forbidden"


def test_branch_staff_cannot_edit_branch_settings(api) -> None:
    branch = _create_branch(api).json()["data"]

    api.login(admin_user(roles=["branch_staff"], branch_grants=(("branch_staff", branch["id"]),)))
    response = api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/settings",
        json={"tour_notification_recipients": ["nope@7magic.test"]},
    )

    assert response.status_code == 403


def test_opening_hours_replace_the_whole_week(api) -> None:
    branch = _create_branch(api).json()["data"]

    api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={"items": [{"day_of_week": 1, "opens_at_local": "10:00:00", "closes_at_local": "18:00:00"}]},
    )
    second = api.client.put(
        f"/api/v1/admin/branches/{branch['id']}/opening-hours",
        json={"items": [{"day_of_week": 2, "opens_at_local": "11:00:00", "closes_at_local": "19:00:00"}]},
    )

    assert second.status_code == 200
    assert [row["day_of_week"] for row in second.json()["data"]["opening_hours"]] == [2]
