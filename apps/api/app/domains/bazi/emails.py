"""The couple's emailed copy of their Ba Zi result. Rendering only, no I/O.

The reading is plain text, like the tour confirmations: the shared layout turns
it into paragraphs and bolds the value of every short `Label: value` line, which
is what makes the pillar rows scannable. The one authored piece of HTML is the
Ba Zi card, which sits between the greeting and the reading. The page used to
offer that card as a PNG download; it is drawn here instead, as a table of live
text, so it needs no image renderer and no bundled Chinese font, and shows even
where remote images are blocked.

The sentences are the page's, copied from
`apps/web/src/routes/wedding-tools/kalkulator-bazi-pasangan/content.ts`. They
are duplicated because the email has to be written here: the API recomputes the
result and renders it itself instead of mailing text a caller supplies. Edit a
sentence there and here together, Indonesian first.

No birth date or time appears in the copy -- only what the page showed. The
mail provider keeps what it sends, and the page promises those are not kept.
"""

from __future__ import annotations

import html
import re
from datetime import date

from app.domains.bazi.labels import ELEMENTS, label
from app.domains.bazi.schemas import BaziResponse, ChartOut, DateCheckOut, DateReasonOut, FindingOut, PillarOut
from app.schemas.content import Locale
from app.services.email import paragraphs

_WHITESPACE = re.compile(r"\s+")

_WEEKDAYS: dict[Locale, tuple[str, ...]] = {
    "id": ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"),
    "en": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
}
_MONTHS: dict[Locale, tuple[str, ...]] = {
    "id": (
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ),
    "en": (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ),
}

_COPY: dict[Locale, dict[str, str]] = {
    "id": {
        "subject": "Hasil Ba Zi kalian dari 7Magic",
        "greeting": "Halo {names},",
        "greeting_plain": "Halo,",
        "intro": (
            "Ini kartu Ba Zi dan salinan hasil Kalkulator Ba Zi Pasangan yang baru saja kalian "
            "hitung di 7Magic."
        ),
        "card_kicker": "BA ZI PASANGAN",
        "card_dates": "Tanggal yang dicek",
        "chart": "Empat pilar {name}",
        "year": "Tahun",
        "month": "Bulan",
        "day": "Hari",
        "hour": "Jam",
        "hour_unknown": "tidak diketahui",
        "shio": "Shio",
        "day_master": "Day master",
        "elements": "Lima unsur",
        "tone_title": "Kecocokan menurut tradisi",
        "tone": "Kesimpulan",
        "findings_title": "Yang terbaca dari chart kalian",
        "no_findings": (
            "Tidak ada kombinasi atau benturan yang menonjol di antara shio, istana pasangan, "
            "dan day master kalian."
        ),
        "uncertain": (
            "Salah satu pilar tahun atau bulan di atas bergantung pada jam lahir, jadi bacaan dan "
            "cek tanggal ini dihitung dari perkiraan. Isi jam lahir yang tepat di kalkulator agar "
            "hasilnya sesuai."
        ),
        "dates_title": "Cek tanggal pernikahan",
        "verdict": "Hasil",
        "day_pillar": "Pilar hari",
        "quiet": "Tidak berbenturan dengan shio maupun istana pasangan kalian.",
        "elder": (
            "Ba Zi adalah tradisi, bukan kepastian. Banyak keluarga tetap mengonfirmasi dengan "
            "orang tua atau ahli feng shui sebelum memutuskan, dan keputusan akhirnya tetap di "
            "tangan kalian berdua."
        ),
        "sign_off": "Salam hangat,\nTim 7Magic",
    },
    "en": {
        "subject": "Your Ba Zi result from 7Magic",
        "greeting": "Hi {names},",
        "greeting_plain": "Hi,",
        "intro": (
            "Here is your Ba Zi card and a copy of the Ba Zi Couple Calculator result you just "
            "worked out on 7Magic."
        ),
        "card_kicker": "COUPLE BA ZI",
        "card_dates": "Dates checked",
        "chart": "{name}'s four pillars",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "hour": "Hour",
        "hour_unknown": "unknown",
        "shio": "Zodiac sign",
        "day_master": "Day master",
        "elements": "Five elements",
        "tone_title": "Compatibility by tradition",
        "tone": "Overall",
        "findings_title": "What your charts show",
        "no_findings": "No notable combination or clash between your signs, spouse palaces and day masters.",
        "uncertain": (
            "One of the year or month pillars above depends on the time of birth, so the reading "
            "and this date check are based on an estimate. Add the exact time of birth in the "
            "calculator for a result that matches."
        ),
        "dates_title": "Wedding date check",
        "verdict": "Result",
        "day_pillar": "Day pillar",
        "quiet": "It doesn't clash with either of your signs or spouse palaces.",
        "elder": (
            "Ba Zi is a tradition, not a certainty. Many families still check with their elders or "
            "a feng shui master before deciding, and the final decision is yours to make together."
        ),
        "sign_off": "Warm regards,\nThe 7Magic team",
    },
}

