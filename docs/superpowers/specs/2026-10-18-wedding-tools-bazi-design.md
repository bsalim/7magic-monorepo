# Wedding tools: Ba Zi compatibility and date check

**Date:** 2026-10-18 · **Status:** approved in conversation (2026-10-19)

## Why

Chinese-Indonesian couples, or couples whose parents care about it, want two
answers before a date is fixed: *do our charts suit each other*, and *does the
date we are considering clash with either of us*. Today that means a paid
consultation or a scattering of shio calculators that ignore the birth time
and the solar calendar. A careful, free Ba Zi (Four Pillars, 八字) tool is a
strong search entry point for that audience and a natural lead for the
wedding team.

The user wants the calculation built **inside the API**, as our own algorithm,
not as a call to an outside service.

## What the user decided

| Topic | Decision |
|---|---|
| Purpose | Both: couple compatibility, and checking dates they are already considering. |
| Separate tool | Ba Zi is its own tool ("more astrology"). The hub's "Tanggal Baik Tionghoa" card stays a separate, later almanac tool (month view of good days). |
| Date check | Yes: the couple enters dates they are considering and sees whether each clashes with either chart. |
| Free vs gated | Free: both charts and the compatibility reading. Behind the shared lead gate: the date check and a printable card. |
| Engine | Python in `apps/api`, written from scratch. No Ba Zi library, no outside API. |

## Goals, non-goals, anti-goals

**Goals.** Correct pillars (they must match a published reference chart for
the same birth moment), a reading a couple can understand without knowing
Chinese metaphysics, a clear clash check for candidate dates, and the same
lead flow as mahar and hashtag (`tool_bazi`).

**Non-goals.** Luck pillars (大运), annual forecasts, hidden stems, Ten Gods,
symbolic stars, useful-god analysis, a month calendar of good days (that is
the Tanggal Baik tool), lunar-date display.

**Anti-goals** (would be a failure even if it works):
- A percentage or score ("87% cocok"). It suggests precision the tradition does
  not have and is the first thing a family elder would dismiss.
- Telling a couple not to marry, or calling a date lucky or guaranteed. Every
  reading is framed as tradition and points them to their family or a master
  for the final word.
- Wrong pillars for births near a solar-term boundary or around 23:00, which
  is where cheap calculators fail and where a knowledgeable visitor checks first.

## The engine (`apps/api/app/domains/bazi/`)

New code goes in a domain package, per CLAUDE.md. Pure functions, no database.

Suggested modules (builder may adjust): `solar.py` (astronomy), `pillars.py`
(stems, branches, the four pillars), `relations.py` (clash, combine, harm,
element cycles), `service.py` (chart, compatibility, date check), `schemas.py`.

### Time

- Input is the clock time as written on the birth certificate plus the
  Indonesian zone it was in: WIB (UTC+7), WITA (UTC+8), WIT (UTC+9). Converted
  to UTC for the astronomy.
- **Our call:** standard clock time, no true-solar-time correction by longitude.
  Most Indonesian practitioners and apps read the clock time; a correction
  needs the birth city and moves a pillar only for births within about 40
  minutes of an hour boundary. The page says which convention it uses.
- **Our call:** births before Indonesia's 1988 zone change (Bali and parts of
  Kalimantan moved zones) are not special-cased; the visitor picks the zone
  their clock showed. Clocks before 1964 (Java and Sumatra on UTC+7:30, earlier
  local times) are not offered: the tool is for the couple, not their parents,
  and the page says births before 1964 may be off by a pillar near a boundary.
- **No birth time (our call).** The chart has three pillars and the hour is
  shown as unknown. The day pillar is the calendar date as entered (a 23:xx
  birth must enter its time to move to the next day; the time field's hint
  says so). If a *jie* term falls on that date, the pillars are computed at
  12:00 local, the affected pillar is marked `depends_on_time`, and the page
  asks for the time. Compatibility and the date check still run on the noon
  pillars, with the reading noting the uncertainty. One branch per pillar in
  the response, never two candidates.
- **Close to a term (our call).** With a birth time within 30 minutes of a
  *jie* term moment, the chart is computed normally and the affected pillar
  carries a `near_term` flag: birth certificates round times, and the page
  says the pillar would differ if the clock was a little off.

### Solar terms (year and month pillars)

The year starts at **Lichun** (立春, sun's apparent ecliptic longitude 315°,
about 4 February), not at Chinese New Year. Months start at the 12 *jie*
terms, every 30° from 315°:

| Branch | Starts at | Longitude |
|---|---|---|
| 寅 Yin (Tiger) | Lichun 立春 | 315° |
| 卯 Mao (Rabbit) | Jingzhe 惊蛰 | 345° |
| 辰 Chen (Dragon) | Qingming 清明 | 15° |
| 巳 Si (Snake) | Lixia 立夏 | 45° |
| 午 Wu (Horse) | Mangzhong 芒种 | 75° |
| 未 Wei (Goat) | Xiaoshu 小暑 | 105° |
| 申 Shen (Monkey) | Liqiu 立秋 | 135° |
| 酉 You (Rooster) | Bailu 白露 | 165° |
| 戌 Xu (Dog) | Hanlu 寒露 | 195° |
| 亥 Hai (Pig) | Lidong 立冬 | 225° |
| 子 Zi (Rat) | Daxue 大雪 | 255° |
| 丑 Chou (Ox) | Xiaohan 小寒 | 285° |

Sun longitude by Meeus, *Astronomical Algorithms*, ch. 25 "higher accuracy":
the Earth's heliocentric position from the abridged VSOP87 series in Meeus's
Appendix III, converted to geocentric, with nutation, aberration and ΔT
applied. That is accurate to about a second of arc, i.e. well within a minute
of the true term moment. (The low-accuracy 0.01° formula is not enough: its
~15-minute error is the size of the boundary cases this tool must get right.)
Term moments are found by iterating on the longitude. Supported birth years:
1900 to 2100.

**Acceptance:** term moments within 2 minutes of an independent reference for
a spread of years, committed in the test file with their source:
- Hong Kong Observatory's solar-term tables (times to the minute, 2013
  onwards);
- for earlier years, values computed once with Skyfield and the JPL DE421
  ephemeris by a one-off script (kept in the repo; Skyfield is a dev-only
  dependency, never imported by the app).

### Pillars

- **Year:** stem `(Y − 4) mod 10`, branch `(Y − 4) mod 12` (Jia = 0, Zi = 0),
  where Y is the Gregorian year, minus one before that year's Lichun.
- **Month:** branch from the table above. Stem by the Five Tigers rule from the
  year stem: Jia/Ji → Bing-Yin, Yi/Geng → Wu-Yin, Bing/Xin → Geng-Yin,
  Ding/Ren → Ren-Yin, Wu/Gui → Jia-Yin, then counting on.
- **Day:** the 60-day cycle runs unbroken; index `(JDN + 49) mod 60` with
  Jia-Zi = 0. Checks: 2000-01-01 is 戊午 (54); 1949-10-01 is 甲子 (0).
- **Hour:** 12 two-hour branches, Zi = 23:00–00:59. Stem by the Five Rats rule
  from the day stem: Jia/Ji → Jia-Zi, Yi/Geng → Bing-Zi, Bing/Xin → Wu-Zi,
  Ding/Ren → Geng-Zi, Wu/Gui → Ren-Zi.
- **Our call:** 23:00 starts the next day's pillar (the traditional "Zi hour
  begins the day" rule). Some schools split early/late Zi; the page notes the
  rule we follow.

**Acceptance:** at least ten full charts match a published reference (a
well-known almanac or a reference calculator the builder names in the test),
including births on a Lichun day before and after the term moment, on a
month-term day, at 22:59 and 23:00, and on 31 December / 1 January.

### Per-person chart

Returned for each partner:
- four pillars (stem and branch, with Chinese character, pinyin, element,
  yin/yang, and for branches the animal); the hour pillar may be absent;
- **day master** (the day stem): the person's element in Ba Zi;
- **shio** (year branch animal), the term Indonesian visitors know;
- **five-element count** over the visible stems and branches (main element of
  each branch only; hidden stems are out of scope), 6 or 8 characters.

### Compatibility rules

Only classical, widely agreed relations. Each finding names the two pillars
involved and the rule.

| Rule | Pairs | Reading |
|---|---|---|
| Six Combinations 六合 | Zi-Chou, Yin-Hai, Mao-Xu, Chen-You, Si-Shen, Wu-Wei | harmony |
| Half Three Harmony 半三合 (two of a trio, one being the middle branch Zi, Wu, Mao or You) | Shen-Zi-Chen, Hai-Mao-Wei, Yin-Wu-Xu, Si-You-Chou | harmony |
| Six Clashes 六冲 | Zi-Wu, Chou-Wei, Yin-Shen, Mao-You, Chen-Xu, Si-Hai | clash |
| Six Harms 六害 | Zi-Wei, Chou-Wu, Yin-Si, Mao-Chen, Shen-Hai, You-Xu | caution |
| Stem Combination 天干五合 of the day masters | Jia-Ji, Yi-Geng, Bing-Xin, Ding-Ren, Wu-Gui | harmony |
| Day-master elements | generating cycle Wood→Fire→Earth→Metal→Water→Wood; controlling cycle Wood→Earth→Water→Fire→Metal→Wood | supportive / one controls the other / same element |

