# Ba Zi Compatibility Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A free Ba Zi (Four Pillars) tool on the wedding-tools hub: each partner's chart and a compatibility reading free, a candidate-date clash check and a printable card behind the shared lead gate.

**Architecture:** A pure calculation engine in a new API domain package `app/domains/bazi/` (astronomy → pillars → relations → service), exposed by one stateless public endpoint `POST /api/v1/public/bazi`. The SvelteKit page calls it through a `/api/bazi` proxy and renders the result; the lead flows through the existing tool-lead gate as `tool_bazi`.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic v2, pytest (`apps/api`); SvelteKit Svelte 5 runes, Tailwind, vitest, Paraglide (`apps/web`); SvelteKit CMS (`apps/cms`). Dev-only references: `skyfield` (JPL DE421) and `lunar-python`.

**Spec:** `docs/superpowers/specs/2026-10-18-wedding-tools-bazi-design.md`

## Global Constraints

- Engine written from scratch: no Ba Zi or astronomy library imported by `app/`. `skyfield` and `lunar-python` go in the `dev` dependency group and are used only by reference scripts and tests.
- Supported years for births and checked dates: 1900 to 2100 inclusive.
- Zones: `WIB` = UTC+7, `WITA` = UTC+8, `WIT` = UTC+9. Clock time, no true-solar-time correction.
- 23:00 starts the next day's pillar.
- Solar-term accuracy: within 2 minutes of the reference. `near_term` window: 30 minutes.
- Up to 3 candidate dates per request.
- No percentage or score anywhere. No "lucky"/"beruntung"/"guaranteed". Readings framed as tradition, with the note to confirm with an elder or a feng shui master.
- The endpoint stores nothing and logs no birth data. POST only.
- API is snake_case on the wire. Indonesian copy is canonical; English is a translation.
- Comments explain why, not what (CLAUDE.md). Run `npx gitnexus impact <symbol>` before editing an existing symbol, and `npx gitnexus detect-changes --scope all --repo .` before committing.
- The user works on `main` and CI deploys on push: commit locally per task, **push only when the user says so**.

## Review Focus

1. A birth at 23:30 with the time given: the day pillar is the next calendar day's, and the hour is Zi with the stem from that next day (test in Task 2).
2. A Lichun-day birth with no time: year and month pillars computed at noon and flagged `depends_on_time`, never silently guessed (test in Task 2).
3. Impossible or out-of-range input (`2026-02-30`, year 1899, four dates, one partner): 422, not a 500 (test in Task 4).
4. Two partners with identical charts: no clash, day masters `same_element`, tone `balanced` (test in Task 3).
5. The API unreachable from the page: the proxy answers 502 and the page keeps what the couple typed and shows a retry message (test in Task 5; page behaviour checked in Task 6).

---

## File structure

```
apps/api/app/domains/bazi/
  __init__.py
  vsop87_earth.py   # data only: truncated VSOP87D Earth series
  solar.py          # ΔT, apparent solar longitude, jie term moments
  pillars.py        # stems, branches, the four pillars, chart flags
  relations.py      # clash/combine/harm/half-harmony/stem combo/element cycles
  service.py        # chart(), compatibility(), check_date()
  labels.py         # id/en names for elements, animals, rules
  schemas.py        # request/response models
apps/api/app/api/v1/public/bazi.py         # the router
apps/api/scripts/bazi_reference.py         # one-off: writes reference values with skyfield + lunar-python
apps/api/tests/test_bazi_solar.py
apps/api/tests/test_bazi_pillars.py
apps/api/tests/test_bazi_relations.py
apps/api/tests/test_bazi_api.py
apps/web/src/routes/api/bazi/+server.ts
apps/web/src/lib/tools/bazi.ts (+ bazi.test.ts)
apps/web/src/lib/components/tools/BaziCard.svelte
apps/web/src/routes/wedding-tools/kalkulator-bazi-pasangan/{+page.svelte,content.ts}
```

Index conventions used everywhere (engine and wire): stems 0–9 = Jia, Yi, Bing, Ding, Wu, Ji, Geng, Xin, Ren, Gui; branches 0–11 = Zi … Hai; elements 0–4 = wood, fire, earth, metal, water. Stem element `stem // 2`, yang when `stem % 2 == 0`. Branch elements: `[water, earth, wood, wood, earth, fire, fire, earth, metal, metal, earth, water]`.

