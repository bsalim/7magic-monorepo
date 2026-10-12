import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from import_article_translations_md import tag_stream  # noqa: E402
from import_markdown_articles import ConversionError, convert  # noqa: E402

SRC = "https://media.7magicwedding.com/articles/2026-10/abc-jewel.jpg"
PATH = Path("article.md")


def test_whole_line_image_becomes_a_captioned_figure() -> None:
    html = convert(
        f'Teks.\n![Rain Vortex di Jewel]({SRC} "Foto: Tin Pham / Pexels")\nLanjut.', PATH
    )

    assert html == (
        "<p>Teks.</p>\n"
        f'<figure><img src="{SRC}" alt="Rain Vortex di Jewel" loading="lazy">'
        "<figcaption>Foto: Tin Pham / Pexels</figcaption></figure>\n"
        "<p>Lanjut.</p>"
    )


def test_caption_is_optional_and_alt_is_escaped() -> None:
    html = convert(f'![Kubah "Flower Dome" & taman]({SRC})', PATH)

    assert html == (
        f'<figure><img src="{SRC}" alt="Kubah &quot;Flower Dome&quot; &amp; taman" '
        'loading="lazy"></figure>'
    )


@pytest.mark.parametrize(
    "md",
    [
        "![Hotlinked](https://images.pexels.com/photos/1/x.jpg)",
        f"Sebuah paragraf dengan ![gambar]({SRC}) di tengah.",
        f"  ![Indented]({SRC})",
    ],
)
def test_other_images_are_still_refused(md: str) -> None:
    with pytest.raises(ConversionError, match="image"):
        convert(md, PATH)


def test_translated_alt_does_not_break_the_shared_tag_stream() -> None:
    indonesian = convert(f'![Air terjun di Jewel]({SRC} "Foto: Pexels")', PATH)
    english = convert(f'![The waterfall at Jewel]({SRC} "Photo: Pexels")', PATH)

    assert tag_stream(indonesian) == tag_stream(english)
