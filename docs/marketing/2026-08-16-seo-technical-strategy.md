# SEO Technical Strategy — 7Magic

**Date:** 2026-08-16
**Target query:** `paket wedding jakarta`
**Status:** Audit complete, nothing implemented. Read from `apps/web` at commit `6b1838c`.
**Companion doc:** `ads/2026-08-01-google-ads-plan.md` — the paid side of the same keyword set.

## Objective

Rank organically for `paket wedding jakarta` and the budget-qualified family around
it (`paket wedding 50 juta jakarta`, `paket pernikahan 300 undangan`), where the
paid research already found empty auctions and uncontested long tail.

## What was verified, and what was not

Everything in the findings below was read directly out of `apps/web`: route
structure, head tags, canonical and hreflang emission, sitemap and robots
construction, the JSON-LD builders, rendering mode, and price rendering on both
the venue card and the venue detail page.

**No live SERP positions, no search volumes, no Core Web Vitals field data.**
Keyword Planner was opened this session but never queried — the account went
straight into campaign setup instead. Competition claims are carried over from
the 2026-08-01 ads research and were not re-checked. Timelines in the sequence
are typical ranges for a site this size, not commitments.

## Finding 1 — nothing on the site targets the query

`src/routes/wedding-venue/[city]/` contains only a `[slug]` directory. There is no
`+page.svelte` at the city level, and none at `/wedding-venue` either. So:

| URL | Today |
|---|---|
| `/wedding-venue/jakarta` | 404 |
| `/wedding-venue` | 404 |
| `/wedding-venue/search` | the only listing page |

`/wedding-venue/search` is a filter interface. Its `pageTitle` is
`'Wedding Venue Search'` and its H1 is *"Find the right package shortlist"* —
English, on a site where Indonesian is canonical, carrying no city and no price
language at all. It matches neither `paket wedding jakarta` nor anything adjacent.

This is the whole problem. Every other fix in this document is real but secondary;
Google cannot rank a page that was never built.

A second cost: the 121 venue detail pages have no hub to link up into, so their
internal link equity dead-ends instead of concentrating anywhere that could rank.

## Finding 2 — faceted URLs are indexable duplicates

`?q=`, `?city=`, `?stars=` and `?page=` combine freely on the search page. No page
emits a self-referencing canonical, and nothing emits a robots directive.

Only the venue detail pages and two standalone landing pages
(`perjanjian-pranikah`, `bali-wedding-planning`) set `rel="canonical"` at all. The
layout emits hreflang and nothing else — see `+layout.svelte:40-45`. Every filter
combination is therefore a crawlable near-duplicate competing with its own parent.

## Finding 3 — a price outlier is being published as structured data

`venuePackageNode` in `src/lib/seo/schema.ts` emits `lowPrice` straight from
`price_start_from`. `Yello Hotel Harmoni` carries `950,000,000` — a budget brand
priced above every five-star in the set, and almost certainly a data-entry error
(already noted in the ads plan).

That number currently goes to Google as a factual price claim inside an
`AggregateOffer`. Audit the outliers at both ends before this feeds any rich
result, and consider a sanity bound in the service layer.

## Finding 4 — price intent still lands on a gated page

Venue cards do render `formatPrice(venue.price_start_from)`. The detail page routes
the real number through `VenueQuoteModal` instead. Bridestory's snippet shows
`IDR 228,000,000` in the SERP itself.

Nearly every query in this cluster is a `harga` / `biaya` / `berapa` question. The
result that answers it in the snippet wins the click. Unchanged from the ads plan,
where it is also the launch blocker.

## Finding 5 — smaller items

| Severity | Item | Where |
|---|---|---|
| Medium | No `og:` or `twitter:` tags anywhere. Venue pages share blank on WhatsApp, which is how a shortlist actually circulates between a couple and their families. | zero matches in `src/` |
| Medium | `STATIC_PATHS` has no city URLs to list, because none exist. The list is deliberately hand-maintained, so new hubs must be added — better, generated from the payload's distinct cities. | `sitemap.xml/+server.ts:25` |
| Low | `<meta name="keywords">` on the homepage. Ignored by Google since 2009, and it publishes the keyword targets to competitors for free. | `+page.svelte:97` |

## What is already right

Worth stating, because it means the work ahead is additive rather than remedial.

- **Everything renders server-side.** No route sets `ssr = false`.
- **The sitemap is built per request**, walks every paginated endpoint to the end,
  and degrades section-by-section rather than failing whole.
- **hreflang and `x-default` are correct** — absolute URLs, and the `/en/` redirect
  resolved before emission rather than on every crawl.
