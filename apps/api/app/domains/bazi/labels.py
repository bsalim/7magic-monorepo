"""Names for the engine's indices: characters, pinyin, and id/en labels.

Short labels only. The longer reading copy (what a day master is like, what a
clash means for a couple) lives on the web page with the rest of the tool's
copy, where it is edited alongside the Indonesian it is translated from.
"""

from __future__ import annotations

from app.schemas.content import Locale

STEM_CHARS = "甲乙丙丁戊己庚辛壬癸"
STEM_PINYIN = ("Jiǎ", "Yǐ", "Bǐng", "Dīng", "Wù", "Jǐ", "Gēng", "Xīn", "Rén", "Guǐ")
BRANCH_CHARS = "子丑寅卯辰巳午未申酉戌亥"
BRANCH_PINYIN = ("Zǐ", "Chǒu", "Yín", "Mǎo", "Chén", "Sì", "Wǔ", "Wèi", "Shēn", "Yǒu", "Xū", "Hài")

ELEMENTS = ("wood", "fire", "earth", "metal", "water")
ANIMALS = ("rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig")

_LABELS: dict[str, dict[Locale, dict[str, str]]] = {
    "element": {
        "id": {"wood": "Kayu", "fire": "Api", "earth": "Tanah", "metal": "Logam", "water": "Air"},
        "en": {"wood": "Wood", "fire": "Fire", "earth": "Earth", "metal": "Metal", "water": "Water"},
    },
    "animal": {
        # The shio names Indonesian Chinese families use day to day.
        "id": {
            "rat": "Tikus",
            "ox": "Kerbau",
            "tiger": "Macan",
            "rabbit": "Kelinci",
            "dragon": "Naga",
            "snake": "Ular",
            "horse": "Kuda",
            "goat": "Kambing",
            "monkey": "Monyet",
            "rooster": "Ayam",
            "dog": "Anjing",
            "pig": "Babi",
        },
        "en": {
            "rat": "Rat",
            "ox": "Ox",
            "tiger": "Tiger",
            "rabbit": "Rabbit",
            "dragon": "Dragon",
            "snake": "Snake",
            "horse": "Horse",
            "goat": "Goat",
            "monkey": "Monkey",
            "rooster": "Rooster",
            "dog": "Dog",
            "pig": "Pig",
        },
    },
    "rule": {
        "id": {
            "six_combination": "Kombinasi Enam (Liu He)",
            "half_harmony": "Setengah Tiga Harmoni (San He)",
            "clash": "Benturan (Chong)",
            "harm": "Celaka (Hai)",
            "stem_combination": "Kombinasi Batang (He)",
            "generates": "Saling menghidupi",
            "controls": "Saling mengendalikan",
            "same_element": "Unsur sama",
        },
        "en": {
            "six_combination": "Six Combination (Liu He)",
            "half_harmony": "Half Three Harmony (San He)",
            "clash": "Clash (Chong)",
            "harm": "Harm (Hai)",
            "stem_combination": "Stem Combination (He)",
            "generates": "Generating",
            "controls": "Controlling",
            "same_element": "Same element",
        },
    },
    "tone": {
        "id": {
            "harmony": "Banyak keselarasan",
            "balanced": "Seimbang",
            "clash": "Ada bentrok yang perlu dibicarakan",
        },
        "en": {
            "harmony": "Mostly in harmony",
            "balanced": "Balanced",
            "clash": "A clash worth talking through",
        },
    },
}


def label(kind: str, key: str, locale: Locale) -> str:
    return _LABELS[kind][locale][key]
