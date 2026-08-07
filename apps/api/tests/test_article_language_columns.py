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


def test_status_stays_shared_but_the_slug_does_not() -> None:
    """One row still means one publish state, but two URLs.

    The slug used to be shared along with the status. It is not any more: an
    English article reading well at an Indonesian URL was costing search traffic,
    so `slug_en` carries the English URL while `status` stays single -- an
    article is published in both languages or neither.
    """
    columns = set(Article.__table__.columns.keys())

    assert {"slug", "slug_en"} <= columns
    assert "status" in columns
    assert "status_en" not in columns


def test_english_slug_falls_back_to_the_indonesian_one() -> None:
    """A null slug_en is a URL that is simply shared, not a broken one."""
    article = Article(slug="harga-catering", slug_en="wedding-catering-prices")
    untranslated = Article(slug="harga-catering")

    assert article.slug_for("en") == "wedding-catering-prices"
    assert article.slug_for("id") == "harga-catering"
    assert untranslated.slug_for("en") == "harga-catering"
