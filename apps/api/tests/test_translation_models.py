from __future__ import annotations

from app.models import VenueTranslation


def test_venue_translation_table_shape() -> None:
    table = VenueTranslation.__table__
    assert table.name == "venue_translations"
    assert {"id", "venue_id", "locale", "description", "packages"} <= set(table.columns.keys())

    unique_cols = [
        tuple(sorted(column.name for column in constraint.columns))
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]
    assert ("locale", "venue_id") in unique_cols


def test_venue_translation_cascades_from_venue() -> None:
    venue_fk = next(iter(VenueTranslation.__table__.c.venue_id.foreign_keys))
    assert venue_fk.column.table.name == "venues"
    assert venue_fk.ondelete == "CASCADE"