# Neutral stand-ins for a blank name, as on the page: never the example couple.
_FALLBACK_NAMES: dict[Locale, tuple[str, str]] = {
    "id": ("Pengantin 1", "Pengantin 2"),
    "en": ("Partner 1", "Partner 2"),
}

_VERDICTS: dict[Locale, dict[str, str]] = {
    "id": {"safe": "Aman", "consider": "Perlu dipertimbangkan", "clash": "Bentrok"},
    "en": {"safe": "Clear", "consider": "Worth weighing", "clash": "Clash"},
}

# One line per day master, by stem index.
_DAY_MASTERS: dict[Locale, tuple[str, ...]] = {
    "id": (
        "Seperti pohon besar: lurus, teguh, senang tumbuh dan melindungi.",
        "Seperti tanaman merambat: luwes, ramah, pandai menyesuaikan diri.",
        "Seperti matahari: hangat, terbuka, sumber semangat orang di sekitarnya.",
        "Seperti nyala lilin: lembut, teliti, menerangi orang-orang terdekat.",
        "Seperti gunung: stabil, bisa diandalkan, tidak mudah goyah.",
        "Seperti tanah kebun: merawat, sabar, membuat yang lain tumbuh.",
        "Seperti baja: tegas, adil, berani mengambil keputusan.",
        "Seperti perhiasan: halus, rapi, peka pada detail dan keindahan.",
        "Seperti sungai besar: bebas, cerdas, penuh gagasan.",
        "Seperti embun dan hujan: intuitif, tenang, menyejukkan.",
    ),
    "en": (
        "Like a tall tree: upright, steady, keen to grow and to shelter others.",
        "Like a climbing vine: flexible, friendly, good at adapting.",
        "Like the sun: warm, open, a source of energy for everyone around.",
        "Like a candle flame: gentle, careful, lighting up the people closest.",
        "Like a mountain: stable, dependable, hard to shake.",
        "Like garden soil: nurturing, patient, helping others grow.",
        "Like steel: decisive, fair, unafraid to make the call.",
        "Like fine jewellery: refined, neat, alert to detail and beauty.",
        "Like a great river: free, clever, full of ideas.",
        "Like dew and rain: intuitive, calm, soothing.",
    ),
}

