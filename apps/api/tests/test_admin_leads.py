"""CMS leads: GET /api/v1/admin/leads and /admin/leads.csv.

Leads are not branch data and they hold personal details, so both routes need an
org-wide `lead:read` grant; a branch-scoped one is not enough.
"""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

from app.api.v1.dependencies import require_admin_user
from app.domains.branches.access import ALL_PERMISSIONS, LEAD_READ, ROLE_PERMISSIONS
from app.main import app
from app.models import ContactLead
from tests.conftest import admin_user

LIST = "/api/v1/admin/leads"
CSV = "/api/v1/admin/leads.csv"


def _seed_leads(api) -> None:
    async def seed(session) -> None:
        session.add_all(
            [
                ContactLead(
                    full_name="Ayu Santoso",
                    email="ayu@example.com",
                    mobile="+628123456789",
                    message="Mau tanya paket ballroom.",
                    source="contact_form",
                    metadata_json={"source_path": "/contact"},
                    created_at=datetime(2026, 10, 5, 3, 0, tzinfo=UTC),
                ),
                ContactLead(
                    full_name="Budi Hartono",
                    email="budi@example.com",
                    mobile="+628999888777",
                    message="Venue pricing request for Hotel Mulia.",
                    source="venue_pricing",
                    metadata_json={"venue_slug": "hotel-mulia"},
                    created_at=datetime(2026, 10, 10, 3, 0, tzinfo=UTC),
                ),
                ContactLead(
                    full_name="Andre & Amanda",
                    email="andre@example.com",
                    mobile="+6281234567890",
                    source="tool_mahar",
                    metadata_json={
                        "source_path": "/wedding-tools/mahar-tanggal-pernikahan",
                        "tool": "mahar",
                        "inputs": {"amount": 20092026},
                    },
                    created_at=datetime(2026, 10, 15, 3, 0, tzinfo=UTC),
                ),
            ]
        )

    api.seed(seed)


def _names(response) -> list[str]:
    return [row["full_name"] for row in response.json()["items"]]


def test_lead_read_is_a_known_permission_branch_staff_lack() -> None:
    assert LEAD_READ in ALL_PERMISSIONS
    assert LEAD_READ not in ROLE_PERMISSIONS["branch_staff"]


def test_an_org_wide_admin_lists_leads_newest_first(api) -> None:
    _seed_leads(api)

    response = api.client.get(LIST)

    assert response.status_code == 200
    assert _names(response) == ["Andre & Amanda", "Budi Hartono", "Ayu Santoso"]
    first = response.json()["items"][0]
    assert first["source"] == "tool_mahar"
    assert first["email"] == "andre@example.com"
    assert first["mobile"] == "+6281234567890"
    assert first["source_path"] == "/wedding-tools/mahar-tanggal-pernikahan"
    assert first["metadata"]["inputs"]["amount"] == 20092026
    assert response.json()["pagination"] == {
        "page": 1,
        "page_size": 50,
        "total": 3,
        "total_pages": 1,
    }


def test_a_branch_scoped_grant_is_not_enough(api) -> None:
    """branch_manager carries lead:read, but only for its branch -- and leads are
    not branch data."""
    _seed_leads(api)
    api.login(admin_user(roles=["branch_manager"], branch_grants=(("branch_manager", 7),)))

    assert api.client.get(LIST).status_code == 403
    assert api.client.get(CSV).status_code == 403


def test_an_org_wide_role_without_lead_read_is_refused(api) -> None:
    api.login(admin_user(roles=["branch_staff"], branch_grants=(("branch_staff", None),)))

    assert api.client.get(LIST).status_code == 403
    assert api.client.get(CSV).status_code == 403


def test_an_anonymous_caller_is_refused(api) -> None:
    app.dependency_overrides.pop(require_admin_user)

    assert api.client.get(LIST).status_code == 401
    assert api.client.get(CSV).status_code == 401


def test_the_source_filter_matches_exactly(api) -> None:
    _seed_leads(api)

    assert _names(api.client.get(LIST, params={"source": "tool_mahar"})) == ["Andre & Amanda"]
    assert _names(api.client.get(LIST, params={"source": "venue_pricing"})) == ["Budi Hartono"]