Compared pairs: year branch with year branch (shio, the family side), day
branch with day branch (the spouse palace, weighted most in tradition), and
the day masters. **Our calls:** punishments (刑) are left out, since the
schools disagree on them more than on the rest; a half three-harmony counts
only when it includes the trio's middle branch (Shen-Chen alone, without Zi,
does not), the stricter and more common reading.

How the day-master relation counts towards the tone (**our call**): one
element generating the other counts as a harmony, one controlling the other
as a caution, the same element as neutral. The stem combination is a harmony
on top of that.

The overall line is one of three tones, never a number: *banyak keselarasan*
(mostly harmony), *seimbang* (mixed), *ada bentrok yang perlu dibicarakan*
(a clash worth discussing). **Our call** on the rule: any day-branch clash
gives the third tone; otherwise harmonies outnumbering clashes and cautions
(harms, a controlling day master) gives the first; else the second.

### Date check

For each candidate date (up to three), compute that day's pillar and compare
its branch with each partner's year branch and day branch:
- a clash with either → **bentrok**;
- a harm with either, no clash → **perlu dipertimbangkan**;
- otherwise → **aman**, noting any combination or harmony.

Each verdict carries a one-line reason per partner ("Hari 午 Kuda berbenturan
dengan shio Tikus Raka"). The check never says *lucky*.

## API

- `POST /api/v1/public/bazi` in a new router module
  `app/api/v1/public/bazi.py` (resource-per-module, like `public/tour.py`).
  POST, not GET, so birth dates never sit in URLs or access logs.
- Body (snake_case): `partners` (exactly two of `{ name?, birth_date,
  birth_time?, zone }`), optional `dates` (up to three ISO dates), `locale`.
- Response: both charts, the compatibility findings and tone, and
  `date_checks` when dates were sent. Text labels (element names, animal names,
  rule names) come back in the requested locale; longer reading copy lives on
  the web page.
- Stores nothing and logs no birth data. Validation rejects years outside
  1900–2100 and impossible dates.
- The web page calls it through a SvelteKit proxy (`/api/bazi`), the same
  pattern and reason as `/api/tool-lead`.
- **Gate:** soft, like the other tools, and the API does not enforce it. The
  visitor types the candidate dates first; the verdicts and the card are
  blurred until unlock, then the page sends `dates` and shows them. So the
  lead can carry the dates.
- **Our call:** one unlock still opens every tool (the shared flag in
  `$lib/tools/lead`). A visitor who unlocked on mahar or hashtag sees the date
  check straight away and creates no `tool_bazi` lead; storing contact details
  in the browser to send a second lead is not worth the privacy cost.

## Page

`/wedding-tools/kalkulator-bazi-pasangan` (English under `/en/...`). Mirrors the
mahar and hashtag pages: `ToolShell`, `content.ts` with id + en copy,
`toolPageJsonLd`, explainer, a fictional example couple, FAQ, related
articles.

- **Inputs:** for each partner a name (optional, used in the reading), birth
  date, birth time (optional, with "tidak tahu"), zone (WIB/WITA/WIT, default
  WIB).
- **Free result:** two chart cards side by side (stacked on phones) showing
  the four pillars with characters, element colours, day master and shio;
  the element balance; the compatibility tone and findings, each with a
  short plain-language line.
- **Gated:** the date check (up to three dates) and a printable couple chart
  card (4:5 PNG and A5 print, same card style as mahar and hashtag).
- **Copy:** Indonesian first. Short descriptions for the 10 day masters, the
  5 element relations and each rule, framed as tradition ("menurut tradisi
  Ba Zi…"). A standing note that families usually confirm with an elder or a
  feng shui master.
- **Lead:** `tool_bazi`. **Our call on privacy:** the lead's `inputs` carry the
  candidate dates, both shio and day masters and the tone, but not the full
  birth dates or times; the team can ask for those in conversation.

## Wiring

Same list as the hashtag tool: `WeddingTool` Literal and `TOOL_LABELS` get
`bazi`; the CMS leads filter gets `tool_bazi`; `$lib/tools/lead` type; a sixth
hub card (live), `toolLinks`, `STATIC_PATHS`, `llms.txt`, and a
`tools_bazi_name` message. Hub grid stays three columns: 3 + 3.

## Left to the builder

Module split inside the domain package, response field names, the card's
layout, element colours, the example couple's details, FAQ wording, related
article choice (from articles that exist), and whether the API computes
term moments on demand or caches them per year.

## Out of scope

The Tanggal Baik Tionghoa month calendar, the weton tool, luck pillars and
anything beyond the rules above, true-solar-time correction, storing charts.