# Keyed `pillar:rule`. `{a}`/`{b}` are the partners in order; `{source}` is
# whoever generates or controls, `{other}` their partner.
_READINGS: dict[Locale, dict[str, str]] = {
    "id": {
        "year:six_combination": (
            "Shio {a} ({shio_a}) dan {b} ({shio_b}) membentuk Kombinasi Enam. Menurut tradisi, "
            "keluarga kedua pihak cenderung mudah akrab."
        ),
        "year:half_harmony": (
            "Shio {a} dan {b} berada dalam satu kelompok Tiga Harmoni. Tradisi membacanya sebagai "
            "tanda mudah bekerja sama."
        ),
        "year:clash": (
            "Shio {a} ({shio_a}) dan {b} ({shio_b}) berbenturan. Banyak keluarga menganggapnya hal "
            "untuk dibicarakan bersama, bukan larangan."
        ),
        "year:harm": (
            "Shio {a} dan {b} membentuk pasangan Celaka. Tradisi menyarankan lebih sabar dalam "
            "urusan keluarga besar."
        ),
        "day:six_combination": (
            "Cabang hari kalian, yang di Ba Zi disebut istana pasangan, saling berkombinasi. "
            "Menurut tradisi ini tanda ikatan yang hangat di rumah tangga."
        ),
        "day:half_harmony": (
            "Cabang hari kalian (istana pasangan) berada dalam satu kelompok Tiga Harmoni: tradisi "
            "membacanya sebagai saling mendukung."
        ),
        "day:clash": (
            "Cabang hari kalian (istana pasangan) berbenturan. Untuk pasangan, inilah yang paling "
            "diperhatikan dalam Ba Zi; ahli biasanya melihat seluruh chart sebelum menyimpulkan "
            "apa pun."
        ),
        "day:harm": (
            "Cabang hari kalian (istana pasangan) membentuk pasangan Celaka. Tradisi membacanya "
            "sebagai gesekan kecil sehari-hari yang perlu dikomunikasikan."
        ),
        "day_master:stem_combination": (
            "Day master kalian ({char_a} dan {char_b}) saling berpasangan. Dalam Ba Zi ini salah "
            "satu tanda jodoh yang klasik."
        ),
        "day_master:generates": (
            "Unsur {source} ({source_element}) menghidupi unsur {other} ({other_element}). Tradisi "
            "membacanya sebagai pasangan yang saling menopang."
        ),
        "day_master:controls": (
            "Unsur {source} ({source_element}) mengendalikan unsur {other} ({other_element}). Bukan "
            "hal buruk; tradisi menyarankan pembagian peran yang seimbang."
        ),
        "day_master:same_element": (
            "Day master kalian berunsur sama ({element_a}). Mudah saling memahami, kadang sama-sama "
            "keras kepala."
        ),
    },
    "en": {
        "year:six_combination": (
            "{a}'s sign ({shio_a}) and {b}'s ({shio_b}) form a Six Combination. By tradition, the "
            "two families tend to get on easily."
        ),
        "year:half_harmony": (
            "{a}'s and {b}'s signs sit in the same Three Harmony group, which tradition reads as an "
            "easy partnership."
        ),
        "year:clash": (
            "{a}'s sign ({shio_a}) and {b}'s ({shio_b}) clash. Many families treat this as "
            "something to talk through together, not a prohibition."
        ),
        "year:harm": (
            "{a}'s and {b}'s signs form a Harm pair. Tradition advises extra patience in matters of "
            "the wider family."
        ),
        "day:six_combination": (
            "Your day branches, called the spouse palace in Ba Zi, combine. By tradition this is a "
            "sign of a warm bond at home."
        ),
        "day:half_harmony": (
            "Your day branches (the spouse palace) sit in the same Three Harmony group, which "
            "tradition reads as mutual support."
        ),
        "day:clash": (
            "Your day branches (the spouse palace) clash. For a couple this is what Ba Zi watches "
            "most closely; a practitioner usually reads the whole chart before concluding anything."
        ),
        "day:harm": (
            "Your day branches (the spouse palace) form a Harm pair. Tradition reads it as small "
            "everyday friction worth talking about."
        ),
        "day_master:stem_combination": (
            "Your day masters ({char_a} and {char_b}) pair with each other, one of the classic "
            "signs of a match in Ba Zi."
        ),
        "day_master:generates": (
            "{source}'s element ({source_element}) feeds {other}'s ({other_element}). Tradition "
            "reads this as partners who hold each other up."
        ),
        "day_master:controls": (
            "{source}'s element ({source_element}) controls {other}'s ({other_element}). Not a bad "
            "sign; tradition advises sharing roles evenly."
        ),
        "day_master:same_element": (
            "Your day masters share an element ({element_a}): quick to understand each other, and "
            "sometimes equally stubborn."
        ),
    },
}

