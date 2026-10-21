# Bali for Australians — wave 1 design

**Date:** 2026-10-21
**Status:** approved in conversation ("let's write and execute"); builder check done
**App:** `apps/web` only. No API, schema or migration changes.

## Why

The user is not happy with organic traffic and wants Australians planning a
Bali wedding (and, later, Bali events). Research on 2026-10-21 found:

- Bali/Indonesia is the #1 overseas destination for Australian couples; 4% of
  them marry overseas; an average destination wedding is A$32,060 for ~55
  guests (Easy Weddings Annual Survey 2026,
  https://assets.easyweddings.com/files/2026/02/12092848/EW-Annual-Survey-2026-LowRes.pdf).
- The results Australians get are dated or vendor-biased. The best-known
  legal guide (Wedshed) is from 2019 and quotes a CNI fee of $110 (2026 posts
  list A$181). Cost guides all recycle one Easy Weddings figure. Nobody covers
  guest logistics or the 2027 holiday clashes.
- Australians get engaged between Christmas and New Year; wedding sites peak in
  mid-January. **Wave 1 must be live by early December 2026** to be indexed in
  time.

What 7Magic has today does not serve this searcher: ~20 Bali articles are
Indonesian pieces translated into English (Rupiah budgets, Indonesian
celebrities), the Bali venue hub has 12 venues, and `/bali-wedding-planning`
has no prices or testimonials (placeholders awaiting 7Magic data).

## Goals

1. Rank in Australia for the legal, cost and timing questions, where current
   results are weakest.
2. Be the page AI assistants cite for those questions: dated, sourced, tabular,
   with FAQ blocks.
3. Turn readers into WhatsApp conversations and enquiry-form leads tagged by
   page, so the user can see which page produced each Australian lead.
4. Introduce the concierge offer as a differentiator.

## Non-goals

- Indonesian editions of these pages. They are written for Australians,
  English only, same as `/bali-wedding-planning` and
  `/wedding-planning-singapore`.
- Waves 2 and 3 (below). Listed so the structure leaves room for them.
- Any change to venue data, the API, or the lead schemas.
- Paid ads.

## Anti-goals (failure even if it ships)

- **A figure presented as 7Magic's price.** The user decided the cost guide
  and calculator use *market estimates*, and explicitly **not** 7Magic venue
  prices ("it's a bit different for the foreign market"). Every figure is a
  sourced market range, labelled as such, with an "as of" date.
- **A wrong date or legal fact.** These pages win on being correct. Nyepi,
  Galungan, Kuningan, school-holiday dates and every legal step are verified
  against an official source before publishing, and the source is linked on
  the page.
- **Offering a concierge service 7Magic cannot deliver.** Only the services
  the user ticked appear (list below).
- **Invented testimonials, prices of 7Magic packages, staff names or
  credentials.** Same rule as the existing landing pages.

## Deliverables

All URLs are English only. Paths are the route as it exists in
`src/routes`; the public URL is the `/en/` form.

| # | Public URL | Route | Kind |
|---|---|---|---|
| 1 | `/en/wedding-tools/bali-wedding-cost-calculator` | `wedding-tools/bali-wedding-cost-calculator` | Interactive tool |
| 2 | `/en/wedding-tools/bali-wedding-date-planner` | `wedding-tools/bali-wedding-date-planner` | Interactive tool |
| 3 | `/en/legally-married-in-bali` | `legally-married-in-bali` | Landing guide |
| 4 | `/en/bali-wedding-cost` | `bali-wedding-cost` | Landing guide |
| 5 | `/en/bali-wedding-concierge` | `bali-wedding-concierge` | Landing page |
| 6 | — | — | English-only route fix (below) |

Slug choice is the builder's call within these constraints: English words,
keyword-bearing, no year in the slug (the year goes in the title so the URL
survives a refresh to 2028).

### 1. Bali Wedding Cost Calculator (layout A — chosen by the user)

One screen. Inputs on the left, live result on the right, sticky from `md`;
on a phone the result sits directly under the inputs. Reuse
`$lib/components/tools/ToolShell.svelte` — it already implements exactly this
layout plus the explainer / FAQ / related-reading sections and FAQPage JSON-LD.

**Inputs**
- Guests: slider + number, 2–150.
- Setting (single choice): private villa, resort, clifftop (Uluwatu/Jimbaran),
  beach club, Ubud jungle / rice field, elopement (just the two of you, up to
  ~10). Elopement collapses the guest slider.
- Month and year: any month from now to end of 2028 (see the 2028 rule in
  deliverable 2).
- Style: simple, classic, luxe.
- Optional concierge add-ons (checkboxes), from the ticked list below. Each
  adds its own estimated line.

**Date flags shown next to the month**, from the same data as the date
planner (deliverable 2): wet season (Nov–Mar), dry-season peak, Nyepi week
(airport closed), Galungan/Kuningan, Australian school holidays (busier,
pricier). Flags inform; they do not change the number unless the source data
supports a seasonal multiplier.

**Result**
- Total as an AUD range (low–high), and per-guest range.
- Expandable breakdown: venue hire / minimum spend; food and drinks; styling and
  flowers; photo and video; ceremony, celebrant and legal paperwork; planner and
  coordination; selected add-ons. Guest travel shown separately as "your
  guests' cost, not your bill", per guest from Sydney / Melbourne / Brisbane /
  Perth.
- Fixed label: "Typical market range, not a 7Magic quote." Plus "Estimates
  checked <date>" and a sources list linking every source used.
- Primary CTA: "Get my real quote on WhatsApp" — `whatsappHref` from
  `$lib/whatsapp` with the inputs pre-filled ("55 guests, clifftop, July 2027,
  classic, add-ons: car & driver, massage").
- Secondary: an enquiry form posting to `/api/contact-lead` with
  `source_path: '/wedding-tools/bali-wedding-cost-calculator'`, inputs folded
  into `message` exactly the way `/bali-wedding-planning` does (the schema has
  no wedding columns).
- **No lead gate** (my call). `LeadGate` and `/api/tool-lead` are typed to
  `mahar | hashtag | bazi` on both sides; extending them means an API change
  this wave avoids, and an overseas couple meeting a gate on a price estimate
  is likely to leave.
- Shareable state (my call): inputs serialised into the query string so a
  couple can send the result to a partner. The page's canonical is the bare
  path; parameterised URLs must not compete with it.
- Analytics via `trackEvent` from `$lib/analytics`: one event when a couple
  first changes an input, one on each CTA click. Names in the style of the
  existing ones ("Venue Quote Requested").

**Data**
All bands live in one module (e.g. `content.ts` beside the page), each band
carrying `source` (URL + title) and `asOf` date, plus an AUD/IDR note where
a source is in Rupiah. The calculation is a pure function of
(inputs, bands) → ranges, unit-tested. No API call.

**This is an estimation model, not a lookup table** (answered by the user:
"cost guide just estimation"). Public sources will not fill a grid of six
settings × three styles × 2–150 guests, so the model is built from sourced
*anchors* and stated assumptions: per-head food and drink ranges, venue hire or
minimum-spend ranges per setting, fixed-cost lines (photo, styling, planner,
ceremony) per style, with style mapped to the low / mid / high part of each
sourced range and an optional season multiplier only if a source supports one.
Each anchor carries its source; each derived step (e.g. "classic = middle third
of the sourced range") is written down in the module and summarised on the page
under "How we estimate". A total is always shown; it is never silently missing
a line.

The anchors are **researched during implementation**, from public sources only:
the Easy Weddings 2026 survey and its Bali cost article, published resort and
venue minimum-spend / package pages (Viceroy, Belmond Jimbaran Puri, etc.),
published planner fee ranges, and published flight fare data for the travel
line. Where sources disagree, show the range they span. A *line* with no
sourced anchor at all (rather than a combination the model derives) is shown
as "quoted on request" and the total is marked "excludes <line>". Add-on lines
follow the same rule.

### 2. Bali Wedding Date Planner (2027–2028)

A tool page on `ToolShell`: pick a month (or a date) and see a month view with:
- Season (wet/dry, with the honest caveat that sources disagree on the edges).
- Balinese holidays: Nyepi (2027: **Monday 8 March**, per SKB 3 Menteri 2027;
  airport closed; Idul Fitri 10–11 March makes 6–15 March a long-weekend
  crunch), Galungan and Kuningan (2027: Galungan 13 Jan and 11 Aug, Kuningan
  23 Jan and 21 Aug — research figures, **verify against an official Bali
  calendar before publishing**), and 2028 equivalents once verified.
- Indonesian public holidays (from the SKB) that affect flights and prices.

**2028 rule (my call).** The 2028 SKB is not out yet (normally late 2027), so
2028 Nyepi and public holidays are not shown as dates; a 2028 month carries an
explicit "2028 holiday dates not yet announced — check with us" notice, never
an empty "no clashes". Galungan and Kuningan follow the fixed 210-day pawukon
cycle, so their 2028 dates may be computed from the 2027 ones and shown
labelled "provisional (calculated)". School holidays for 2028 are shown only
where a state has published them; otherwise the same "not yet announced"
notice.
- Australian school holidays for NSW, VIC, QLD, WA, SA (2027; 2028 where
  published). NSW 2027 is verified (12–23 Apr, 5–16 Jul, 27 Sep–8 Oct); the
  others must be taken from each state's education department.

Below the tool: a "best months for a Bali wedding" explainer and a table of
the key dates, which is the part AI answers will quote. CTA: "Check a date with
us on WhatsApp", pre-filled with the date. Same `source_path` tagging.

The dates live in one data module that the calculator (deliverable 1) also
imports for its flags. Each date carries its source URL.

### 3. Legal guide — "Is a Bali wedding legal in Australia? (2027 guide)"

Primary keyword: *is a bali wedding legal in australia*. Secondary: *legally
married in bali*, *certificate of no impediment bali*, *symbolic ceremony
bali*.

Content, each fact linked to its source:
- The two routes: legal ceremony in Bali, or legal at home + symbolic in Bali
  (and why many couples choose the second). An Australian celebrant can only
  marry people in Australia.
- Indonesian requirements: Marriage Law 1/1974 — same recognised religion (or
  one converts); atheist/agnostic not accepted; religious ceremony first, then
  civil registration at Dukcapil (Catatan Sipil); notice at least 10 days
  before; documents (CNI, passports, birth certificates, divorce/death papers,
  4×6 photos).
- CNI: issued by the Australian Embassy Jakarta or Consulate-General Denpasar
  (covers Bali, NTB, NTT); not accepted if more than 3 months old; fee
  (A$181 at 2026 posts — **verify the Denpasar fee and booking method**).
- Recognition in Australia (valid since 1 Jan 1995 if valid here too; cannot be
  registered in Australia; name change may need extra steps), apostille
  (Indonesia joined 4 June 2022 — **verify on the HCCH status table**).
- Same-sex couples: symbolic ceremony only.
- A timeline checklist (months before → week of).
- Facts flagged "unverified" in research (e.g. Catholic couples must marry in a
  Catholic church) are either verified from a primary source or left out.

Conversion: the user confirmed 7Magic **handles the legal paperwork** (CNI
appointment, Dukcapil registration). The page closes on "We handle the
paperwork for you" with WhatsApp and the enquiry form
(`source_path: '/legally-married-in-bali'`). Do not state a price for it.

"Last checked <date>" visible at the top. FAQPage JSON-LD.

### 4. Cost guide — "How much does a Bali wedding cost? (2027, in AUD)"

Primary: *bali wedding cost*. Secondary: *bali wedding cost for 50 guests*,
*how much is a wedding in bali aud*, *bali wedding per head*.

- Uses the **same bands module** as the calculator, so the guide and the tool
  can never disagree.
- Tables by setting and guest count (e.g. 2 / 20 / 50 / 100), a breakdown of
  where the money goes, how minimum-spend and outside-vendor fees work, hidden
  costs, guest travel shown separately, and how season moves prices.
- The same "typical market range, not a 7Magic quote" framing and sources list.
- Prominent link into the calculator; CTA to WhatsApp / enquiry form
  (`source_path: '/bali-wedding-cost'`).
- The existing Indonesian article `menikah-di-bali-budget-masuk-akal` is for a
  different reader and stays as is.

### 5. Bali Wedding Concierge

A landing page presenting the concierge services, grouped as the user saw
them, **no prices** — "ask us". Only these, as ticked by the user on
2026-10-21:

- Paperwork: legal marriage paperwork.
- Guests: airport pickups & guest shuttles; accommodation blocks; arrival help
  pack (e-VOA, levy, All Indonesia arrival card, eSIM, money); guest activities
  (day trips, spa days, surf, kids).
- Wedding week: welcome dinner & recovery brunch; Balinese blessing / melukat;
  hens & bucks in Bali.
- Before/after: pre-wedding / engagement shoot (link the existing
  `lokasi-prewedding-unik-bali` article); vow renewal / anniversary.
- During the stay: private car & driver; Balinese massage & spa; private chef /
  villa BBQ; restaurant & beach-club bookings; nanny / babysitting; yoga, surf
  & wellness; on-call doctor & pharmacy runs; holiday photographer.

**Not offered** (unticked): video venue tours, date/permission check, single
AUD invoice, guest RSVP website, proposal planning, honeymoon extension, hair &
makeup / dress care. Hair & makeup was clicked twice and ended unticked; it is
**left out** (my call, flagged to the user — adding it later is one entry in the
shared list).

Keywords: *bali wedding concierge*, *bali wedding guest transport*, *private
driver bali wedding*, *bali villa concierge wedding*. CTA: WhatsApp pre-filled
"I'd like help with: …" from the services the reader selects on the page, plus
the enquiry form (`source_path: '/bali-wedding-concierge'`).

The calculator's add-on checkboxes use this same list (one shared module).

### 6. English-only route fix

Today an English-only page is served at both `/x` and `/en/x` by the paraglide
catch-all. `/bali-wedding-planning` (verified live): `<html lang="id">` at the
root, canonical pointing at `/en/…`, and the layout's hreflang announces the
root as `id` and `x-default`. The sitemap lists both locales via
`bothLocales`. Google gets "this English page is the Indonesian edition of
itself".

Fix, applied to every English-only page — the five new ones plus
`/bali-wedding-planning` and `/wedding-planning-singapore`:
- The root form 301s to the `/en/` form (same mechanism as
  `paket-sangjit/+page.server.ts`).
- The page's load returns `alternates: { en: '/en/…' }`, which the layout
  already honours, so only `hreflang="en"` is emitted and no `x-default`
  pointing at a redirect.
- The sitemap emits only the `en` URL for these paths. A single list of
  English-only paths (next to `STATIC_PATHS`) drives the redirect check, the
  sitemap and its tests.
- **Internal links go straight to the `/en/` URL** (my call). Today the header
  (`site-nav.ts`), the footer and `llms.ts` link the root form through
  `localizeHref`, which after this change would be a redirect on every page.
  The English-only list also drives those links, and `PublicFooter.test.ts`,
  `PublicHeader.test.ts` and the llms tests are updated to expect the `/en/`
  href. `llms.ts` lists these pages as English-only, with no Indonesian URL.

`/bali-event-organizer` is bilingual and is not touched.

## Linking and discovery

- `/bali-wedding-planning` gets a "Planning from Australia" block linking all
  five pages.
- The wedding tools hub (`wedding-tools/content.ts`) gets cards for the two
  tools in its English copy. They are English-only tools, so the Indonesian hub
  either omits them or labels them as English pages — builder's call, but never
  link the Indonesian hub to a redirecting root URL.
- The five guides/tools cross-link (cost guide ↔ calculator, legal guide →
  date planner, concierge ↔ calculator add-ons).
- New paths go in `STATIC_PATHS` and `llms.txt` (`$lib/seo/llms.ts`). The
  footer test requires every static path to be one link from any page; satisfy
  it with links to the `/en/` URLs, per the internal-links rule above.
- The language switcher is hidden on English-only pages (builder's call how),
  so it never offers an Indonesian edition that redirects back.
- JSON-LD with the existing `$lib/seo/schema` builders: breadcrumb, WebPage,
  FAQPage where there is a FAQ.

## Constraints

- Svelte 5 runes, Tailwind, the existing UI components; match how
  `/bali-wedding-planning` and the Ba Zi tool are written. Copy hardcoded
  English (no paraglide messages for page copy), as on `/bali-wedding-planning`.
- Images: reuse what is in `static/img/bali/`; no new stock in this wave unless
  a page has nothing usable.
- Australian English spelling (organise, colour, favourite) on these pages.
- `pnpm check`, `pnpm --filter @7magic/web test` green. The calculator's
  math and the English-only route list get unit tests.
- The repo works directly on main. Commit to main; **ask before pushing**,
  since a push to main deploys to production through CI.

## Left to the builder

- Exact copy, headings, section order, and how many FAQ entries.
- Precise band values (from research, sourced, as above).
- Visual design within the site's existing style.
- Whether the date planner shows a month grid or a list.

## Later waves (not in this build)

- Wave 2: landing pages for elopement packages, small weddings (10–30
  guests), vow renewal; area pages for Uluwatu clifftop, Ubud jungle, beach.
  Grow the Bali venue catalogue beyond 12.
- Wave 3: guest guide article (flights from Perth/Sydney/Melbourne, e-VOA,
  levy), hens & bucks page, and research into Australian demand for Bali
  events (milestone birthdays, corporate retreats) to extend
  `/bali-event-organizer`.
