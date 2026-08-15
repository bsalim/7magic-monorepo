"""The shared email shell.

Email clients are not browsers: Outlook renders through Word, Gmail strips
`<style>` blocks, and a large share of clients block remote images by default.
The tests that matter are the ones pinning escaping -- template text and
guest-supplied names both arrive here untrusted -- and the images-off fallback.
"""

from __future__ import annotations

from app.services.email.layout import (
    OFFICES,
    paragraphs,
    render_email,
    render_lead_email,
)


# --- Escaping -----------------------------------------------------------------


def test_paragraphs_escapes_before_it_structures() -> None:
    """A guest named <script> must not become markup. Escaping first is the whole
    safety argument, since template text and guest input both land here."""
    result = paragraphs("<script>alert(1)</script>")

    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_a_detail_value_containing_markup_is_inert() -> None:
    """Escaping runs before the detail pattern, so a crafted value cannot break
    out through the emphasis it gets wrapped in."""
    result = paragraphs("Venue: <img src=x onerror=alert(1)>")

    assert "<img" not in result
    assert "&lt;img" in result


def test_paragraphs_escapes_ampersands() -> None:
    assert "Dina &amp; Rangga" in paragraphs("Dina & Rangga")


# --- Structure ----------------------------------------------------------------


def test_blank_lines_become_separate_paragraphs() -> None:
    result = paragraphs("Halo Dina,\n\nTur Anda dikonfirmasi.")

    assert result.count("<p ") == 2


def test_single_newlines_become_line_breaks() -> None:
    result = paragraphs("Venue: Jakarta\nTanggal: 17 Mei 2026")

    assert result.count("<p ") == 1
    assert "<br />" in result


def test_blank_text_produces_nothing() -> None:
    assert paragraphs("") == ""


def test_an_unknown_placeholder_survives_rendering() -> None:
    """domains/events/emails.py renders unknown tokens literally rather than
    raising mid-send; the layout must not undo that."""
    assert "{unknown_token}" in paragraphs("Hi {unknown_token}")


# --- Emphasis on detail lines -------------------------------------------------
# "Venue: The Ritz-Carlton" carries one thing the reader is scanning for, and it
# is not the word "Venue".


def test_a_detail_value_is_emphasised() -> None:
    result = paragraphs("Venue: The Ritz-Carlton Pacific Place")

    assert "<strong" in result
    assert "The Ritz-Carlton Pacific Place</strong>" in result


def test_the_label_is_not_emphasised() -> None:
    result = paragraphs("Tanggal: 17 Mei 2026")

    assert "<strong" in result
    assert "Tanggal:</strong>" not in result


def test_every_line_of_a_booking_block_is_emphasised() -> None:
    result = paragraphs(
        "Venue: The Ritz-Carlton Pacific Place\n"
        "Alamat: Jl. Jend. Sudirman Kav. 52-53, Kebayoran Baru, Jakarta\n"
        "Tanggal: 17 Mei 2026\n"
        "Jumlah tamu: 2"
    )

    assert result.count("<strong") == 4


def test_ordinary_prose_is_left_alone() -> None:
    """The rule must not fire on a greeting or a sentence."""
    assert "<strong" not in paragraphs("Halo Dina,")
    assert "<strong" not in paragraphs("Kami sudah menerima booking Anda untuk Venue Tour.")


def test_a_sentence_containing_a_colon_is_left_alone() -> None:
    """The label is bounded to a short run without sentence punctuation, so prose
    that happens to contain a colon does not get half of itself bolded."""
    text = "Kami tunggu kabarnya. Satu hal: silakan balas email ini kapan saja."

    assert "<strong" not in paragraphs(text)


def test_a_colon_with_no_value_after_it_is_left_alone() -> None:
    assert "<strong" not in paragraphs("Catatan:")


# --- The shell ----------------------------------------------------------------


def test_the_wordmark_renders_when_no_logo_is_configured() -> None:
    """Blank is also what a reader with images blocked effectively sees."""
    result = render_email(heading="Booking confirmed", body_html="<p>Hi</p>", logo_url="")

    assert "7MAGIC" in result
    assert "<img" not in result


def test_a_configured_logo_renders_as_an_image_with_alt_text() -> None:
    result = render_email(
        heading="Booking confirmed",
        body_html="<p>Hi</p>",
        logo_url="https://media.7magicwedding.com/email/7magic-logo.png",
    )

    assert 'src="https://media.7magicwedding.com/email/7magic-logo.png"' in result
    assert 'alt="7Magic Wedding"' in result


