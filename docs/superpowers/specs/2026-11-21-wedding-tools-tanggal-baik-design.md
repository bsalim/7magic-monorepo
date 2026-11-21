# Tanggal Baik Tionghoa: the almanac month

**Date:** 2026-11-21 · **Status:** built · **Route:** `/wedding-tools/tanggal-baik-tionghoa`

The Wedding Tools hub announced this card as "Segera hadir" from the start, and
the Ba Zi spec left it out of scope as "a separate, later almanac tool (month
view of good days)". The owner asked for it on 2026-11-21 and chose the form:
a month calendar, personal to the couple's two shio, behind the same email gate
as Ba Zi.

## What it answers

Pick a month and both shio; see every day of that month marked **commonly
chosen**, **ordinary** or **avoided** for a wedding, with the reasons.

## Rules, and why only these

Two things, the two a printed Tong Shu shows beside every date and that every
almanac works out the same way:

| Rule | How it is computed | Effect |
|------|--------------------|--------|
| Day officer (建除十二神, Jian Chu) | `(day branch - solar month branch) mod 12` into 建除满平定执破危成收开闭 | 定 Ding, 成 Cheng, 开 Kai: favoured. 破 Po, 闭 Bi: avoided. The other seven: no verdict. |
| Clash with a shio (冲, "ciong") | The day branch against each partner's year branch, with Ba Zi's `branch_rules` | Clash: the day is avoided. Harm (六害): a favoured day drops to ordinary. Six Combination / half Three Harmony: noted, rating unchanged. |

A day is **avoided** if its officer is Po or Bi or it clashes with either shio;
**commonly chosen** if its officer is Ding, Cheng or Kai and it neither clashes
nor harms; **ordinary** otherwise.

What the officers mean for a wedding is where almanacs differ (some call Man or
Ping good, others black-path). Following the Ba Zi tool's rule of "only what the
schools broadly agree on", only the two ends get a verdict and the page says so.
Daily stars, lunar dates, the four separations and extinctions, the year
breaker, and relatives' signs are not weighed; the page lists that under "what
this tool does not weigh" and sends couples with a candidate date to Ba Zi.

**Solar months** turn at the jie terms, from Ba Zi's `solar.jie_moments`. The
day a term falls on belongs to the new month, so the officer of the day before
repeats on it. Terms are dated in UTC+8, the convention of printed almanacs,
not in the reader's zone: matching the calendar on a family's wall is the
correctness test here. Pinned in the tests against a published almanac: June
2025 has its Bi days on the 4th, 5th (Mangzhong), 17th and 29th, and 5 June
clashes the Pig.

## Shape

- **API.** `app/domains/almanac/` (`service.py` the reading, `schemas.py`,
  `response.py`), `POST /api/v1/public/almanac` with `{year, month, shio[0..2],
  locale}`. Pure calculation, nothing stored. Reuses Ba Zi's pillars, relations,
  solar terms and labels, so a date has the same day pillar on both pages.
- **Web.** `$lib/tools/almanac.ts`, the `/api/almanac` proxy, and the page with
  its `content.ts` (Indonesian canonical, English beside it). The shio are two
  pickers, not birth dates: the tool needs nothing else, and a picker sidesteps
  the Imlek-versus-Lichun question (the hint points January/February births to
  the Ba Zi calculator).
- **Gate.** As Ba Zi after 2026-11-21: the month is read first and waits blurred
  until this browser has an email on file (`7m_tools_email`); WhatsApp optional.
  The lead is the shared tool lead, `tool_tionghoa`, with the month, the two
  shio and the good days as inputs. Nothing is emailed to the couple in this
  version. `ToolLeadCreate.phone` became optional at the API for this; whether a
  gate asks for it is the page's choice (mahar and hashtag still do).
- **Registered in** the hub card, `STATIC_PATHS` (sitemap), the tools nav,
  `llms.txt`, `WeddingTool` on both sides, `TOOL_LABELS`, the CMS leads filter.

## Not in this version

Emailing the month to the couple; a lunar-date column; a year view; saving or
sharing a month by URL.
