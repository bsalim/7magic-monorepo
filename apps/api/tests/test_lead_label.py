import pytest

from app.services.leads import _lead_label


@pytest.mark.parametrize(
    ("message", "label"),
    [
        ("LEAD: Paket Sangjit\nTanggal sangjit: 12 Okt", "Paket Sangjit"),
        ("  lead: Prenup \n", "Prenup"),
        # A couple writing "lead" mid-sentence is not a landing-page marker.
        ("Halo, saya mau tanya. LEAD: bukan ini", None),
        ("LEAD:", None),
        ("", None),
        (None, None),
    ],
)
def test_lead_label_reads_only_a_leading_marker(message: str | None, label: str | None) -> None:
    assert _lead_label(message) == label