---

### Task 1: Solar terms

**Files:**
- Create: `apps/api/app/domains/bazi/__init__.py`, `apps/api/app/domains/bazi/vsop87_earth.py`, `apps/api/app/domains/bazi/solar.py`, `apps/api/scripts/bazi_reference.py`
- Modify: `apps/api/pyproject.toml` (dev group: `skyfield`, `lunar-python`)
- Test: `apps/api/tests/test_bazi_solar.py`

**Interfaces:**
- Produces:
  - `JIE_LONGITUDES: tuple[float, ...]`: 12 values, index = month branch offset from Yin, `(315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285)`
  - `delta_t_seconds(year: float) -> float`: Espenak–Meeus (NASA) polynomials, 1900–2100
  - `solar_longitude(moment: datetime) -> float`: apparent geocentric longitude in degrees `[0, 360)` for a UTC-aware datetime
  - `term_moment(year: int, longitude: float) -> datetime`: the UTC moment in Gregorian `year` when the sun reaches `longitude`
  - `jie_moments(year: int) -> list[tuple[int, datetime]]`: `(month_branch, utc_moment)` for the 12 jie terms in that Gregorian year, chronological; `functools.cache`d

- [ ] **Step 1: Generate the references.** Write `scripts/bazi_reference.py` (module docstring: what it writes, that it is run once by hand, that skyfield/lunar-python are dev-only). Its `solar` sub-command prints, for 1900, 1930, 1960, 1975, 1988, 1990, 2000 and 2050, the 12 jie moments to the second in UTC computed with skyfield + DE421 (`almanac`-style root finding on apparent ecliptic longitude of date). Run `uv sync` then `uv run python scripts/bazi_reference.py solar`. Separately fetch Hong Kong Observatory's "24 Solar Terms" pages for 2013, 2020, 2024 and 2026 (`https://www.hko.gov.hk/en/gts/astron<YYYY>/Solar_Term_<YYYY>.htm`) and note Lichun, Jingzhe, Xiaoshu, Daxue and Xiaohan, converting HKT (UTC+8) to UTC.

- [ ] **Step 2: Write the failing tests** in `tests/test_bazi_solar.py`, with the reference values pasted in as constants and a comment naming each source:

```python
@pytest.mark.parametrize(("year", "longitude", "expected_utc"), SKYFIELD_REFERENCE + HKO_REFERENCE)
def test_term_moment_matches_the_reference_within_two_minutes(year, longitude, expected_utc):
    assert abs(term_moment(year, longitude) - expected_utc) <= timedelta(minutes=2)

def test_jie_moments_are_twelve_in_order_starting_with_xiaohan():
    moments = jie_moments(2026)
    assert [branch for branch, _ in moments] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
    assert all(a[1] < b[1] for a, b in zip(moments, moments[1:]))
    assert all(m.year == 2026 for _, m in moments)

def test_solar_longitude_is_normalised():
    assert 0 <= solar_longitude(datetime(2026, 3, 20, 12, tzinfo=UTC)) < 360

def test_delta_t_is_in_the_known_range():
    assert 60 < delta_t_seconds(2000) < 66   # ~63.8 s
    assert -5 < delta_t_seconds(1900) < 0    # ~-2.8 s
```

- [ ] **Step 3: Run** `uv run pytest tests/test_bazi_solar.py -v`. Expected: FAIL (module not found).

- [ ] **Step 4: Implement.** `vsop87_earth.py`: the VSOP87D Earth series (L0–L5, B0–B1, R0–R4) truncated to the term set of Meeus, *Astronomical Algorithms*, Appendix III, as tuples `(A, B, C)`, with a docstring citing VSOP87 (Bretagnon & Francou 1988, IMCCE) and the truncation. `solar.py`: Meeus ch. 25 higher-accuracy path: heliocentric L, B, R from the series (τ in Julian millennia TT) → geocentric (+180°, −B) → FK5 correction (−0.09033″) → nutation in longitude (Meeus ch. 22, the 63-term table or the abridged 4-term one if Step 5 stays within 2 min) → aberration (−20.4898″ / R). `term_moment`: start from the mean date (1 January of `year` + `((longitude − 280.46) mod 360) / 0.9856` days, Xiaohan/Lichun land in Jan–Feb), then Newton steps `t += 58 * sin(radians(target − λ))` days until under 0.5 s; convert TT → UTC with `delta_t_seconds`.

