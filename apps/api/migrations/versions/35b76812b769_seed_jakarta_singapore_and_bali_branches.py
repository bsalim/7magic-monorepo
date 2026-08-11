"""seed jakarta singapore and bali branches

Revision ID: 35b76812b769
Revises: c3683869fcd8
Create Date: 2026-08-11 14:58:12.331904

Seeds the three real 7Magic locations so production has them without anyone
typing them in.

Written as an upsert keyed on slug rather than a plain insert. `c3683869fcd8`
already creates a `jakarta` row, so a blind insert would hit the unique slug
constraint and abort the deploy halfway through; this fills that row in instead,
and is safe to re-run.

On the update path the address and contact fields below are treated as the source
of truth and overwritten. Alembic's version table means that only ever applies to
`jakarta` on a normal deploy; it matters only if someone stamps backwards, where
restoring the known-good values is the wanted outcome anyway.

Addresses and postal codes match the offices published in
`apps/web/src/lib/components/PublicFooter.svelte`; the contact details match
`apps/web/src/lib/whatsapp.ts` and the site's Organization schema. No opening
hours are seeded -- those are business data nobody should guess, and their
absence is why every branch lands with `bookable = false`. See the note on
`_BOOKABLE_ON_INSERT` below.
"""

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "35b76812b769"
down_revision = "c3683869fcd8"
branch_labels = None
depends_on = None


# A branch with no opening hours refuses every date, so listing one on /tour
# would hand guests a form that always says "we are closed". Every branch
# therefore arrives with bookable = false; the team sets its hours in the CMS and
# then ticks "Takes visits".
#
# The same rule is re-applied to rows that already exist -- `jakarta` is created
# by c3683869fcd8 with bookable = true and no hours, which is exactly the trap.
# It is only ever forced *off*, and only while a branch has no hours, so this
# never re-disables a branch someone has since configured and switched on.
_BOOKABLE_ON_INSERT = False

# The shared enquiry line. Per-branch numbers can be set in the CMS later; the
# only other phone number in the repo is a placeholder, so no public_phone here.
_PUBLIC_EMAIL = "hello@7magic.id"
_WHATSAPP = "+6289628614447"

BRANCHES = [
    {
        "slug": "jakarta",
        "name": "7Magic Jakarta",
        "address_line1": "Jalan Gajah Mada No. 10",
        "address_line2": None,
        "city": "jakarta",
        "postal_code": "10130",
        "country_code": "ID",
        "timezone": "Asia/Jakarta",
    },
    {
        "slug": "singapore",
        "name": "7Magic Singapore",
        "address_line1": "110 Pasir Ris Street 11",
        "address_line2": None,
        "city": "singapore",
        "postal_code": "510110",
        # Not ID: the column defaults to Indonesia and this is the one branch
        # that is not there.
        "country_code": "SG",
        "timezone": "Asia/Singapore",
    },
    {
        "slug": "bali",
        "name": "7Magic Bali",
        "address_line1": "Sunday Arshika Hotel - Lobby, Sunset Road Kuta - Bali",
        "address_line2": None,
        "city": "bali",
        "postal_code": "80612",
        "country_code": "ID",
        # WITA, an hour ahead of Jakarta -- a tour slot rendered in the wrong
        # zone is an hour early or late at the door.
        "timezone": "Asia/Makassar",
    },
]

# Added by this migration, so safe for downgrade to remove. `jakarta` predates
# it and is left alone.
_ADDED_SLUGS = ("singapore", "bali")

_branches = sa.table(
    "branches",
    sa.column("id", sa.Integer),
    sa.column("public_id", sa.Uuid),
    sa.column("slug", sa.String),
    sa.column("name", sa.String),
    sa.column("address_line1", sa.String),
    sa.column("address_line2", sa.String),
    sa.column("city", sa.String),
    sa.column("postal_code", sa.String),
    sa.column("country_code", sa.String),
    sa.column("timezone", sa.String),
    sa.column("public_email", sa.String),
    sa.column("whatsapp_number", sa.String),
    sa.column("active", sa.Boolean),
    sa.column("bookable", sa.Boolean),
    sa.column("is_default", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
)

_opening_hours = sa.table(
    "branch_opening_hours",
    sa.column("id", sa.Integer),
    sa.column("branch_id", sa.Integer),
)

_branch_settings = sa.table(
    "branch_settings",
    sa.column("id", sa.Integer),
    sa.column("branch_id", sa.Integer),
    sa.column("tour_notification_recipients", sa.JSON),
    sa.column("created_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    connection = op.get_bind()
    # Passed explicitly rather than left to the server default: SQLite accepts
    # DEFAULT now() in the CREATE TABLE but has no now() to evaluate on INSERT.
    seeded_at = datetime.now(UTC)

    for branch in BRANCHES:
        shared = {
            **branch,
            "public_email": _PUBLIC_EMAIL,
            "whatsapp_number": _WHATSAPP,
        }

        branch_id = connection.execute(
            sa.select(_branches.c.id).where(_branches.c.slug == branch["slug"])
        ).scalar_one_or_none()

        if branch_id is None:
            connection.execute(
                _branches.insert().values(
                    **shared,
                    public_id=uuid.uuid4(),
                    active=True,
                    bookable=_BOOKABLE_ON_INSERT,
                    # The single-default invariant lives in branch_service, so
                    # this migration never promotes a second one.
                    is_default=branch["slug"] == "jakarta",
                    created_at=seeded_at,
                )
            )
            branch_id = connection.execute(
                sa.select(_branches.c.id).where(_branches.c.slug == branch["slug"])
            ).scalar_one()
        else:
            changes = {key: value for key, value in shared.items() if key != "slug"}
            # active and is_default are left alone -- by the time this re-runs they
            # may reflect a decision someone made in the CMS. bookable is forced
            # off only while the branch has no hours, for the reason above.
            has_hours = (
                connection.execute(
                    sa.select(sa.func.count())
                    .select_from(_opening_hours)
                    .where(_opening_hours.c.branch_id == branch_id)
                ).scalar_one()
                > 0
            )
            if not has_hours:
                changes["bookable"] = False
            connection.execute(
                _branches.update().where(_branches.c.id == branch_id).values(**changes)
            )

        has_settings = connection.execute(
            sa.select(_branch_settings.c.id).where(_branch_settings.c.branch_id == branch_id)
        ).scalar_one_or_none()
        if has_settings is None:
            connection.execute(
                _branch_settings.insert().values(
                    branch_id=branch_id,
                    tour_notification_recipients=[],
                    created_at=seeded_at,
                )
            )


def downgrade() -> None:
    connection = op.get_bind()
    # branch_settings goes with it via ON DELETE CASCADE; any event still
    # pointing at one of these becomes company-wide via ON DELETE SET NULL.
    connection.execute(_branches.delete().where(_branches.c.slug.in_(_ADDED_SLUGS)))