def test_search_reads_name_email_phone_and_message(api) -> None:
    _seed_leads(api)

    assert _names(api.client.get(LIST, params={"q": "AYU"})) == ["Ayu Santoso"]
    assert _names(api.client.get(LIST, params={"q": "budi@"})) == ["Budi Hartono"]
    assert _names(api.client.get(LIST, params={"q": "1234567890"})) == ["Andre & Amanda"]
    assert _names(api.client.get(LIST, params={"q": "ballroom"})) == ["Ayu Santoso"]


def test_the_date_range_includes_both_end_days(api) -> None:
    _seed_leads(api)

    response = api.client.get(LIST, params={"date_from": "2026-10-10", "date_to": "2026-10-15"})

    assert _names(response) == ["Andre & Amanda", "Budi Hartono"]


def test_the_date_range_reads_days_in_jakarta_time(api) -> None:
    """18:00 UTC on the 9th is 01:00 on the 10th in Jakarta, which is the day the
    team saw the lead arrive."""

    async def seed(session) -> None:
        session.add(
            ContactLead(
                full_name="Late Night",
                source="contact_form",
                created_at=datetime(2026, 10, 9, 18, 0, tzinfo=UTC),
            )
        )

    api.seed(seed)

    on_the_tenth = api.client.get(LIST, params={"date_from": "2026-10-10", "date_to": "2026-10-10"})
    on_the_ninth = api.client.get(LIST, params={"date_from": "2026-10-09", "date_to": "2026-10-09"})

    assert _names(on_the_tenth) == ["Late Night"]
    assert _names(on_the_ninth) == []


def test_pages_hold_fifty_leads(api) -> None:
    async def seed(session) -> None:
        session.add_all(
            [
                ContactLead(
                    full_name=f"Lead {index:02d}",
                    source="contact_form",
                    created_at=datetime(2026, 10, 1, 0, index, tzinfo=UTC),
                )
                for index in range(55)
            ]
        )

    api.seed(seed)

    first = api.client.get(LIST).json()
    second = api.client.get(LIST, params={"page": 2}).json()

    assert len(first["items"]) == 50
    assert first["items"][0]["full_name"] == "Lead 54"
    assert [row["full_name"] for row in second["items"]] == [
        f"Lead {index:02d}" for index in range(4, -1, -1)
    ]
    assert second["pagination"]["total"] == 55
    assert second["pagination"]["total_pages"] == 2


def test_the_csv_export_applies_the_same_filters(api) -> None:
    _seed_leads(api)

    response = api.client.get(CSV, params={"source": "tool_mahar"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    rows = list(csv.reader(io.StringIO(response.text)))
    assert rows[0] == ["Date", "Source", "Name", "Email", "Phone", "Page", "Message", "Details"]
    assert len(rows) == 2
    # By header name, not a fixed index: inserting a column ahead of it should fail
    # on the header assertion above, not silently here.
    assert rows[1][rows[0].index("Email")] == "andre@example.com"
    assert "20092026" in rows[1][rows[0].index("Details")]


def test_the_csv_export_defuses_spreadsheet_formulas(api) -> None:
    async def seed(session) -> None:
        session.add(
            ContactLead(
                full_name='=HYPERLINK("http://evil.example","klik")',
                email="@evil.example",
                mobile="-1+1",
                message="+cmd",
                source="contact_form",
                metadata_json={"source_path": "/contact"},
            )
        )

    api.seed(seed)

    rows = list(csv.reader(io.StringIO(api.client.get(CSV).text)))
    row = dict(zip(rows[0], rows[1], strict=True))
    assert row["Name"].startswith("'=")
    assert row["Email"] == "'@evil.example"
    assert row["Phone"] == "'-1+1"
    assert row["Message"] == "'+cmd"


def test_the_csv_export_leaves_normalised_phones_alone(api) -> None:
    _seed_leads(api)

    rows = list(csv.reader(io.StringIO(api.client.get(CSV, params={"source": "tool_mahar"}).text)))
    assert rows[1][rows[0].index("Phone")] == "+6281234567890"
