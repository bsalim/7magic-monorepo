# Bali for Australians — Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Five English-only pages for Australians planning a Bali wedding (cost calculator, date planner, legal guide, cost guide, concierge), plus a fix so English-only pages stop posing as Indonesian.

**Architecture:** All in `apps/web`. Pure data/logic modules in `src/lib/tools/` and `src/lib/` (unit-tested), one shared enquiry component, then thin route pages. A single `ENGLISH_ONLY_PATHS` list drives redirects, hreflang, sitemap, llms.txt, header/footer hrefs and the language switcher. No API changes.

**Tech Stack:** SvelteKit, Svelte 5 runes, Tailwind, paraglide (routing + nav labels only), vitest + @testing-library/svelte.

**Spec:** `docs/superpowers/specs/2026-10-21-bali-australia-hub-design.md` — read it first; this plan argues from it.

## Global Constraints

- English-only pages, Australian spelling (organise, colour). Page copy hardcoded in the route (as `/bali-wedding-planning` does), not paraglide messages. Nav labels *are* paraglide messages, in both `messages/id.json` and `messages/en.json`.
- Every money figure is a **market estimate**, never a 7Magic price and never read from the venue DB. Fixed label: "Typical market range, not a 7Magic quote."
- Every date and legal fact is verified against a primary/official source during its task, and that source URL is stored next to the value and linked on the page. A fact that cannot be verified is left out.
- Concierge offers exactly the 18 services in Task 3; nothing else.
- No invented testimonials, staff names, credentials or 7Magic package prices.
- Leads: `POST /api/contact-lead` with `{ name, phone, email?, message, source_path }`; `source_path` is the unlocalized route path; `message` ≤ 2000 chars. WhatsApp via `whatsappHref` from `$lib/whatsapp`. Analytics via `trackEvent` from `$lib/analytics`.
- CLAUDE.md: before editing an existing function/component, run `gitnexus_impact({target, direction: "upstream"})` and report it; before committing, run `gitnexus_detect_changes()`. The index is stale — run `npx gitnexus analyze --index-only` from the repo root once before Task 1.
- Commit to `main` per task. **Never push** — pushing deploys to production; the final task asks the user.
- Commands (from repo root): tests `pnpm --filter @7magic/web test`, types `pnpm check`. Baseline: 33 files / 270 tests pass.

## Review Focus

1. A shared calculator link with garbage or stale params (`?guests=-5&setting=foo&year=2019`) must render sensible defaults, never crash or show NaN — test in Task 3 (`fromQuery`).
2. An elopement URL with `guests=80` must clamp to the elopement maximum, not price 80 guests as an elopement — test in Task 3.
3. A 2028 month must never look clash-free just because 2028 holidays are unpublished — test in Task 2 (`monthFlags` notices).
4. The root (non-`/en`) form of a shared calculator URL must 301 to `/en/…` **keeping its query string** — test in Task 1.
5. The enquiry message with every add-on ticked must stay under the API's 2000-char limit and survive `&` in service names — test in Task 4.

---

### Task 1: English-only routing

**Files:**
- Create: `src/lib/seo/english-only.ts`, `src/lib/seo/english-only.test.ts`
- Create: `src/routes/bali-wedding-planning/+page.server.ts`, `src/routes/wedding-planning-singapore/+page.server.ts`
- Modify: `src/routes/sitemap.xml/+server.ts` (static entries), `src/lib/seo/llms.ts` (`link()` + the two existing entries), `src/lib/seo/llms.test.ts`
- Modify: `src/lib/components/PublicHeader.svelte`, `src/lib/components/PublicFooter.svelte` (nav `href`s), `PublicHeader.test.ts:75-77`, `PublicFooter.test.ts` (static-paths assertion)
- Modify: `src/lib/components/LanguageSwitcher.svelte`