- [ ] **Step 5: Run** `uv run pytest tests/test_bazi_solar.py -v`. Expected: all PASS. Then `uv run ruff check app/domains/bazi scripts/bazi_reference.py tests/test_bazi_solar.py`. Expected: clean.

- [ ] **Step 6: Commit** (local, no push): `feat(api): solar-term moments for the Ba Zi engine`.

---

### Task 2: Pillars and charts

**Files:**
- Create: `apps/api/app/domains/bazi/pillars.py`
- Modify: `apps/api/scripts/bazi_reference.py` (add `charts` sub-command)
- Test: `apps/api/tests/test_bazi_pillars.py`

**Interfaces:**
- Consumes: `jie_moments`, `term_moment` from Task 1.
- Produces:
  - `Zone = Literal["WIB", "WITA", "WIT"]`, `ZONE_OFFSETS: dict[Zone, int]` = `{"WIB": 7, "WITA": 8, "WIT": 9}`
  - `@dataclass(frozen=True) class Pillar: stem: int; branch: int; depends_on_time: bool = False; near_term: bool = False`, with `index` property = the 0–59 cycle position
  - `@dataclass(frozen=True) class Chart: year: Pillar; month: Pillar; day: Pillar; hour: Pillar | None`, with properties `day_master -> int` (day stem), `shio -> int` (year branch), `element_counts -> tuple[int, int, int, int, int]` (visible stems + branch main elements of the present pillars)
  - `day_pillar(day: date) -> Pillar`: `(JDN + 49) % 60`
  - `cycle_pillar(index: int) -> Pillar`
  - `chart_for(birth_date: date, birth_time: time | None, zone: Zone) -> Chart`

Algorithm (not determined by the signatures):
- With a time: local → UTC via the zone. Year = Gregorian year, minus one if before that year's Lichun (`term_moment(y, 315)`). Month branch = branch of the latest jie moment ≤ birth (look in `jie_moments(y)` and the previous year's Daxue/Xiaohan entries). Month stem = Five Tigers: Yin-month stem `(2 * (year_stem % 5) + 2) % 10`, then `+ (branch − 2) % 12`. Day: the local date, plus one day when local hour ≥ 23. Hour branch `((hour + 1) // 2) % 12`; hour stem = Five Rats: `(2 * (day_stem % 5) + hour_branch) % 10`, using the (possibly advanced) day's stem. `near_term` on the year and/or month pillar when the birth instant is within 30 minutes of the jie that decided it (or of the next one).
- Without a time: compute as above at 12:00 local, `hour = None`. If any jie moment falls within that local calendar date, set `depends_on_time` on the month pillar, and on the year pillar too when that jie is Lichun.

- [ ] **Step 1: Generate chart references.** Add a `charts` sub-command to the script that prints the four pillars from `lunar-python` (`Solar.fromYmdHms(...).getLunar().getEightChar()`, sect 2 for the 23:00 rule) for: 1984-02-04 at 30 minutes before and after Lichun (WIB), a Jingzhe-day birth either side of the term, 1995-12-31 23:59, 1996-01-01 00:30, 1990-06-15 22:59 and 23:00, 2000-01-01 12:00, 1988-08-08 08:08 WITA, 2001-11-22 05:45 WIT. Convert local times to the UTC+8 lunar-python expects. Run it and paste the results as `REFERENCE_CHARTS` with a comment naming lunar-python and its version.

- [ ] **Step 2: Write the failing tests** in `tests/test_bazi_pillars.py`:

```python
def test_day_cycle_anchors():
    assert day_pillar(date(2000, 1, 1)).index == 54   # 戊午
    assert day_pillar(date(1949, 10, 1)).index == 0   # 甲子

def test_1984_after_lichun_is_jia_zi_year():
    chart = chart_for(date(1984, 3, 10), time(12), "WIB")
    assert (chart.year.stem, chart.year.branch) == (0, 0)

def test_five_tigers_and_five_rats():
    chart = chart_for(date(1984, 3, 10), time(0, 30), "WIB")  # Jia year, Mao month (after Jingzhe)
    assert (chart.month.stem, chart.month.branch) == (3, 3)   # 丁卯
    assert chart.hour.branch == 0 and chart.hour.stem == (2 * (chart.day.stem % 5)) % 10

@pytest.mark.parametrize(("birth_date", "birth_time", "zone", "expected"), REFERENCE_CHARTS)
def test_charts_match_the_reference(birth_date, birth_time, zone, expected):
    chart = chart_for(birth_date, birth_time, zone)
    assert [(p.stem, p.branch) for p in (chart.year, chart.month, chart.day, chart.hour)] == expected

def test_23_00_starts_the_next_day():
    late = chart_for(date(1990, 6, 15), time(23, 30), "WIB")
    assert late.day.index == day_pillar(date(1990, 6, 16)).index
    assert late.hour.branch == 0
    assert late.hour.stem == (2 * (late.day.stem % 5)) % 10

def test_lichun_day_without_time_is_flagged_not_guessed():
    chart = chart_for(date(2026, 2, 4), None, "WIB")
    assert chart.hour is None
    assert chart.year.depends_on_time and chart.month.depends_on_time

def test_an_ordinary_day_without_time_has_no_flags():
    chart = chart_for(date(2026, 3, 1), None, "WIB")
    assert not chart.year.depends_on_time and not chart.month.depends_on_time

def test_a_birth_near_a_term_is_flagged():
    lichun = term_moment(2026, 315).astimezone(timezone(timedelta(hours=7)))
    chart = chart_for(lichun.date(), (lichun + timedelta(minutes=10)).time(), "WIB")
    assert chart.month.near_term and chart.year.near_term

def test_element_counts_cover_present_pillars_only():
    assert sum(chart_for(date(2026, 3, 1), None, "WIB").element_counts) == 6
    assert sum(chart_for(date(2026, 3, 1), time(9), "WIB").element_counts) == 8
```

- [ ] **Step 3: Run** `uv run pytest tests/test_bazi_pillars.py -v`. Expected: FAIL (import error).
- [ ] **Step 4: Implement** `pillars.py` per the Interfaces and Algorithm above.
- [ ] **Step 5: Run** `uv run pytest tests/test_bazi_pillars.py tests/test_bazi_solar.py -v` and ruff. Expected: all PASS, clean. If a reference chart disagrees, check the reference's zone conversion before the engine.
- [ ] **Step 6: Commit** (local): `feat(api): Ba Zi four pillars, with birth-time and solar-term flags`.

---

### Task 3: Relations, compatibility and the date check

**Files:**
- Create: `apps/api/app/domains/bazi/relations.py`, `apps/api/app/domains/bazi/service.py`
- Test: `apps/api/tests/test_bazi_relations.py`

**Interfaces:**
- Consumes: `Chart`, `Pillar`, `day_pillar` from Task 2.
- Produces:
  - `Rule = Literal["six_combination", "half_harmony", "clash", "harm", "stem_combination", "generates", "controls", "same_element"]`
  - `Kind = Literal["harmony", "caution", "clash", "neutral"]`
  - `branch_rules(a: int, b: int) -> list[Rule]`: arithmetic forms: clash `(a − b) % 12 == 6`; six combination `(a + b) % 12 == 1`; harm `(a + b) % 12 == 7`; half harmony `a != b and a % 4 == b % 4 and (a in {0, 3, 6, 9} or b in {0, 3, 6, 9})`
  - `stem_rules(a: int, b: int) -> list[Rule]`: stem combination `(a − b) % 10 == 5`; plus exactly one of `generates` (either direction, `(ea + 1) % 5 == eb` or reverse), `controls` (`(ea + 2) % 5 == eb` or reverse), `same_element`, using elements `stem // 2`
  - `RULE_KIND: dict[Rule, Kind]`: combination, half_harmony, stem_combination, generates → harmony; harm, controls → caution; clash → clash; same_element → neutral
  - `@dataclass(frozen=True) class Finding: rule: Rule; kind: Kind; pillar: Literal["year", "day", "day_master"]; a: int; b: int; source: int | None = None`: `a`/`b` are the first and second partner's branch (or, for `day_master`, stem) indices; `source` is the partner (0 or 1) who generates or controls the other, `None` for every other rule
  - `Tone = Literal["harmony", "balanced", "clash"]`
  - `@dataclass(frozen=True) class Compatibility: tone: Tone; findings: list[Finding]`
  - `compatibility(first: Chart, second: Chart) -> Compatibility`: year branch vs year branch, day branch vs day branch, day master vs day master
  - `Verdict = Literal["safe", "consider", "clash"]` (rendered as aman / perlu dipertimbangkan / bentrok)
  - `@dataclass(frozen=True) class DateReason: partner: int; against: Literal["shio", "day"]; rule: Rule`
  - `@dataclass(frozen=True) class DateCheck: day: date; pillar: Pillar; verdict: Verdict; reasons: list[DateReason]`
  - `check_date(day: date, charts: tuple[Chart, Chart]) -> DateCheck`