def test_the_body_is_placed_inside_the_shell() -> None:
    result = render_email(heading="Booking confirmed", body_html="<p>Hello Dina</p>", logo_url="")

    assert "<p>Hello Dina</p>" in result


def test_the_heading_is_escaped() -> None:
    result = render_email(heading="Dina & Rangga", body_html="<p>x</p>", logo_url="")

    assert "Dina &amp; Rangga" in result


def test_the_layout_uses_tables_for_structure() -> None:
    """A div-and-flexbox layout collapses in Outlook, which renders through Word."""
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="")

    assert "<table" in result


def test_the_layout_carries_no_style_block() -> None:
    """Gmail strips them, so every rule has to be inline to survive."""
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="")

    assert "<style" not in result


def test_a_preheader_is_present_but_hidden() -> None:
    """The line clients show beside the subject. Unset, they scrape whatever text
    comes first, which is usually the logo alt text."""
    result = render_email(
        heading="Hi", body_html="<p>x</p>", preheader="Your tour is confirmed", logo_url=""
    )

    assert "Your tour is confirmed" in result
    assert "display:none" in result


# --- The footer ---------------------------------------------------------------


def test_the_footer_names_the_company() -> None:
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="")

    assert "7Magic Wedding Planner" in result


def test_the_footer_is_left_aligned() -> None:
    """The name was briefly centred over left-aligned addresses, which read as
    two blocks laid out separately."""
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="")

    assert "text-align:center" not in result


def test_the_offices_sit_under_a_heading() -> None:
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="", locale="en")

    assert "Office address" in result


def test_the_office_heading_follows_the_guests_language() -> None:
    """An Indonesian confirmation must not carry an English heading."""
    indonesian = render_email(heading="Hi", body_html="<p>x</p>", logo_url="", locale="id")
    english = render_email(heading="Hi", body_html="<p>x</p>", logo_url="", locale="en")

    assert "Alamat kantor" in indonesian
    assert "Office address" not in indonesian
    assert "Office address" in english


def test_an_absent_or_unknown_locale_falls_back_to_indonesian() -> None:
    """Same rule the confirmation body follows, so the two cannot disagree."""
    for locale in (None, "", "klingon"):
        assert "Alamat kantor" in render_email(
            heading="Hi", body_html="<p>x</p>", logo_url="", locale=locale
        )


def test_a_region_tagged_locale_reaches_the_footer() -> None:
    """The shell used a bare dict lookup while the body stripped the region tag,
    so an `en-GB` guest got an English confirmation in an Indonesian footer."""
    for locale in ("en-GB", "en_US", "EN"):
        result = render_email(
            heading="Hi", body_html="<p>x</p>", logo_url="", locale=locale
        )
        assert "Office address" in result, locale
        assert "Alamat kantor" not in result, locale


def test_the_footer_lists_every_office() -> None:
    """A transactional email that names a real, findable business reads as one."""
    result = render_email(heading="Hi", body_html="<p>x</p>", logo_url="")

    for city, address in OFFICES:
        assert city in result
        assert address in result


def test_the_offices_match_what_the_site_publishes() -> None:
    """Pinned so a change here is deliberate: these are copied from the public
    site's footer, and the two must not drift apart."""
    assert OFFICES == (
        ("Jakarta", "Jalan Gajah Mada No. 10, Jakarta, Indonesia 10130"),
        (
            "Bali",
            "Sunday Arshika Hotel - Lobby, Sunset Road Kuta - Bali, Bali, 80612, Indonesia",
        ),
        ("Singapore", "110 Pasir Ris Street 11, Singapore 510110"),
    )


# --- The lead notification ----------------------------------------------------


def test_lead_email_still_renders_its_fields() -> None:
    """Unchanged contract: leads.py passes a dict and expects a table."""
    result = render_lead_email(heading="New enquiry", fields={"Name": "Dina"})

    assert "Dina" in result
    assert "New enquiry" in result


def test_lead_email_skips_blank_fields() -> None:
    result = render_lead_email(heading="New enquiry", fields={"Name": "Dina", "City": ""})

    assert "City" not in result


def test_lead_email_escapes_its_values() -> None:
    result = render_lead_email(heading="New enquiry", fields={"Name": "<script>x</script>"})

    assert "<script>" not in result