**Interfaces:**
- Produces (all paths unlocalized, e.g. `'/bali-wedding-cost'`):
  - `ENGLISH_ONLY_PATHS: readonly string[]` — starts as `['/bali-wedding-planning', '/wedding-planning-singapore']`; later tasks append.
  - `isEnglishOnly(path: string): boolean`
  - `englishPath(path: string): string` — `localizeHref(path, { locale: 'en' })`
  - `siteHref(path: string): string` — `englishPath` for English-only paths, else `localizeHref(path)`
  - `englishOnlyLoad(path: string): ({ url }: { url: URL }) => { alternates: { en: string } }` — throws `redirect(301, englishPath(path) + url.search)` when `url.pathname !== englishPath(path)`

- [ ] **Step 1: Impact analysis.** `gitnexus_impact` upstream on `link` (llms.ts), `PublicHeader`, `PublicFooter`, `LanguageSwitcher`, the sitemap `GET`. Report blast radius.
- [ ] **Step 2: Failing tests** in `english-only.test.ts`:
  - `englishOnlyLoad('/bali-wedding-planning')({ url: new URL('https://x/bali-wedding-planning?guests=20') })` throws a redirect with `status 301`, `location '/en/bali-wedding-planning?guests=20'`.
  - Same load with `/en/bali-wedding-planning` returns `{ alternates: { en: '/en/bali-wedding-planning' } }`.
  - `siteHref('/bali-wedding-planning') === '/en/bali-wedding-planning'`; `siteHref('/paket-sangjit') === '/paket-sangjit'` (default locale id).
  - Every entry of `ENGLISH_ONLY_PATHS` has a route `+page.server.ts`: glob `/src/routes/**/+page.server.ts`, assert each path maps to one, and that the file's source contains `englishOnlyLoad` (use `import.meta.glob(..., { query: '?raw', import: 'default', eager: true })`).