_REASON_VERBS: dict[Locale, dict[str, str]] = {
    "id": {
        "clash": "berbenturan dengan",
        "harm": "membentuk pasangan Celaka dengan",
        "six_combination": "berkombinasi dengan",
        "half_harmony": "selaras (Tiga Harmoni) dengan",
    },
    "en": {
        "clash": "clashes with",
        "harm": "forms a Harm pair with",
        "six_combination": "combines with",
        "half_harmony": "is in Three Harmony with",
    },
}

_REASONS: dict[Locale, dict[str, str]] = {
    "id": {
        "line": "Hari {day} {animal} {verb} {target}.",
        "shio": "shio {shio} {name}",
        "day": "cabang hari (istana pasangan) {name}",
    },
    "en": {
        "line": "The {day} {animal} day {verb} {target}.",
        "shio": "{name}'s sign, the {shio}",
        "day": "{name}'s day branch (spouse palace)",
    },
}


def _one_line(value: str | None) -> str:
    # A name is the one thing in this email a stranger typed. Left with its
    # newlines it could start a paragraph of its own, or forge a `Label: value`
    # row the layout would style like a real one.
    return _WHITESPACE.sub(" ", value or "").strip()


def _format_date(day: date, locale: Locale) -> str:
    """`Sabtu, 26 September 2026`, as the page spells a checked date."""
    return f"{_WEEKDAYS[locale][day.weekday()]}, {day.day} {_MONTHS[locale][day.month - 1]} {day.year}"


def _pillar_line(name: str, pillar: PillarOut | None, copy: dict[str, str]) -> str:
    if pillar is None:
        return f"{name}: {copy['hour_unknown']}"
    return (
        f"{name}: {pillar.stem.char}{pillar.branch.char} "
        f"({pillar.stem.pinyin} {pillar.branch.pinyin}) · "
        f"{pillar.stem.element_label}, {pillar.branch.animal_label}"
    )


def _chart_block(chart: ChartOut, name: str, locale: Locale) -> str:
    copy = _COPY[locale]
    master = chart.day_master
    balance = " · ".join(
        f"{label('element', element, locale)} {chart.elements[element]}" for element in ELEMENTS
    )
    return "\n".join(
        [
            copy["chart"].format(name=name),
            *(_pillar_line(copy[key], getattr(chart, key), copy) for key in ("year", "month", "day", "hour")),
            f"{copy['shio']}: {chart.shio.animal_label}",
            f"{copy['day_master']}: {master.char} {master.pinyin} · {master.element_label}",
            _DAY_MASTERS[locale][master.index],
            f"{copy['elements']}: {balance}",
        ]
    )


def _finding_block(
    finding: FindingOut, charts: list[ChartOut], names: tuple[str, str], locale: Locale
) -> str:
    heading = f"{finding.rule_label} ({finding.a} · {finding.b})"
    template = _READINGS[locale].get(f"{finding.pillar}:{finding.rule}")
    if template is None:
        # A pairing with no sentence still names its rule, as on the page.
        return heading
    source = finding.source or 0
    other = 1 - source
    return heading + "\n" + template.format(
        a=names[0],
        b=names[1],
        shio_a=charts[0].shio.animal_label,
        shio_b=charts[1].shio.animal_label,
        char_a=finding.a,
        char_b=finding.b,
        element_a=charts[0].day_master.element_label,
        source=names[source],
        other=names[other],
        source_element=charts[source].day_master.element_label,
        other_element=charts[other].day_master.element_label,
    )


