from __future__ import annotations

from io import BytesIO

from PIL import Image

from app.services.images import BREAKPOINTS, render_variants, srcset_from


def _jpeg(width: int, height: int) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height), (180, 140, 90)).save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def test_renders_both_formats_at_every_breakpoint_that_fits() -> None:
    variants, metadata = render_variants(_jpeg(2400, 1600))

    assert metadata["breakpoints_used"] == [label for label, _ in BREAKPOINTS]
    # Five widths in two formats.
    assert len(variants) == len(BREAKPOINTS) * 2
    assert {variant.fmt for variant in variants} == {"webp", "jpeg"}


def test_never_upscales_beyond_the_original_width() -> None:
    """A 600px original must not be blown up to 1920 -- that adds bytes without
    adding detail, which is why some imported photos have fewer variants."""
    variants, metadata = render_variants(_jpeg(600, 400))

    assert metadata["breakpoints_used"] == ["xs", "sm"]
    assert max(variant.width for variant in variants) == 480


def test_preserves_aspect_ratio() -> None:
    variants, _ = render_variants(_jpeg(1600, 900))

    for variant in variants:
        assert abs(variant.width / variant.height - 16 / 9) < 0.02


def test_records_orientation_and_original_dimensions() -> None:
    _, landscape = render_variants(_jpeg(1600, 900))
    _, portrait = render_variants(_jpeg(900, 1600))
    _, square = render_variants(_jpeg(800, 800))

    assert landscape["orientation"] == "landscape"
    assert portrait["orientation"] == "portrait"
    assert square["orientation"] == "square"
    assert (landscape["original_width"], landscape["original_height"]) == (1600, 900)


def test_undecodable_upload_returns_none_rather_than_raising() -> None:
    """The original is already stored by the time we resize, so a file Pillow
    cannot read must not fail the whole upload."""
    assert render_variants(b"definitely not an image") is None


def test_srcset_lists_url_and_width_pairs() -> None:
    entries = [
        {"cdn_url": "https://cdn.test/a_xs_320w.webp", "width": 320},
        {"cdn_url": "https://cdn.test/a_sm_480w.webp", "width": 480},
    ]

    assert srcset_from(entries) == (
        "https://cdn.test/a_xs_320w.webp 320w, https://cdn.test/a_sm_480w.webp 480w"
    )