Tone rule (spec, our call): any `clash` finding on the `day` pillar → `clash`; else harmonies > (clashes + cautions) → `harmony`; else `balanced`. Verdict: any clash in reasons → `clash`; else any harm → `consider`; else `safe` (reasons still list combinations and half harmonies).

- [ ] **Step 1: Write the failing tests:**

```python
def test_each_branch_has_exactly_one_clash_and_one_combination():
    for a in range(12):
        assert sum("clash" in branch_rules(a, b) for b in range(12)) == 1
        assert sum("six_combination" in branch_rules(a, b) for b in range(12)) == 1
        assert sum("harm" in branch_rules(a, b) for b in range(12)) == 1

def test_the_classical_pairs():
    assert branch_rules(0, 6) == ["clash"]                 # 子午
    assert branch_rules(2, 11) == ["six_combination"]      # 寅亥
    assert branch_rules(0, 7) == ["harm"]                  # 子未
    assert "half_harmony" in branch_rules(8, 0)            # 申子
    assert "half_harmony" not in branch_rules(8, 4)        # 申辰 without 子

def test_stem_relations():
    assert "stem_combination" in stem_rules(0, 5)          # 甲己
    assert "generates" in stem_rules(0, 2)                 # wood feeds fire
    assert "controls" in stem_rules(0, 4)                  # wood controls earth
    assert "same_element" in stem_rules(0, 1)

def test_a_day_branch_clash_sets_the_clash_tone(): ...    # build charts with day branches 0 and 6
def test_identical_charts_are_balanced():
    chart = chart_for(date(1995, 5, 5), time(10), "WIB")
    result = compatibility(chart, chart)
    assert result.tone == "balanced"
    assert all(f.rule != "clash" for f in result.findings)
    assert any(f.rule == "same_element" for f in result.findings)

def test_a_date_clashing_with_either_shio_is_a_clash():
    # the check date's day branch clashes with partner 2's year branch
    ...
    assert check.verdict == "clash"
    assert DateReason(partner=1, against="shio", rule="clash") in check.reasons

def test_a_harm_only_date_needs_consideration(): ...
def test_a_quiet_date_is_safe_and_lists_its_harmonies(): ...
```

Pick dates for the date-check tests by computing `day_pillar` in the test (search a 60-day window for the needed branch) rather than hard-coding.

- [ ] **Step 2: Run** `uv run pytest tests/test_bazi_relations.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement** `relations.py` (rules, `RULE_KIND`) and `service.py` (`compatibility`, `check_date`, plus `chart` re-exported from pillars).
- [ ] **Step 4: Run** the three bazi test files and ruff. Expected: PASS, clean.
- [ ] **Step 5: Commit** (local): `feat(api): Ba Zi compatibility findings and the date clash check`.

---

### Task 4: Endpoint, labels and the `bazi` lead

**Files:**
- Create: `apps/api/app/domains/bazi/labels.py`, `apps/api/app/domains/bazi/schemas.py`, `apps/api/app/api/v1/public/bazi.py`
- Modify: `apps/api/app/api/v1/router.py` (include the router at `/public`), `apps/api/app/schemas/content.py` (`WeddingTool = Literal["mahar", "hashtag", "bazi"]`), `apps/api/app/services/leads.py` (`TOOL_LABELS["bazi"] = "Ba Zi"`)
- Test: `apps/api/tests/test_bazi_api.py`, `apps/api/tests/test_tool_leads.py`

**Interfaces:**
- Consumes: `chart_for`, `compatibility`, `check_date` and the dataclasses from Tasks 2–3.
- Produces the wire shape the web relies on (snake_case):

```
BaziRequest:   partners: list[PartnerIn] (exactly 2), dates: list[date] (0..3, default []), locale: "id" | "en" = "id"
PartnerIn:     name: str | None (max 40), birth_date: date, birth_time: time | None, zone: "WIB" | "WITA" | "WIT" = "WIB"
StemOut:       index, char, pinyin, element ("wood"...), element_label, yang: bool
BranchOut:     index, char, pinyin, element, element_label, animal ("rat"...), animal_label
PillarOut:     stem: StemOut, branch: BranchOut, depends_on_time: bool, near_term: bool
ChartOut:      name, year, month, day: PillarOut, hour: PillarOut | None, day_master: StemOut,
               shio: BranchOut, elements: dict[str, int] (keys wood, fire, earth, metal, water)
