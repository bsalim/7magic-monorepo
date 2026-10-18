# Wedding tools: Mahar generator, lead gate and CMS leads

**Date:** 2026-10-18 · **Status:** approved in conversation (layout B, approach A, soft gate)

## Why

Free tools earn backlinks and search traffic that articles do not, and they are
a natural place to meet couples who are planning right now. The first tool turns
a meaningful date into a mahar amount (the idea behind Andre Taulany's
Rp20.092.026). The basic result is free and public, so the page stays linkable;
a designed mahar card is unlocked with email + WhatsApp, which become leads.

Three more tools follow later with their own specs (weton/jodoh, Chinese good
dates, guest count and budget). This spec builds the shared parts once.

## Decisions taken

| Topic | Decision |
|---|---|
| URL | Hub `/wedding-tools`, tool `/wedding-tools/mahar-tanggal-pernikahan`. English under `/en/...` through the default paraglide pattern (no custom urlPatterns entry). |
| Layout | Option B: inputs on top, amount updates as you type, a live card preview with the couple's names behind a soft blur; "Buka gratis" opens the gate. |
| Gate | Soft: amount and its reading are free; the card (PNG + print/PDF) needs email + WhatsApp + consent. |
| Lead routing | Same as contact forms: saved to `contact_leads`, then the existing email to `ADMIN_EMAILS` and the WhatsApp team alert. Also listed in the CMS. |
| Card | Rendered in the browser (SVG → canvas → PNG; PDF via a print stylesheet). No server rendering, no new dependencies. |
| Date input | The existing `DateField` (bits-ui calendar in a popover, month/year dropdowns), extended with a `locale` prop so it shows Indonesian month names and a weekday label ("Minggu, 20 September 2026"). |

## Mahar methods (`apps/web/src/lib/tools/mahar.ts`)

Pure functions, no DOM, unit-tested with vitest. All amounts are whole Rupiah,
formatted `Rp20.092.026` (id) / `Rp20,092,026` (en).

1. **Tanggal akad** (default), three variants for one date:
   - `dmy`: DD MM YYYY → 20-09-2026 → **Rp20.092.026**. A leading zero falls
     away (05-09-2026 → Rp5.092.026); the reading line keeps it ("05 · 09 · 2026").
   - `ymd`: YYYY MM DD → **Rp20.260.920**.
   - `dmy_short`: DD MM YY → **Rp200.926**.
2. **Tanggal spesial**: same three variants on another date, labelled by kind:
   `jadian` (started dating), `bertemu` (first met). Kind `ulang_tahun` takes two
   birthdays and joins DDMM + DDMM: 12-05 and 03-11 → **Rp12.050.311**.
3. **Kalender Hijriah**: the akad date converted with
   `Intl.DateTimeFormat('en-u-ca-islamic-umalqura')` to day, month number and
   year, then `dmy` on those parts (8 Rabiul Akhir 1448 → **Rp8.041.448**).
   Indonesian month names: Muharram, Safar, Rabiul Awal, Rabiul Akhir, Jumadil
   Awal, Jumadil Akhir, Rajab, Sya'ban, Ramadhan, Syawal, Dzulqa'dah, Dzulhijjah.
   The page states that Umm al-Qura can differ by a day from Kemenag's calendar.
4. **Uang + emas**: cash = year × 1.000 (2026 → **Rp2.026.000**) and gold =
   DD,MM grams (20-09 → **20,09 gram**). The whole grams are split greedily into
   standard gold-bar sizes (100, 50, 25, 10, 5, 3, 2, 1 g; 20 g → 10 + 10) and
   the remainder suggested as jewellery. No prices, ever.

Added after the research (2026-10-18), all sourced in the research notes:

- Variant `dmy_unpadded` for the date methods: day and month without leading
  zeros plus the full year (3-4-2021 → Rp342.021, as Atta Halilintar did).
  Ali Syakieb's reported Rp602.021 matches no encoding of his 6-2-2021 date, so
  it is not used as an example. Chip order: dmy, dmy_unpadded, ymd, dmy_short.
- `terbilang(amount, locale)`: the amount in words, shown in the free result
  with the ijab kabul wording "dengan maskawin uang sebesar … dibayar tunai",
  so the groom can practise it. Penghulu often stumble on these numbers.
- A payment note when the amount is not a multiple of Rp100: the smallest
  denomination in circulation is Rp100, so couples usually pay such amounts by
  bank transfer.
- Examples on the page: celebrity date-number mahars with two sources each.
  Jennifer Coppen is left out (fraud reports, 9 Oct 2026).