def _reason_line(
    reason: DateReasonOut,
    check: DateCheckOut,
    charts: list[ChartOut],
    names: tuple[str, str],
    locale: Locale,
) -> str:
    wording = _REASONS[locale]
    target = wording[reason.against].format(
        name=names[reason.partner], shio=charts[reason.partner].shio.animal_label
    )
    return wording["line"].format(
        day=f"{check.pillar.stem.char}{check.pillar.branch.char}",
        animal=check.pillar.branch.animal_label,
        verb=_REASON_VERBS[locale].get(reason.rule, reason.rule_label),
        target=target,
    )


def _date_block(
    check: DateCheckOut, charts: list[ChartOut], names: tuple[str, str], locale: Locale
) -> str:
    copy = _COPY[locale]
    pillar = check.pillar
    reasons = [_reason_line(reason, check, charts, names, locale) for reason in check.reasons]
    return "\n".join(
        [
            _format_date(check.date, locale),
            f"{copy['verdict']}: {_VERDICTS[locale][check.verdict]}",
            f"{copy['day_pillar']}: {pillar.stem.char}{pillar.branch.char} · {pillar.branch.animal_label}",
            *(reasons or [copy["quiet"]]),
        ]
    )


def _is_uncertain(charts: list[ChartOut]) -> bool:
    return any(
        pillar.depends_on_time or pillar.near_term
        for chart in charts
        for pillar in (chart.year, chart.month)
    )


# The card's palette is the site's cream and gold; the font stack is the layout's,
# since an email cannot load the site's own.
_CARD_FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
_CARD_HAN = "'Noto Serif SC','Songti SC','PingFang SC','Microsoft YaHei',serif"
_CARD_INK = "#141414"
_CARD_GOLD = "#8a6524"
_CARD_MUTED = "#5c5c5c"
_CARD_LINE = "#ead9b8"
_VERDICT_INK = {"safe": "#14532d", "consider": "#7a4d00", "clash": "#7f1d1d"}


def _card_pillar(name: str, pillar: PillarOut | None) -> str:
    label = (
        f'<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;'
        f'color:{_CARD_MUTED}">{html.escape(name)}</div>'
    )
    if pillar is None:
        # An unknown hour keeps its column, so the three known pillars do not
        # slide under the wrong labels.
        chars = f'<div style="font-size:28px;line-height:74px;color:{_CARD_MUTED}">&ndash;</div>'
    else:
        chars = (
            f'<div lang="zh" style="font-family:{_CARD_HAN};font-size:28px;line-height:37px;'
            f'color:{_CARD_INK}">{pillar.stem.char}</div>'
            f'<div lang="zh" style="font-family:{_CARD_HAN};font-size:28px;line-height:37px;'
            f'color:{_CARD_GOLD}">{pillar.branch.char}</div>'
        )
    return (
        '<td width="25%" align="center" style="padding:10px 2px;background:#ffffff;'
        f'border:1px solid {_CARD_LINE}">{label}{chars}</td>'
    )


def _card_chart(chart: ChartOut, name: str, locale: Locale) -> str:
    copy = _COPY[locale]
    master = chart.day_master
    cells = "".join(
        _card_pillar(copy[key], getattr(chart, key)) for key in ("year", "month", "day", "hour")
    )
    summary = (
        f"{copy['day_master']} {master.char} {master.element_label} · "
        f"{copy['shio']} {chart.shio.animal_label}"
    )
    return (
        f'<div style="margin-top:18px;font-size:14px;font-weight:600;color:{_CARD_INK}">'
        f"{html.escape(name)}</div>"
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        f'style="margin-top:8px;border-collapse:collapse;font-family:{_CARD_FONT}">'
        f"<tr>{cells}</tr></table>"
        f'<div style="margin-top:8px;font-size:13px;color:#4a4a4a">{html.escape(summary)}</div>'
    )


