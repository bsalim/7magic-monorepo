# Wedding tools: hashtag generator

**Date:** 2026-10-18 · **Status:** approved in conversation ("yes" to the outline)

## Why

A couple's own wedding hashtag is one of the first things they settle once a
date is set: it goes on the invitation, the prewedding posts and a sign at the
reception so guests' photos end up in one place. It is a natural, frequently
searched free tool ("hashtag pernikahan", "wedding hashtag generator"), and the
second tool on the hub after mahar. The other three announced tools (weton,
Chinese good dates, guest count and budget) follow one at a time.

## Decisions

| Topic | Decision |
|---|---|
| URL | `/wedding-tools/generator-hashtag-pernikahan`, English under `/en/...` by the default pattern. |
| Free result | Every generated hashtag, grouped by style, each with a copy button, a "check on Instagram" link and a length warning; "copy all". |
| Gate | Same soft gate as mahar (shared `LeadGate`, one unlock for every tool). It unlocks a designed hashtag sign: 4:5 PNG for Instagram and an A5 print for the reception table. |
| Lead | `tool_hashtag` in `contact_leads`, same email + WhatsApp alerts, listed in the CMS. |
| Examples | A fictional couple only. No celebrity hashtags: they would need the two-source verification and none is needed to show the patterns. |
| Facts | No numeric claims about Instagram (hashtag limits change). The explainer gives practical advice only. |

## Generator (`apps/web/src/lib/tools/hashtag.ts`)

Pure, deterministic (so SSR and hydration agree), unit-tested.

Inputs: groom and bride nicknames (required for a result), optional family
name, optional date (ISO), optional city, a set of events (lamaran, prewedding,
sangjit, akad, pemberkatan, resepsi), and the order (groom first or bride first).

Normalising: accents stripped, anything but letters and digits dropped, each
word capitalised and joined (CamelCase reads better; hashtags are
case-insensitive). Results deduplicated case-insensitively.

Groups, each `{ id, tags: [{ tag, long }] }`:

1. `classic`: `#AB`, `#BA`, `#ADanB`, `#AAndB`, `#ABWedding`.
2. `blend`: syllable blends. `head` is the name up to its first vowel (plus the
   next consonant when the name starts with a vowel): Raka→Ra, Andre→An,
   Amanda→Am. `tail` is the last syllable: Nadia→dia, Amanda→da, Kevin→vin.
   Blends: head+head (`#RaNa`), head(A)+tail(B) (`#Radia`), head(B)+tail(A) (`#Naka`),
   plus `#{Blend}Wedding` and `#{Blend}Forever`.
3. `indonesian`: `#SahnyaAB`, `#AHalalinB` (groom halalin bride, the common
   slang), `#KisahAB`, `#ABSelamanya`, `#AkhirnyaAB`, `#{Blend}Menikah`.
4. `english`: `#ALovesB`, `#BSaidYes`, `#ABEverAfter`, `#Team{Blend}`,
   with a family name `#HappilyEverF` and `#MrAndMrsF`.
5. `date` (with a date): `#AB2026`, `#{Blend}200926`, `#{Blend}2026`, `#AB2009`.
6. `events` (per chosen event): `#ABLamaran`, `#ABPrewed`, `#ABSangjit`,
   `#ABAkad`, `#ABHolyMatrimony`, `#ABResepsi`; with a city `#ABDi{City}` and
   `#{Blend}In{City}`.

A tag longer than 24 characters is marked `long` (hard to read on a sign and
easy to mistype), not dropped. Indonesian and English groups show on both
editions: couples here mix both.

## Page

Mirrors the mahar page: `ToolShell`, a `content.ts` with id + en copy,
`toolPageJsonLd` (WebApplication + FAQPage + breadcrumbs), explainer of tips,
the fictional example, FAQ, related articles (digital invitations, wedding
content creators, photography styles). The visitor stars one tag to put on the
sign; the first classic tag by default.

## Wiring

`WeddingTool` Literal and `TOOL_LABELS` get `hashtag`; the CMS leads filter gets
`tool_hashtag`; `LeadGate`'s `tool` prop widens to a shared `WeddingTool` type
in `$lib/tools/lead`; hub card, `toolLinks`, `STATIC_PATHS` and `llms.txt` list
the page. The hub grid becomes three columns, so five cards wrap 3 + 2.

## Out of scope

Checking whether a tag is already taken (Instagram has no public API for it;
the page links to the tag's Instagram page instead), the other three tools.
