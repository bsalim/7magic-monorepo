"""Crop a photo for an article header and print its credit into the image.

For celebrity wedding articles that use a photo of the couple rather than a
stock scene. The credit is burned in, not only captioned, because the image
travels without the page: WhatsApp previews, Google Discover and image search
all show it bare. A printed credit names the owner; it is not a licence, so
prefer agency press photos and the couple's own posts, and ask the
photographer where you can.

Output is 1.9:1, the ratio WhatsApp and Discover display uncropped. The credit
sits lower-centre because the page crops the same file twice: the article
header (`h-[360px] object-cover`) trims top and bottom on desktop and both
sides on a phone, where only about the middle half of the width survives.

    uv run python scripts/credit_article_photo.py in.jpg out.jpg "Foto: Instagram @asnawi_bhr"
    uv run python scripts/credit_article_photo.py in.jpg out.jpg "..." --focus 0.35

`--focus` is the vertical centre of the crop as a fraction of the height
(0 top, 1 bottom); portraits usually want faces nearer the top than 0.5.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

WIDTH, HEIGHT = 1600, 840
# Bottom edge of the credit as a fraction of the height. Past ~0.9 the desktop
# header crops it off; the card thumbnails trim a little less than that.
CREDIT_BOTTOM = 0.82
# Wider than about half the image and a phone crops the ends of the credit.
MAX_CREDIT_WIDTH = 0.45


def crop(image: Image.Image, focus: float) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left = (resized.width - WIDTH) // 2
    top = round((resized.height - HEIGHT) * min(max(focus, 0.0), 1.0))
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def add_credit(image: Image.Image, text: str) -> Image.Image:
    size = 26
    font = ImageFont.load_default(size=size)
    draw = ImageDraw.Draw(image)
    while draw.textlength(text, font=font) > WIDTH * MAX_CREDIT_WIDTH and size > 16:
        size -= 1
        font = ImageFont.load_default(size=size)
    if draw.textlength(text, font=font) > WIDTH * MAX_CREDIT_WIDTH:
        raise SystemExit(f"Credit too long to stay visible on a phone: {text!r}")

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    pad_x, pad_y = size * 0.7, size * 0.4
    box_w, box_h = right - left + 2 * pad_x, bottom - top + 2 * pad_y
    x0 = (WIDTH - box_w) / 2
    y1 = HEIGHT * CREDIT_BOTTOM
    y0 = y1 - box_h

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        (x0, y0, x0 + box_w, y1), radius=box_h / 2, fill=(0, 0, 0, 140)
    )
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    ImageDraw.Draw(image).text(
        (x0 + pad_x - left, y0 + pad_y - top), text, font=font, fill=(255, 255, 255)
    )
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("credit")
    parser.add_argument("--focus", type=float, default=0.5)
    args = parser.parse_args()

    with Image.open(args.source) as image:
        result = add_credit(crop(image, args.focus), args.credit)
    result.save(args.output, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"{args.output}  {result.width}x{result.height}  {args.output.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