def _card_html(result: BaziResponse, names: tuple[str, str], locale: Locale) -> str:
    """The Ba Zi card: both charts, the tone and any checked dates, as markup an
    email client will render. Everything a visitor typed is escaped here."""
    copy = _COPY[locale]
    charts = "".join(
        _card_chart(chart, name, locale) for chart, name in zip(result.charts, names, strict=True)
    )
    dates = ""
    if result.date_checks:
        rows = "".join(
            "<tr>"
            f'<td style="padding:3px 0;font-size:14px;color:{_CARD_INK}">'
            f"{html.escape(_format_date(check.date, locale))}</td>"
            f'<td align="right" style="padding:3px 0;font-size:14px;font-weight:700;'
            f'color:{_VERDICT_INK[check.verdict]}">{_VERDICTS[locale][check.verdict]}</td>'
            "</tr>"
            for check in result.date_checks
        )
        dates = (
            f'<div style="margin-top:16px;padding-top:14px;border-top:1px solid {_CARD_LINE}">'
            f'<div style="font-size:12px;letter-spacing:.1em;text-transform:uppercase;'
            f'color:{_CARD_MUTED}">{copy["card_dates"]}</div>'
            '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
            f'style="margin-top:4px;font-family:{_CARD_FONT}">{rows}</table></div>'
        )
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="margin:4px 0 22px"><tr>'
        f'<td style="padding:24px;background:#fbf7f0;border:1px solid {_CARD_LINE};'
        f'border-radius:14px;font-family:{_CARD_FONT}">'
        f'<div style="font-size:11px;font-weight:600;letter-spacing:.24em;color:{_CARD_GOLD}">'
        f'{copy["card_kicker"]}</div>'
        f'<div style="margin-top:6px;font-size:24px;line-height:1.25;font-weight:700;'
        f'color:{_CARD_INK}">{html.escape(" & ".join(names))}</div>'
        f"{charts}"
        f'<div style="margin-top:18px;padding-top:14px;border-top:1px solid {_CARD_LINE}">'
        f'<div style="font-size:12px;letter-spacing:.1em;text-transform:uppercase;'
        f'color:{_CARD_MUTED}">{copy["tone_title"]}</div>'
        f'<div style="margin-top:2px;font-size:18px;font-weight:700;color:{_CARD_INK}">'
        f"{html.escape(result.tone_label)}</div></div>"
        f"{dates}</td></tr></table>"
    )


def result_copy(result: BaziResponse, locale: Locale) -> tuple[str, str, str]:
    """Subject, plain-text body and HTML body of the copy the couple is sent.

    The HTML body is the same reading with the card set between the greeting and
    the rest; the plain text is what a client without HTML shows.

    The subject is fixed and carries no name: it is the first thing a stranger
    reads, and a name is typed by whoever filled the form, not necessarily by
    the person the email reaches.
    """
    copy = _COPY[locale]
    typed = [_one_line(chart.name) for chart in result.charts]
    names = (typed[0] or _FALLBACK_NAMES[locale][0], typed[1] or _FALLBACK_NAMES[locale][1])
    given = " & ".join(name for name in typed if name)

    blocks = [
        copy["greeting"].format(names=given) if given else copy["greeting_plain"],
        copy["intro"],
        *(_chart_block(chart, name, locale) for chart, name in zip(result.charts, names, strict=True)),
        f"{copy['tone_title']}\n{copy['tone']}: {result.tone_label}",
        copy["findings_title"],
        *(
            [_finding_block(finding, result.charts, names, locale) for finding in result.findings]
            or [copy["no_findings"]]
        ),
    ]
    if _is_uncertain(result.charts):
        blocks.append(copy["uncertain"])
    if result.date_checks:
        blocks.append(copy["dates_title"])
        blocks += [_date_block(check, result.charts, names, locale) for check in result.date_checks]
    blocks += [copy["elder"], copy["sign_off"]]
    # Greeting and intro, then the card, then everything they introduce.
    body_html = (
        paragraphs("\n\n".join(blocks[:2]))
        + _card_html(result, names, locale)
        + paragraphs("\n\n".join(blocks[2:]))
    )
    return copy["subject"], "\n\n".join(blocks), body_html
