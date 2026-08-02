"""Generate responsive variants for an uploaded venue photo.

Imported photos carry five widths in both webp and jpeg, and the public site
renders them through a <picture> srcset. Uploads used to store a single
original, so a CMS-added photo was the one image every screen downloaded.
This module produces the same variant set so uploads and imports behave alike.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from PIL import Image, ImageOps

logger = logging.getLogger("app.images")

# Matches the imported photos: label, target width, and per-format quality.
BREAKPOINTS: list[tuple[str, int]] = [
    ("xs", 320),
    ("sm", 480),
    ("md", 800),
    ("lg", 1200),
    ("xl", 1920),
]

WEBP_QUALITY = 85
JPEG_QUALITY = 90

# The layout hint stored alongside the variants, mirroring the imported set.
SIZES_ATTRIBUTE = (
    "(max-width: 320px) 280px, (max-width: 480px) 440px, (max-width: 800px) 760px, 1200px"
)


@dataclass
class RenderedVariant:
    """One encoded image ready to upload."""

    key_suffix: str
    content: bytes
    content_type: str
    width: int
    height: int
    fmt: str
    quality: int
    variant_type: str


def _orientation(width: int, height: int) -> str:
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def render_variants(original: bytes) -> tuple[list[RenderedVariant], dict[str, Any]] | None:
    """Encode `original` at every breakpoint in webp and jpeg.

    Returns the variants plus metadata about the source image, or None when the
    bytes are not a decodable image -- callers should still store the original
    in that case rather than failing the upload.
    """
    try:
        with Image.open(BytesIO(original)) as source:
            # Honour EXIF rotation before measuring, or portrait phone photos
            # come out sideways and with swapped dimensions.
            source = ImageOps.exif_transpose(source)
            source.load()
            src_width, src_height = source.size
            rgb = source.convert("RGB")
    except Exception as exc:  # Pillow raises a variety of decode errors
        logger.warning("Could not decode uploaded image for resizing: %s", exc)
        return None

    variants: list[RenderedVariant] = []

    for label, target_width in BREAKPOINTS:
        # Never upscale: a 600px original gets xs/sm only, which is why some
        # imported photos legitimately have fewer than five variants.
        if target_width > src_width:
            continue

        height = max(1, round(src_height * target_width / src_width))
        resized = rgb.resize((target_width, height), Image.LANCZOS)

        for fmt, quality, extension, content_type in (
            ("webp", WEBP_QUALITY, "webp", "image/webp"),
            ("jpeg", JPEG_QUALITY, "jpg", "image/jpeg"),
        ):
            buffer = BytesIO()
            resized.save(buffer, format=fmt.upper(), quality=quality)
            variants.append(
                RenderedVariant(
                    key_suffix=f"_{label}_{target_width}w.{extension}",
                    content=buffer.getvalue(),
                    content_type=content_type,
                    width=target_width,
                    height=height,
                    fmt=fmt,
                    quality=quality,
                    variant_type=label,
                )
            )

    metadata = {
        "original_width": src_width,
        "original_height": src_height,
        "orientation": _orientation(src_width, src_height),
        "breakpoints_used": [
            label for label, width in BREAKPOINTS if width <= src_width
        ],
        "sizes_attribute": SIZES_ATTRIBUTE,
    }
    return variants, metadata


def srcset_from(entries: list[dict[str, Any]]) -> str:
    """`url 320w, url 480w, ...` for one format's variants."""
    return ", ".join(f"{entry['cdn_url']} {entry['width']}w" for entry in entries)
