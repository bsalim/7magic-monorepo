"""tour registration venue name and city

Revision ID: 98340a4dd7ce
Revises: 12a105423ba9
Create Date: 2026-08-13 10:28:48.541460
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "98340a4dd7ce"
down_revision = "12a105423ba9"
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