FindingOut:    rule, rule_label, kind, pillar ("year" | "day" | "day_master"), a, b (chars), source: int | None
DateReasonOut: partner (0 | 1), against ("shio" | "day"), rule, rule_label
DateCheckOut:  date, pillar: PillarOut, verdict ("safe" | "consider" | "clash"), reasons: list[DateReasonOut]
BaziResponse:  charts: list[ChartOut] (2), tone, tone_label, findings: list[FindingOut], date_checks: list[DateCheckOut]
```

- `labels.py`: `STEMS` (char, pinyin), `BRANCHES` (char, pinyin, animal key); `label(kind: str, key: str, locale: Locale) -> str` with id/en tables. Indonesian: elements Kayu, Api, Tanah, Logam, Air; animals Tikus, Kerbau, Macan, Kelinci, Naga, Ular, Kuda, Kambing, Monyet, Ayam, Anjing, Babi; tones "Banyak keselarasan", "Seimbang", "Ada bentrok yang perlu dibicarakan". Rule labels: id "Kombinasi Enam (Liu He)", "Setengah Tiga Harmoni (San He)", "Benturan (Chong)", "Celaka (Hai)", "Kombinasi Batang (He)", "Saling menghidupi", "Saling mengendalikan", "Unsur sama"; English equivalents.
- Router `POST /bazi`, `response_model=BaziResponse`, sync computation (no DB session). Validation in the schema: years 1900–2100 for every date, exactly two partners, at most three dates; 422 otherwise. Module docstring: stores nothing, POST so birth data stays out of URLs and logs.

- [ ] **Step 1: Write the failing tests** in `tests/test_bazi_api.py` (uses the `api` fixture from `conftest.py`, `api.client.post`):

```python
ENDPOINT = "/api/v1/public/bazi"

def test_two_partners_get_two_charts_and_a_tone(api): ...   # 200; len(charts) == 2; tone in {...}; day_master has element_label
def test_labels_follow_the_locale(api): ...                  # same body, locale en → animal_label "Rat"-style, id → "Tikus"
def test_a_missing_time_returns_no_hour_pillar(api): ...
def test_dates_come_back_checked_in_order(api): ...          # 2 dates → 2 date_checks, same order, verdict keys only
def test_no_dates_means_no_date_checks(api): ...
@pytest.mark.parametrize("body", [one_partner, four_dates, feb_30, year_1899, bad_zone])
def test_bad_input_is_a_422(api, body): ...
def test_nothing_is_stored(api): ...                         # ContactLead count unchanged after a call
```

and in `tests/test_tool_leads.py`, mirroring the hashtag test:

```python
def test_a_bazi_lead_is_stored_and_labelled_as_the_bazi_tool(api, recorder) -> None:
    # tool="bazi", inputs={"shio": "Tikus / Kuda", "tone": "balanced", "dates": "2026-09-20:safe"}
    # assert lead.source == "tool_bazi" and "Wedding tool: Ba Zi" in the label, as the hashtag test does
