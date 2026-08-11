"""open the seeded branches for tour bookings

Revision ID: 3c88ae63f480
Revises: 35b76812b769
Create Date: 2026-08-11 22:31:44.108225

Gives Jakarta, Singapore and Bali a standard week of opening hours and switches
`bookable` on, so all three take tour bookings instead of arriving switched off
as `35b76812b769` left them.

The hours are a default, not researched fact -- nothing in this repo publishes
7Magic's real visiting hours. See `_OPENS_AT` / `_CLOSES_AT` / `_OPEN_DAYS` below:
changing them here only affects branches that have no hours yet, so once a branch
is live the CMS is the place to edit it.

Times are local wall-clock per branch, which is what `opens_at_local` means: 10:00
is 10:00 in Jakarta, in Singapore and in Bali, not one instant shared by all three.
"""

from datetime import UTC, datetime, time

import sqlalchemy as sa
from alembic import op

revision = "3c88ae63f480"
down_revision = "35b76812b769"
branch_labels = None
depends_on = None


_SLUGS = ("jakarta", "singapore", "bali")

# Monday to Saturday, ISO numbering. Sunday is left closed to match a normal
# Indonesian office week -- worth revisiting, since Sunday is precisely when
# couples are free to visit, but that is a business call rather than a default.
_OPEN_DAYS = (1, 2, 3, 4, 5, 6)
_OPENS_AT = time(10, 0)
_CLOSES_AT = time(18, 0)

_branches = sa.table(
    "branches",
    sa.column("id", sa.Integer),
    sa.column("slug", sa.String),
    sa.column("bookable", sa.Boolean),
)

_opening_hours = sa.table(
    "branch_opening_hours",
    sa.column("id", sa.Integer),
    sa.column("branch_id", sa.Integer),
    sa.column("day_of_week", sa.Integer),
    sa.column("opens_at_local", sa.Time),
    sa.column("closes_at_local", sa.Time),
    sa.column("active", sa.Boolean),
    sa.column("sort_order", sa.Integer),
    sa.column("created_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    connection = op.get_bind()
    # Explicit rather than left to the server default: SQLite accepts DEFAULT
    # now() in the CREATE TABLE but has no now() to evaluate on INSERT.
    seeded_at = datetime.now(UTC)

    for slug in _SLUGS:
        branch_id = connection.execute(
            sa.select(_branches.c.id).where(_branches.c.slug == slug)
        ).scalar_one_or_none()
        if branch_id is None:
            continue

        # Only ever fills a gap. A branch whose hours someone has already set --
        # or deliberately cleared -- is left exactly as it is, so re-running this
        # cannot overwrite a real schedule with the default one.
        already_set = connection.execute(
            sa.select(sa.func.count())
            .select_from(_opening_hours)
            .where(_opening_hours.c.branch_id == branch_id)
        ).scalar_one()
        if already_set:
            continue

        connection.execute(
            _opening_hours.insert(),
            [
                {
                    "branch_id": branch_id,
                    "day_of_week": day,
                    "opens_at_local": _OPENS_AT,
                    "closes_at_local": _CLOSES_AT,
                    "active": True,
                    "sort_order": day,
                    "created_at": seeded_at,
                }
                for day in _OPEN_DAYS
            ],
        )
        # Now that it has hours it can honour a booking, so it may be advertised.
        connection.execute(
            _branches.update().where(_branches.c.id == branch_id).values(bookable=True)
        )


def downgrade() -> None:
    connection = op.get_bind()
    branch_ids = connection.execute(
        sa.select(_branches.c.id).where(_branches.c.slug.in_(_SLUGS))
    ).scalars().all()
    if not branch_ids:
        return

    connection.execute(
        _opening_hours.delete().where(_opening_hours.c.branch_id.in_(branch_ids))
    )
    # Back to unbookable, matching the state 35b76812b769 leaves them in: with the
    # hours gone they would refuse every date anyway.
    connection.execute(
        _branches.update().where(_branches.c.id.in_(branch_ids)).values(bookable=False)
    )