Each method returns `{ method, variants: [{ id, amount, digits, reading, label }] }`;
the visitor picks a variant with chips, and that variant goes on the card.
Invalid or missing dates return no variants; the UI shows a hint, not an error.

## Page (`apps/web/src/routes/wedding-tools/...`)

- Server-rendered, so the explainer, worked examples and FAQ are in the HTML.
  JSON-LD: WebApplication (free offer) + FAQPage + BreadcrumbList through
  `$lib/seo/schema`. Canonical + hreflang as other bilingual pages.
- Copy lives in a per-page `content.ts` (id canonical, en translation), like
  `perjanjian-pranikah`. Facts in the explainer must be sourced (see
  `research-mahar` findings); no prices.
- Method tabs → `DateField` (or two for birthdays) → optional names → variant
  chips → amount block → `MaharCard` preview (blurred until unlocked) →
  explainer, examples, FAQ, related articles.
- Mobile-first: one column under `md`, inputs/preview side by side from `md`.

## Shared components (reused by the next tools)

- `ToolShell.svelte`: header, intro, slots for inputs/result/gate, explainer, FAQ, related.
- `LeadGate.svelte`: a bits-ui dialog (sheet on mobile) with email, WhatsApp
  (Indonesian formats normalised to `+62…`), a required consent checkbox linking
  `/privacy`, and a hidden honeypot. On success it stores
  `{ unlockedAt }` in `localStorage` under `7m_tools_unlocked` (wrapped in
  try/catch) so the visitor is not asked again on any tool, and fires a
  `generate_lead` gtag event when analytics is present.
- `MaharCard.svelte`: portrait 4:5 SVG (1080×1350), cream and gold, names (or
  "Mahar Pernikahan" when none), the date line (Masehi; plus Hijri for method 3),
  the amount (cash + gold lines for method 4), "dibayar tunai", and a small
  7magicwedding mark. Export: PNG via canvas; PDF via `window.print()` with a
  print stylesheet sized to A5.

## Lead API

`POST /api/v1/public/tool-leads` (web proxy: `POST /api/tool-lead`)

```json
{
  "tool": "mahar",
  "email": "a@b.com",
  "phone": "+6281234567890",
  "names": "Andre & Amanda",
  "inputs": { "method": "akad", "variant": "dmy", "date": "2026-09-20", "amount": 20092026 },
  "consent": true,
  "source_path": "/wedding-tools/mahar-tanggal-pernikahan",
  "website": ""
}
```

- Schema `ToolLeadCreate` in `app/schemas/content.py`: `tool` is a Literal
  (`"mahar"` for now), email validated, phone 8–20 chars after normalising,
  `names` ≤ 120, `inputs` ≤ 20 keys with scalar values, `consent` must be true,
  `website` is the honeypot: when non-empty, return 201 and store nothing.
- `LeadService.create_tool_lead`: one `ContactLead` row with
  `source="tool_<tool>"`, `full_name=names`, `email`, `mobile=phone`,
  `metadata_json={"source_path", "tool", "inputs", "consent_at"}`, committed
  before notifying; then the same email + WhatsApp notifications as contact
  leads, labelled `Wedding tool: Mahar`. Notification failures never fail the
  request.
- Response 201 `{ "ok": true }`.

## CMS leads

- Permission `lead:read`, added to `ALL_PERMISSIONS`; the endpoints require it
  **org-wide** (a branch-scoped grant is not enough), because leads are not
  branch data and hold personal details.
- `app/api/v1/admin/leads.py` (new resource router, HTTP concerns only):
  `GET /admin/leads?source=&q=&date_from=&date_to=&page=` (newest first, 50 per
  page) and `GET /admin/leads.csv` with the same filters. Queries live in
  `LeadService.list_leads` / `export_leads`.
- CMS route `/leads`: table (date, source, name, email, phone, page, details),
  source filter (all, contact form, venue pricing, each tool), search, date
  range, "Export CSV". Nav link "Leads". Read-only.

## Testing

- vitest: every method and variant, leading zeros, birthdays join, Hijri for
  known dates, gold split, formatting in both locales, invalid input.
- pytest: tool lead stored with source and metadata; honeypot stores nothing;
  consent false → 422; notifications called; admin list/CSV need org-wide
  `lead:read` (403 for branch-scoped and anonymous); filters work.
- svelte-check and the existing localized-route tests pass.

## Out of scope

The other three tools; emailing the card; editing or deleting leads in the CMS;
rate limiting beyond the honeypot.
