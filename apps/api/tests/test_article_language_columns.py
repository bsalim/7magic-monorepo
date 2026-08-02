"""Article translations as columns rather than sibling rows.

Two languages only, so a second row per article carried more machinery than it
earned: its own slug, status and publish date all had to be kept in step. The
English text now lives beside the Indonesian on the same row, and an empty
English field falls back to Indonesian exactly as before.
"""

from __future__ import annotations

from app.models import Article


def test_article_has_a_column_per_language() -> None:
    columns = set(Article.__table__.columns.keys())

    assert {"title_id", "title_en"} <= columns
    assert {"summary_id", "summary_en"} <= columns
    assert {"body_id", "body_en"} <= columns


def test_sibling_row_machinery_is_gone() -> None:
    """locale and translation_group_id only existed to link sibling rows."""
    columns = set(Article.__table__.columns.keys())

    assert "locale" not in columns
    assert "translation_group_id" not in columns


def test_slug_and_status_stay_shared() -> None:
    """One row means one URL slug and one publish state for both languages."""
    columns = set(Article.__table__.columns.keys())

    assert "slug" in columns
    assert "status" in columns
    assert "slug_en" not in columns
    assert "status_en" not in columns