- **Structured data is good.** `schema.ts` ships Organization, WebSite,
  EventVenue/Hotel, Product with AggregateOffer, BreadcrumbList and BlogPosting,
  with the `<`-escaping and absolute-`@id` traps already handled.
- **Images are responsive webp/jpeg variants on R2** — most of Core Web Vitals won
  before starting.

## The page that ranks for this query

Build it inside the existing IA. `/paket-wedding-jakarta` reads closer to the
query, but the city hub inherits inbound internal links from 61 venue pages and
their breadcrumbs, and internal links are the lever we control.

**`/wedding-venue/jakarta`**

1. **H1 in Indonesian, containing the query.** *"Paket Wedding Jakarta — 61 Venue
   dengan Harga Mulai Rp X"*. One H1, and the only place the exact phrase needs to
   appear verbatim.
2. **A price table above the fold** — venue, district, capacity, *mulai dari*.
   This is the asset Bridestory outranks us with, and we hold better data than
   they publish.
3. **Budget bands as real sections** — under 50jt, 50–100jt, 100–200jt, 200jt+ —
   each linking to the filtered view. These map onto the `paket wedding 50 juta`
   family, which is where the cheap high-intent volume sits.
4. **District sub-groupings** — Jakarta Selatan, Pusat, Barat, Utara, Timur. Real
   subheadings, because that is how couples here narrow a shortlist.
5. **An FAQ block with `FAQPage` schema** answering the actual questions —
   *berapa biaya resepsi 300 undangan*, *apa saja yang termasuk paket all-in*.
   Cheap to write, and it competes for People Also Ask.
6. **CollectionPage + ItemList + BreadcrumbList** JSON-LD. `venueItemList()` and
   `breadcrumbList()` already exist — no new schema code required.
7. **600–900 words of genuine Indonesian prose** on what a Jakarta package
   includes and excludes. This is what separates a hub page from a directory
   listing.
8. **Breadcrumbs on the 61 venue pages point up into it**, turning the hub from an
   orphan into the best-linked page on the site.

Tangerang, Bekasi and Bogor follow the same template for free.

## Outside the codebase

- **Google Business Profile is the highest-return item here.** The ads research
  found `gedung pernikahan jakarta` and `wedding organizer jakarta` returning a
  Local Pack with no ads at all. The pack sits above every organic result and
  costs nothing to compete in.
- **Bridestory holds organic rank 1** on domain strength. The head term will not
  move quickly; the budget-qualified and venue-named long tail is uncontested and
  converts better anyway.
- **The article inventory already exists.**
  `intimate-wedding-100-tamu-jakarta-rincian-biaya` and its neighbours are exactly
  the supporting content a hub needs. They need Indonesian anchor text pointing
  into the hub — and their prices verified first, since ids 122–145 still carry
  model-estimated figures.

## Sequence

| Phase | When | Work |
|---|---|---|
| 1 | Week 1 | Surface `mulai dari Rp X` in crawlable HTML on detail pages; audit price outliers. Until this ships, ranking for price queries only buys bounces. Display change, not a data one. |
| 2 | Week 1–2 | Build `/wedding-venue/[city]/+page.svelte` to the spec above. Add cities to the sitemap. Point venue breadcrumbs at it. Jakarta first. |
| 3 | Week 2 | Self-referencing canonical in the layout; facet handling on the search page; search page copy into Paraglide, Indonesian written first; OG tags; delete meta keywords. |
| 4 | Week 3+ | Link existing articles into the hub with Indonesian anchor text. Complete and review the Google Business Profile. |

## Measurement

| Signal | Where | Expect by |
|---|---|---|
| Hub page indexed | Search Console · URL Inspection | 3–10 days after ship |
| Impressions on `paket wedding jakarta` | Search Console · Queries | 2–4 weeks |
| Position enters top 20 | Search Console · avg. position | 6–12 weeks |
| ItemList / FAQ rich results valid | Rich Results Test | immediately |
| Faceted duplicates dropping out | Search Console · Pages | 4–8 weeks |
| Local Pack presence | Business Profile insights | 2–6 weeks |

## Open decisions

| Question | Owner |
|---|---|
| Does showing "mulai dari Rp X" conflict with hotel partner agreements? Blocks phase 1. | User |
| Verify the Rupiah figures in articles 122–145 before linking them into the hub | User |
| Is `Yello Hotel Harmoni` at 950jt an error, or a real number? | User |
| City hub at `/wedding-venue/jakarta` vs standalone `/paket-wedding-jakarta` | Decided — city hub, for the internal links |
