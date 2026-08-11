from __future__ import annotations

from app.domains.events.sanitize import sanitize_html


def test_allowed_formatting_survives() -> None:
    assert sanitize_html("<p>Halo <strong>calon pengantin</strong></p>") == (
        "<p>Halo <strong>calon pengantin</strong></p>"
    )


def test_script_tags_are_removed_with_their_contents() -> None:
    assert sanitize_html("<p>Halo</p><script>alert(1)</script>") == "<p>Halo</p>"


def test_event_handlers_are_stripped_from_allowed_tags() -> None:
    assert sanitize_html('<p onclick="steal()">Halo</p>') == "<p>Halo</p>"


def test_javascript_hrefs_are_dropped() -> None:
    assert sanitize_html('<a href="javascript:alert(1)">klik</a>') == "<a>klik</a>"


def test_https_hrefs_are_kept() -> None:
    assert (
        sanitize_html('<a href="https://7magic.id">klik</a>')
        == '<a href="https://7magic.id">klik</a>'
    )


def test_none_becomes_an_empty_string() -> None:
    assert sanitize_html(None) == ""