- [ ] **Step 3: Run** `pnpm --filter @7magic/web test english-only` → FAIL (module missing).
- [ ] **Step 4: Implement** `english-only.ts`; add the two `+page.server.ts` files: `export const load = englishOnlyLoad('/bali-wedding-planning')` (and singapore).
- [ ] **Step 5: Wire the list through:**
  - sitemap: static entries become `{ alternates: isEnglishOnly(p) ? { en: englishPath(p) } : bothLocales(p) }` (`alternateLinks` already skips x-default without `id`; `SitemapEntry`'s "must contain `id`" comment becomes "at least one locale").
  - llms: `link()` emits `- [label](<absolute en url>): note` with no `([English](…))` suffix for English-only paths. Update the test "links every static page" to look for `](${SITE_URL}${siteHref(path)})`.
  - Header/footer: every `localizeHref(link.href)` for nav links becomes `siteHref(link.href)`. Footer test: `STATIC_PATHS.filter(p => !hrefs.includes(siteHref(p)))`. Header test lines 75-77 expect `/en/bali-wedding-planning` and `/en/wedding-planning-singapore`.
  - `LanguageSwitcher.svelte`: render nothing when `isEnglishOnly(deLocalizeHref(page.url.pathname))`.
- [ ] **Step 6: Run** full web tests + `pnpm check` → all pass.
- [ ] **Step 7: Commit** `fix(web): serve English-only pages under /en only, with en-only hreflang and sitemap` (after `gitnexus_detect_changes()`).

### Task 2: Bali dates data (`bali-dates.ts`)

**Files:** Create `src/lib/tools/bali-dates.ts`, `src/lib/tools/bali-dates.test.ts`

**Interfaces — Produces:**
```ts
export type Source = { title: string; url: string };
export type AuState = 'NSW' | 'VIC' | 'QLD' | 'WA' | 'SA';
export type BaliEventKind = 'nyepi' | 'galungan' | 'kuningan' | 'id-holiday' | 'au-school';
export type BaliEvent = {
  kind: BaliEventKind; name: string;
  start: string; end: string;          // ISO yyyy-mm-dd, inclusive
  state?: AuState;                      // au-school only
  provisional?: boolean;                // computed, not published
  note?: string;                        // e.g. "Airport closed for 24 hours"
  source: Source;
};
export type Season = 'wet' | 'dry' | 'shoulder';
export type MonthFlags = { season: Season; events: BaliEvent[]; notices: string[] };
export const BALI_EVENTS: BaliEvent[];
export const DATES_CHECKED: string;                       // ISO date of verification
export const ANNOUNCED: { idHolidays: number; auSchool: Record<AuState, number> }; // last year published
export function seasonOf(month: number): Season;           // 1–12
export function galunganDates(fromIso: string, toIso: string): string[]; // 210-day cycle
export function monthFlags(year: number, month: number): MonthFlags;
```

- [ ] **Step 1: Verify the data** (web research, primary sources only; record each URL):
  - Nyepi 2027 Mon 8 Mar (SKB 3 Menteri 2027, https://setneg.go.id/baca/index/inilah_skb_3_menteri_libur_nasional_dan_cuti_bersama_2027); all 2027 national holidays + cuti bersama from the same SKB (Idul Fitri 10–11 Mar).
  - Galungan 2027 (13 Jan, 11 Aug) and Kuningan (23 Jan, 21 Aug) against a Bali provincial / PHDI / Kemenag calendar. If none confirms, mark them `provisional`.
  - 2027 school holidays for NSW (verified: 12–23 Apr, 5–16 Jul, 27 Sep–8 Oct), VIC, QLD, WA, SA from each state education department; 2028 only if published.
  - `seasonOf`: Nov–Mar `wet`, May–Sep `dry`, Apr and Oct `shoulder` (sources disagree on the edges; say so on the pages).
- [ ] **Step 2: Failing tests:**
  - `BALI_EVENTS` has a `nyepi` event with `start === '2027-03-08'` and a non-empty `source.url`.
  - `galunganDates('2026-06-17', '2028-12-31')` equals `['2026-06-17','2027-01-13','2027-08-11','2028-03-08','2028-10-04']`.
  - Every `kuningan` event starts exactly 10 days after a `galungan` event.
  - All 2028 galungan/kuningan events have `provisional: true`.
  - `monthFlags(2027, 3).events` includes kinds `nyepi` and `id-holiday`; its `notices` is `[]`.
  - `monthFlags(2028, 6).notices` contains a string matching `/2028 holiday dates not yet announced/` (Review Focus 3).
  - `monthFlags(2027, 7)` includes an `au-school` event with `state: 'NSW'`.
  - `seasonOf(1) === 'wet'`, `seasonOf(7) === 'dry'`, `seasonOf(4) === 'shoulder'`.
  - Every event has `start <= end` and a source URL starting `https://`.
- [ ] **Step 3: Run** → FAIL. **Step 4: Implement** (galungan/kuningan for 2028 generated from `galunganDates`, everything else literal data with `source`). Notice text: `"2028 holiday dates not yet announced. Check your date with us."`; school-holiday notice per state whose `ANNOUNCED.auSchool[state] < year`.
- [ ] **Step 5: Run** → PASS. **Step 6: Commit** `feat(web): verified Bali and Australian holiday dates for 2027-2028`.

### Task 3: Concierge list and cost model

**Files:** Create `src/lib/bali-concierge.ts`, `src/lib/bali-concierge.test.ts`, `src/lib/tools/bali-cost.ts`, `src/lib/tools/bali-cost.test.ts`

**Interfaces — Produces:**
```ts
// bali-concierge.ts
export type ConciergeGroup = 'paperwork' | 'guests' | 'wedding-week' | 'before-after' | 'stay';
export type ConciergeKey = 'legal' | 'transfers' | 'accommodation' | 'arrival' | 'activities'
  | 'welcome' | 'blessing' | 'hens' | 'prewedding' | 'renewal' | 'car' | 'massage' | 'chef'
  | 'reservations' | 'nanny' | 'wellness' | 'doctor' | 'holiday-photographer';
export type ConciergeService = { key: ConciergeKey; group: ConciergeGroup; name: string; blurb: string };
export const CONCIERGE_GROUPS: { key: ConciergeGroup; title: string }[];
export const CONCIERGE_SERVICES: ConciergeService[];

// bali-cost.ts
export type Setting = 'villa' | 'resort' | 'clifftop' | 'beach-club' | 'ubud' | 'elopement';
export type Style = 'simple' | 'classic' | 'luxe';
export type City = 'sydney' | 'melbourne' | 'brisbane' | 'perth';
export type Range = { low: number; high: number };          // whole AUD
export type CostInput = { guests: number; setting: Setting; style: Style; year: number; month: number; addOns: ConciergeKey[] };
export type CostLine = { key: string; label: string; range: Range | null };  // null = "quoted on request"
export type CostEstimate = { total: Range; perGuest: Range; lines: CostLine[]; excludes: string[];
  guestTravel: Record<City, Range>; flags: MonthFlags };
export const SETTINGS: { key: Setting; label: string; maxGuests: number }[];  // elopement maxGuests 10, others 150
export const ESTIMATES_AS_OF: string;
export const COST_SOURCES: Source[];
export const METHOD_NOTES: string[];   // the "How we estimate" bullets shown on the pages
export function estimateCost(input: CostInput): CostEstimate;
export function defaultInput(today: Date): CostInput;       // 55 guests, villa, classic, July of next year, no add-ons
export function fromQuery(params: URLSearchParams, today: Date): CostInput;
export function toQuery(input: CostInput): string;
```

- [ ] **Step 1: Concierge.** Test: `CONCIERGE_SERVICES.map(s => s.key)` has exactly the 18 keys above, no duplicates, every `group` in `CONCIERGE_GROUPS`, and none of `beauty | proposal | honeymoon | video-tour | guest-site | aud-invoice | date-check`. Implement with group titles "Paperwork & planning", "Your guests", "Wedding week", "Before & after", "During your stay" and blurbs from the spec's deliverable 5. Run → PASS. Commit `feat(web): Bali concierge service list`.
- [ ] **Step 2: Research the anchors** (public sources only, each URL into `COST_SOURCES`, each derived step into `METHOD_NOTES` and a code comment): Easy Weddings 2026 survey (A$32,060 / ~55 guests) and its Bali cost article; published resort minimum spends / packages (e.g. Viceroy, Belmond Jimbaran Puri); published villa wedding hire ranges; planner fee ranges; photographer/videographer ranges; return fares SYD/MEL/BNE/PER→DPS. Convert IDR at one stated rate with its date. Add-ons with no sourced range get `null`.
- [ ] **Step 3: Failing tests** for `estimateCost`:
  - For each setting except elopement: total at 100 guests ≥ total at 30 guests (low and high).
  - `luxe.low ≥ classic.low ≥ simple.low` for villa, 55 guests.
  - `total.low === sum(lines with range).low` and same for high.
  - An add-on whose line has `range: null` appears by label in `excludes`; with no such add-on `excludes` is `[]`.
  - `perGuest.low === Math.round(total.low / guests)`.
  - Calibration: classic villa 55 guests total overlaps A$20,000–40,000.
  - `estimateCost({...,setting:'elopement', guests: 80}).perGuest` equals the result for 10 guests (Review Focus 2).
  - `flags` equals `monthFlags(year, month)`.
- [ ] **Step 4: Failing tests** for query state (Review Focus 1):
  - `fromQuery(new URLSearchParams(toQuery(x)), today)` deep-equals `x` for a valid `x`.
  - `fromQuery(new URLSearchParams('guests=-5&setting=foo&style=&year=2019&month=13&addons=car,bogus'), new Date('2026-10-21'))` returns `defaultInput` values for guests/setting/style/year/month and `addOns: ['car']`.
  - A year/month before `today`'s month falls back to the default; after 2028-12 falls back too.
- [ ] **Step 5: Run** → FAIL. **Step 6: Implement.** Model shape: venue/min-spend range per setting; food & drink per head × guests; styling, photo, ceremony (incl. legal paperwork), planner fixed per style; style picks the low/middle/high third of each sourced range; seasonal multiplier only if a source supports it. Round to nearest A$100.
- [ ] **Step 7: Run** → PASS. **Step 8: Commit** `feat(web): sourced Bali wedding cost model in AUD`.

### Task 4: Shared enquiry block

**Files:** Create `src/lib/components/bali/BaliEnquiry.svelte`, `src/lib/components/bali/BaliEnquiry.test.ts`, `src/lib/components/bali/enquiry.ts`

**Interfaces:**
- `enquiry.ts`: `export function enquiryMessage(context: string[], notes: string): string` — context lines, blank line, notes (or "No extra notes."), truncated to 2000 chars.
- `BaliEnquiry.svelte` props: `{ sourcePath: string; heading: string; context: string[]; whatsappText: string; event: string }`. Renders a WhatsApp button (`whatsappHref(whatsappText)`, fires `trackEvent(event, { channel: 'whatsapp' })`) and a form (name, phone, email optional, notes) that posts like `/bali-wedding-planning`'s `submit` (copy its error/success copy and `inputClass`), with `message: enquiryMessage(context, notes)`.

- [ ] **Step 1: Failing tests:** `enquiryMessage` with all 18 concierge names plus 6 context lines is ≤ 2000 chars and contains `Hens & bucks` unescaped (Review Focus 5); the component, with `fetch` mocked, posts JSON whose `source_path` equals the prop and whose `message` starts with the first context line; the WhatsApp link's `href` contains `encodeURIComponent('&')` for a text containing `&`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS. **Step 5: Commit** `feat(web): shared Bali enquiry block`.

### Task 5: Cost calculator page

**Files:** Create `src/routes/wedding-tools/bali-wedding-cost-calculator/{+page.server.ts,+page.svelte}`; modify `english-only.ts` (append path), `static-paths.ts`, `llms.ts`, `site-nav.ts` (`toolLinks`), `messages/{id,en}.json` (`tools_bali_cost_name`), `routes/wedding-tools/content.ts` (card key `'bali-cost'`, both hubs; hub links use `siteHref`).

**Interfaces — Consumes:** Task 1 `englishOnlyLoad`, `siteHref`; Task 2 `MonthFlags`; Task 3 `estimateCost`, `fromQuery`, `toQuery`, `defaultInput`, `SETTINGS`, `CONCIERGE_SERVICES`, `COST_SOURCES`, `METHOD_NOTES`, `ESTIMATES_AS_OF`; Task 4 `BaliEnquiry`. Path constant `'/wedding-tools/bali-wedding-cost-calculator'`.

- [ ] **Step 1:** Impact analysis on `toolLinks`, the hub `content.ts` exports, `buildLlmsTxt`.
- [ ] **Step 2:** Page on `ToolShell` (layout A): inputs snippet (guest slider+number clamped to the setting's `maxGuests`, setting chips, month select from current month to Dec 2028 with that month's flags/notices shown under it, style chips, add-on checkboxes grouped by `CONCIERGE_GROUPS`); result snippet (total, per guest, `<details>` breakdown, guest travel per city labelled "your guests' cost, not your bill", the fixed "Typical market range, not a 7Magic quote." label, "Estimates checked {ESTIMATES_AS_OF}", "excludes …" when non-empty, WhatsApp CTA via `BaliEnquiry` with context like `55 guests · Clifftop · July 2027 · Classic · Add-ons: …`). Initial state from `fromQuery(page.url.searchParams, new Date())`; on change `replaceState` to `?${toQuery(input)}` (no navigation, no history spam). `trackEvent('Bali Calculator Used')` once on first change. Explainer: "How we estimate" (`METHOD_NOTES`) and sources list (`COST_SOURCES`). 5–8 FAQs. Canonical `canonicalUrl('/en/wedding-tools/bali-wedding-cost-calculator')` — bare path, never with params. `toolPageJsonLd` with locale `'en'`. `source_path` = the path constant.
- [ ] **Step 3:** Register the path in `ENGLISH_ONLY_PATHS`, `STATIC_PATHS`, `llms.ts` (Inspiration section), `toolLinks`, hub cards.
- [ ] **Step 4: Run** full tests + `pnpm check` → PASS (static-paths, footer, llms and english-only tests now cover the page).
- [ ] **Step 5: Run the app** (`./rundev.sh`), open `https://7magic.localhost/en/wedding-tools/bali-wedding-cost-calculator`: change every input, check phone width (375px) has no horizontal scroll, `/wedding-tools/bali-wedding-cost-calculator?guests=20` 301s to `/en/…?guests=20`, view-source shows only `hreflang="en"`.
- [ ] **Step 6: Commit** `feat(web): Bali wedding cost calculator in AUD`.

### Task 6: Date planner page

**Files:** Create `src/routes/wedding-tools/bali-wedding-date-planner/{+page.server.ts,+page.svelte}`; same registrations as Task 5 (`tools_bali_dates_name`, card key `'bali-dates'`).

**Interfaces — Consumes:** Task 2 everything; Task 4 `BaliEnquiry`; Task 1 helpers.

- [ ] **Step 1:** Page on `ToolShell`: inputs = month picker (current month → Dec 2028) and optional exact date; result = that month's season, events (name, dates, `note`, "provisional (calculated)" badge, source link), notices, and for an exact date a clear verdict line ("Clashes with Nyepi — airport closed" / "No Balinese or public holiday clash found in our data"). Explainer: "Best months for a Bali wedding" + a server-rendered table of every 2027 event (the AI-citable part), "Dates checked {DATES_CHECKED}". 5–8 FAQs. CTA via `BaliEnquiry` (`context: ['Date to check: …']`, event `'Bali Date Check Requested'`).
- [ ] **Step 2:** Registrations (as Task 5 Step 3).
- [ ] **Step 3: Run** tests + check → PASS; run app, check March 2027 and June 2028 render as Task 2's tests describe, phone width OK.
- [ ] **Step 4: Commit** `feat(web): Bali wedding date planner for 2027-2028`.

### Task 7: Cost guide `/en/bali-wedding-cost`

**Files:** Create `src/routes/bali-wedding-cost/{+page.server.ts,+page.svelte}`; register in `ENGLISH_ONLY_PATHS`, `STATIC_PATHS`, `llms.ts` (Bali planning section), `site-nav.ts` (`venueRegions` → bali `packages`), `messages` (`service_bali_cost`).

- [ ] **Step 1:** Page (pattern: `/bali-wedding-planning`, `landingPageJsonLd` with FAQ). Title "How Much Does a Bali Wedding Cost? (2027, in AUD) | 7Magic". Tables generated **from `estimateCost`** (never hand-typed figures): by setting at 2/20/50/100 guests, classic style; a where-the-money-goes breakdown for 50 guests; minimum spend and outside-vendor fees explained; hidden costs; guest travel table; season effect from `seasonOf`. Same fixed label, `ESTIMATES_AS_OF`, `METHOD_NOTES`, `COST_SOURCES`. Prominent link to the calculator via `siteHref`. `BaliEnquiry` with `source_path: '/bali-wedding-cost'`.
- [ ] **Step 2: Test** (`src/routes/bali-wedding-cost/page.test.ts`): rendering the page shows the 50-guest villa total formatted exactly as `estimateCost` returns it (guards against hand-typed numbers drifting).
- [ ] **Step 3: Run** tests + check → PASS; view in app at 375px.
- [ ] **Step 4: Commit** `feat(web): Bali wedding cost guide in AUD`.

### Task 8: Legal guide `/en/legally-married-in-bali`

**Files:** Create `src/routes/legally-married-in-bali/{+page.server.ts,+page.svelte,content.ts}`; register as Task 7 (`service_bali_legal`).

- [ ] **Step 1: Verify every fact** from primary sources and store each with its URL in `content.ts` (`{ text, source }`): Embassy Jakarta marriage page (https://indonesia.embassy.gov.au/jakt/MarriageInd.html), Smartraveller marriage + CNI pages, the Denpasar consulate's CNI fee and booking method, Marriage Law 1/1974 (same religion), Dukcapil 10-day notice and documents, HCCH status table for Indonesia's apostille (4 June 2022), recognition since 1 Jan 1995, same-sex = symbolic only. Drop anything unverified (e.g. "Catholic couples must marry in a Catholic church" unless a primary source confirms). Set `LAST_CHECKED`.
- [ ] **Step 2:** Page: "Is a Bali Wedding Legal in Australia? (2027 Guide)". "Last checked {LAST_CHECKED}" at the top; two routes (legal in Bali vs legal at home + symbolic); requirements; CNI; recognition at home; same-sex; a months-before → week-of checklist; link to the date planner; close with "We handle the paperwork for you" (no price) + `BaliEnquiry` (`source_path: '/legally-married-in-bali'`). Every fact renders with its source link. `landingPageJsonLd` + FAQ.
- [ ] **Step 3: Test** (`content.test.ts`): every fact has an `https://` source; `LAST_CHECKED` is an ISO date.
- [ ] **Step 4: Run** tests + check → PASS; view in app.
- [ ] **Step 5: Commit** `feat(web): legal guide for Australians marrying in Bali`.

### Task 9: Concierge page `/en/bali-wedding-concierge`

**Files:** Create `src/routes/bali-wedding-concierge/{+page.server.ts,+page.svelte}`; register as Task 7 (`service_bali_concierge`).

- [ ] **Step 1:** Page from `CONCIERGE_GROUPS`/`CONCIERGE_SERVICES` only: each service a selectable card; selection feeds `BaliEnquiry` (`context: ['I'd like help with: …']`, WhatsApp text the same, event `'Bali Concierge Requested'`). No prices anywhere. Links: prewedding to the existing article `lokasi-prewedding-unik-bali` (English URL from the API's alternates — look it up, do not guess the en slug), the calculator ("add these to your estimate"), the legal guide. `landingPageJsonLd` with a `serviceNode` and FAQ.
- [ ] **Step 2: Test** (`page.test.ts`): renders exactly 18 service cards; selecting two puts both names in the WhatsApp href.
- [ ] **Step 3: Run** tests + check → PASS; view in app.
- [ ] **Step 4: Commit** `feat(web): Bali wedding concierge page`.

### Task 10: Hub linking and final verification

**Files:** Modify `src/routes/bali-wedding-planning/+page.svelte` (new "Planning from Australia" section linking all five pages via `siteHref`).

- [ ] **Step 1:** Impact analysis on the page; add the section near the venue section; cross-links checked: cost guide ↔ calculator, legal guide → date planner, concierge ↔ calculator.
- [ ] **Step 2: Run** full web tests, `pnpm check`, and `cd apps/api && uv run pytest` is not needed (no API change). Expected: all green, test count > 270.
- [ ] **Step 3: Live check** in the running app: each of the 7 English-only pages — root form 301s to `/en/`, only `hreflang="en"`, no language switcher, canonical correct; `/sitemap.xml` lists them once each under `/en/`; `/llms.txt` lists them; footer links are `/en/…`; phone width clean.
- [ ] **Step 4:** `gitnexus_detect_changes()`; commit `feat(web): link the Bali-for-Australians pages from Bali wedding planning`.
- [ ] **Step 5:** Report to the user and **ask before `git push`** (push deploys prod via CI).