```

- [ ] **Step 2: Run** `uv run pytest tests/test_bazi_api.py tests/test_tool_leads.py -v`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** labels, schemas, router, and the two one-line lead changes (`npx gitnexus impact ToolLeadCreate` first; additive, same as hashtag).
- [ ] **Step 4: Run** the full suite `uv run pytest` and `uv run ruff check .`. Expected: all pass (374 + new), clean.
- [ ] **Step 5: Commit** (local): `feat(api): public Ba Zi endpoint and the tool_bazi lead`.

---

### Task 5: Web client and proxy

**Files:**
- Create: `apps/web/src/routes/api/bazi/+server.ts`, `apps/web/src/lib/tools/bazi.ts`, `apps/web/src/lib/tools/bazi.test.ts`
- Modify: `apps/web/src/lib/tools/lead.ts` (`WeddingTool = 'mahar' | 'hashtag' | 'bazi'`)

**Interfaces:**
- Consumes: the wire shape from Task 4.
- Produces (in `$lib/tools/bazi`):
  - TS types mirroring Task 4: `BaziRequest`, `PartnerIn`, `ChartOut`, `PillarOut`, `FindingOut`, `DateCheckOut`, `BaziResponse`, `Verdict`, `Tone`, `Zone`
  - `fetchBazi(body: BaziRequest, fetcher?: typeof fetch): Promise<BaziResponse>`: posts to `/api/bazi`, throws `BaziUnavailableError` on network failure or 5xx, `BaziInputError` on 422
  - `baziLeadInputs(result: BaziResponse): Record<string, string>`: keys `shio`, `day_masters`, `tone`, `dates` ("2026-09-20:safe,2026-10-10:clash"), never a birth date or time
  - `isCompleteBirth(partner: PartnerIn): boolean`: has a valid ISO `birth_date` in 1900–2100

`+server.ts` is a copy of the `tool-lead` proxy pointed at `${getApiBaseUrl()}/api/v1/public/bazi`, with the same 400/502 handling and its own docstring.

- [ ] **Step 1: Write the failing tests** in `bazi.test.ts`:

```ts
it('builds lead inputs without any birth data', () => {
  const inputs = baziLeadInputs(SAMPLE_RESPONSE);
  expect(Object.keys(inputs).sort()).toEqual(['dates', 'day_masters', 'shio', 'tone']);
  for (const birth of SAMPLE_BIRTH_DATES) expect(JSON.stringify(inputs)).not.toContain(birth);
  expect(inputs.dates).toBe('2026-09-20:safe,2026-10-10:clash');
});
it('turns a 502 into BaziUnavailableError', async () => { /* fetcher returning status 502 */ });
it('turns a 422 into BaziInputError', async () => { /* fetcher returning status 422 */ });
it('rejects a birth year outside 1900-2100', () => { expect(isCompleteBirth({ birth_date: '1899-12-31', birth_time: null, zone: 'WIB' })).toBe(false); });
```

- [ ] **Step 2: Run** `pnpm --filter @7magic/web test -- bazi`. Expected: FAIL.
- [ ] **Step 3: Implement** `bazi.ts`, the proxy, and the `WeddingTool` union change.
- [ ] **Step 4: Run** `pnpm --filter @7magic/web test` and `pnpm --filter @7magic/web check`. Expected: PASS, 0 errors.
- [ ] **Step 5: Commit** (local): `feat(web): Ba Zi API client, proxy and lead inputs`.

---

### Task 6: Page, copy and card

**Files:**
- Create: `apps/web/src/routes/wedding-tools/kalkulator-bazi-pasangan/content.ts`, `.../+page.svelte`, `apps/web/src/lib/components/tools/BaziCard.svelte`

**Interfaces:**
- Consumes: `fetchBazi`, `baziLeadInputs`, `isCompleteBirth`, types from Task 5; `ToolShell`, `LeadGate` (`tool="bazi"`), `DateField`, `SocialMeta`, `toolPageJsonLd`, `isUnlocked`, `card-export` exactly as the hashtag page uses them.
- Produces: `TOOL_PATH = '/wedding-tools/kalkulator-bazi-pasangan'` and `baziCopy(locale)` from `content.ts`; `BaziCard` with `downloadPng()` and `print()` like `HashtagCard`.

Follow `generator-hashtag-pernikahan/` for structure, comments and copy shape. Requirements:
- **Inputs** per partner: name (optional, maxlength 40), birth date (`DateField`), birth time (optional, with a "tidak tahu jam lahir" checkbox that clears it; hint: lahir pukul 23.00 ke atas wajib isi jam), zone select WIB/WITA/WIT default WIB. Calculation runs on a button press, not on every keystroke; inputs survive an error.
- **Free result:** two chart panels side by side from `md:` and stacked on phones; four pillars each showing the stem and branch characters, pinyin, element label (an element colour per element, builder's palette) and the animal; "jam tidak diketahui" in place of a missing hour; a visible note on any `depends_on_time` or `near_term` pillar. Day master and shio called out. Element balance as five small bars. Tone headline (`tone_label`) and findings, each with a one-line plain reading from `content.ts` keyed by `rule` and `pillar`.
- **Gated:** up to three candidate date fields shown to everyone; their verdicts and the card blurred until unlocked (as the hashtag card). On unlock (or when already unlocked) the page re-calls `fetchBazi` with `dates` and shows each verdict (aman / perlu dipertimbangkan / bentrok) with per-partner reasons, e.g. "Hari 午 Kuda berbenturan dengan shio Tikus Raka". The `LeadGate` receives `inputs={baziLeadInputs(result)}` after the dated call.
- **Card:** 1080 × 1350 SVG in the cream/gold style of `HashtagCard` (gradient ids `bazi-card-*`): both names, both charts' pillar characters, the tone line, checked dates with verdicts. PNG name `bazi-<name1>-<name2>.png`.
- **Copy** (`content.ts`, id canonical + en): meta, form, result, the 10 day-master descriptions, readings per rule, verdict texts, the convention notes (clock time and zone, 23:00 rule, pre-1964 note, no-time behaviour), the standing "konfirmasi dengan orang tua atau ahli feng shui" note, explainer (what Ba Zi is, the four pillars, how the reading works, its limits; no numbers, nothing "lucky"), a fictional example couple with a "Coba contoh ini" button, 6–8 FAQs, 3 related links to existing articles (check slugs in the DB like the hashtag task did).
- **Errors:** `BaziUnavailableError` → retry message, inputs kept; `BaziInputError` → field message.

- [ ] **Step 1: Write** `content.ts`.
- [ ] **Step 2: Write** `BaziCard.svelte`.
- [ ] **Step 3: Write** `+page.svelte`.
- [ ] **Step 4: Run** `pnpm --filter @7magic/web check`. Expected: 0 errors.
- [ ] **Step 5: Browser check** with `./rundev.sh` (or the web dev server plus the API): fill the example; both charts render; a 23:30 birth shows the next day; a no-time Lichun-day birth shows the flag; stop the API and press calculate → retry message, inputs kept; set the unlock flag in localStorage, add two dates → verdicts and the card render without overlap; phone width (390 px) stacks the charts with no horizontal scroll. Remove the unlock flag afterwards; submit no lead.
- [ ] **Step 6: Commit** (local): `feat(web): Ba Zi compatibility page and couple chart card`.

---

### Task 7: Hub, navigation, SEO and CMS wiring

**Files:**
- Modify: `apps/web/src/routes/wedding-tools/content.ts` (key union + `'bazi'`, `BAZI_PATH`, an id and en card), `apps/web/src/routes/wedding-tools/+page.svelte` (icon in `ICONS`, comment "Three live tools today"), `apps/web/messages/id.json` / `en.json` (`tools_bazi_name`: "Kalkulator Ba Zi" / "Ba Zi Calculator"), `apps/web/src/lib/site-nav.ts` (`toolLinks()` third entry), `apps/web/src/lib/seo/static-paths.ts`, `apps/web/src/lib/seo/llms.ts` (entry: "Ba Zi compatibility calculator"), `apps/cms/src/routes/leads/+page.svelte` (`{ value: 'tool_bazi', label: 'Ba Zi tool' }`), the hub meta descriptions (id + en) to mention Ba Zi.

- [ ] **Step 1:** `npx gitnexus impact toolLinks` and `npx gitnexus impact buildLlmsTxt`; note the risk.
- [ ] **Step 2:** Make the edits, following each file's hashtag entry.
- [ ] **Step 3: Run** `pnpm --filter @7magic/web test`, `pnpm check` (web + cms), `cd apps/api && uv run pytest && uv run ruff check .`. Expected: all pass, 0 errors.
- [ ] **Step 4: Browser check:** the hub shows Ba Zi as live (3 + 3 grid), the footer lists it, `/llms.txt` and the sitemap include the path.
- [ ] **Step 5:** `npx gitnexus detect-changes --scope all --repo .`; confirm only expected symbols. Revert any CLAUDE.md/AGENTS.md rewrite by gitnexus.
- [ ] **Step 6: Commit** (local): `feat(web): list the Ba Zi tool on the hub, nav, sitemap and llms.txt`. Report to the user and push only on their go.
