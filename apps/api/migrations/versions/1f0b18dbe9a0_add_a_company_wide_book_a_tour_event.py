"""add a Book a Tour event for each branch

Revision ID: 1f0b18dbe9a0
Revises: 3c88ae63f480
Create Date: 2026-08-12 08:14:03.552118

A branch needs three things to take a tour booking: active, bookable, and an
*event* open for it. The previous two migrations gave every branch the first two;
without this one they still answer "this branch is not taking visit bookings right
now", because registrations hang off an event and there was none.

One event per branch rather than a single company-wide one (`branch_id` NULL),
even though the service supports that. A registration's branch is read through
`registration.event.branch_id`, so a company-wide event would leave every booking
with no branch: the CMS branch column blank, the CSV branch column empty, and --
worst -- branch-scoped staff unable to see their own branch's bookings, since that
list filters on `Event.branch_id`. Per-branch events keep all three working, and
capacity, registration windows and email templates are per-branch concerns anyway.

Every window column stays NULL, so `registration_block` finds nothing to refuse
and the event is permanently open, which is what a standing offer wants.
"""

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "1f0b18dbe9a0"
down_revision = "3c88ae63f480"
branch_labels = None
depends_on = None


_EVENT_NAME = "Book a Tour"
_SLUGS = ("jakarta", "singapore", "bali")

_branches = sa.table(
    "branches",
    sa.column("id", sa.Integer),
    sa.column("slug", sa.String),
)

_events = sa.table(
    "events",
    sa.column("id", sa.Integer),
    sa.column("public_id", sa.Uuid),
    sa.column("branch_id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("description_html", sa.Text),
    sa.column("is_active", sa.Boolean),
    sa.column("deleted_at", sa.DateTime(timezone=True)),
    sa.column("created_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    connection = op.get_bind()
    seeded_at = datetime.now(UTC)

    for slug in _SLUGS:
        branch_id = connection.execute(
            sa.select(_branches.c.id).where(_branches.c.slug == slug)
        ).scalar_one_or_none()
        if branch_id is None:
            continue

        # Idempotent per branch: re-running must not leave two, and a branch whose
        # event someone already made keeps theirs. A soft-deleted one does not
        # count -- the service skips it, so letting it stand in would keep the
        # branch unbookable.
        existing = connection.execute(
            sa.select(_events.c.id).where(
                _events.c.branch_id == branch_id,
                _events.c.name == _EVENT_NAME,
                _events.c.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue

        connection.execute(
            _events.insert().values(
                public_id=uuid.uuid4(),
                branch_id=branch_id,
                name=_EVENT_NAME,
                description_html="",
                is_active=True,
                # Explicit: SQLite accepts DEFAULT now() in the CREATE TABLE but
                # has no now() to evaluate on INSERT.
                created_at=seeded_at,
            )
        )


def downgrade() -> None:
    connection = op.get_bind()
    branch_ids = (
        connection.execute(sa.select(_branches.c.id).where(_branches.c.slug.in_(_SLUGS)))
        .scalars()
        .all()
    )
    if not branch_ids:
        return
    # Registrations against these events go with them, via ON DELETE CASCADE.
    connection.execute(
        _events.delete().where(
            _events.c.branch_id.in_(branch_ids), _events.c.name == _EVENT_NAME
        )
    )
