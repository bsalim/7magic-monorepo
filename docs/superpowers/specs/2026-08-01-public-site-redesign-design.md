# Public Site Redesign — The Knot-inspired Design System

**Date:** 2026-08-01
**Status:** Draft — awaiting review
**Scope:** `apps/web` only. `apps/cms` and `apps/api` are unaffected.

## Goal

Give the public site a single design system, replacing the ad-hoc utility classes and
hardcoded hex values currently scattered across every component.

The visual reference is [theknot.com](https://www.theknot.com/marketplace) — its
whitespace, photo-led layouts and card patterns — rendered in 7Magic's own gold/pink
palette rather than The Knot's pink-on-white. Typography moves to **Poppins** for
titles and **Jost** for body copy.

Today `apps/web` has no design system at all. `VenueCard.svelte` reaches for
`border-[#eadfce]` and `text-amber-500`, `PublicHeader.svelte` hardcodes `#c99d65` and
`#b8884d`, and the page backgrounds use `#fbf8f3`. Nothing is shared, so nothing is
consistent. That is the real problem this redesign solves; the new look is the visible
half of it.

## Decisions (validated with the user)

| Decision | Choice |
|---|---|
| Scope | Whole public site — every route under `apps/web` |
| Reference fidelity | The Knot's structure and spacing, **not** its colours. White base with gold and pink. |
| Palette | Gold leads (primary CTAs, ratings, premium marks); pink is the accent (secondary CTA, tags, favourites) |
| Typography | Poppins — headings, buttons, prices, numerals. Jost — body copy, labels, meta. |
| Component stack | Tailwind v4 token layer + hand-built components; `bits-ui` for interactive parts only. **Not** full shadcn-svelte. |
| Radius | Inputs/search `6px`; buttons and badges stay pill; cards `10px` |
| Venue detail layout | Photo mosaic → title block → sticky section tabs → two columns with a sticky enquiry form |
| Header + homepage | Two-row header (brand row + nav row), full-bleed hero photo with the search bar overlaid |
| CMS | Untouched. Keeps its shadcn neutral theme and Inter. |

### Why not full shadcn-svelte

The CMS uses `shadcn-svelte` + `bits-ui` because it is an interactive admin tool —
data tables, dialogs, comboboxes, date pickers. The public site is a marketing and SEO
surface whose interactive needs amount to four widgets. Adopting shadcn there would add
~10 dependencies and a neutral token vocabulary we would spend the whole project
overriding, on pages where bundle size directly affects LCP and search ranking.

`bits-ui` alone gives us the accessibility behaviour that is genuinely hard to write
(focus trapping, keyboard navigation, portalling) without the styling layer we do not
want.

## Design tokens — `apps/web/src/app.css`

Declared with Tailwind v4 `@theme`, so every token is automatically available as a
utility (`bg-gold`, `text-muted`, `rounded-input`).

### Colour

| Token | Value | Used for |
|---|---|---|
| `--color-canvas` | `#FFFFFF` | Page background. Replaces the current `#fbf8f3` cream. |
| `--color-surface` | `#FBF7F0` | Alternating section bands, subtle panels |
| `--color-ink` | `#141414` | Headings, primary text |
| `--color-muted` | `#6B6B6B` | Secondary text, meta, captions |
| `--color-line` | `#E8E8E8` | Borders, dividers, card outlines |
| `--color-gold` | `#B08542` | Primary CTA fill, active nav underline |
| `--color-gold-dark` | `#8A6524` | Gold hover, text on gold-soft |
| `--color-gold-soft` | `#FBF6EC` | Premium badge fill, star-rating chips |
| `--color-pink` | `#E5568E` | Secondary CTA border and text, favourites |
| `--color-pink-dark` | `#B8306A` | Text on pink-soft |
| `--color-pink-soft` | `#FDF1F6` | Tag fill, accent chips |
| `--color-whatsapp` | `#128C7E` | WhatsApp CTA only — never decorative |

Gold and pink are never used for body text. Both `gold-dark` on `gold-soft` and
`pink-dark` on `pink-soft` must clear WCAG AA (4.5:1) at 12px; verify during
implementation and darken the `-dark` tokens if they fall short.

### Radius

| Token | Value | Applies to |
|---|---|---|
| `--radius-input` | `6px` | Inputs, selects, textareas, the hero search bar |
| `--radius-card` | `10px` | Cards, panels, images, photo mosaic tiles |
| `--radius-pill` | `9999px` | Buttons, badges, chips |

### Typography

| Token | Value |
|---|---|
| `--font-display` | `Poppins, ui-sans-serif, system-ui, sans-serif` |
| `--font-body` | `Jost, ui-sans-serif, system-ui, sans-serif` |

Poppins is **not** a variable font, so it ships as static weights via
`@fontsource/poppins` — import 400, 500, 600 and 700 only. Jost is variable:
`@fontsource-variable/jost`. Both are self-hosted; no Google Fonts CDN request, no
third-party connection on an SEO page, no FOUT from a blocking external stylesheet.
The CMS already self-hosts Inter this way, so the pattern is established.

Type scale (display font unless noted):

| Role | Size / weight |
|---|---|
| Hero headline | 44px / 700, `-0.015em` |
| Page title (h1) | 34px / 700, `-0.015em` |
| Section heading (h2) | 24px / 700 |
| Card title (h3) | 16px / 600 |
| Body | 16px / 400 Jost, line-height 1.65 |
| Meta / label | 13px / 400 Jost, `--color-muted` |
| Eyebrow | 11px / 500 Jost, uppercase, `0.12em` |

## Components — `apps/web/src/lib/components/ui/`

Hand-built against the tokens. Each takes explicit props and carries no page-specific
logic, so pages compose them without reaching back in.

| Component | Notes |
|---|---|
| `Button` | Variants `gold`, `pink`, `whatsapp`, `ghost`; sizes `sm`, `md`, `lg`. Renders `<a>` or `<button>` by prop. |
| `Card` | Outline + `--radius-card`, optional hover lift |
| `Badge` | Variants `gold`, `pink`, `neutral` |
| `Input` / `Select` / `Textarea` | `--radius-input`, shared focus ring |
| `SectionHeading` | Title + optional subtitle + optional right-side action |
| `Breadcrumb` | Takes a `{label, href}[]` |
| `StarRating` | Renders `venue.stars` as hotel stars. **Not** a review score — see below. |
| `PhotoMosaic` | 1 large + 4 small grid, "See all (n)" overlay on the last tile, opens `Lightbox` |
| `Lightbox` | `bits-ui` Dialog — keyboard nav, focus trap |
| `SearchBar` | Segmented venue-type / city / guests fields + pill Search button |
| `Prose` | Typographic scale for article and description HTML |

`bits-ui` is used for exactly four things: **Lightbox** (Dialog), **mobile nav drawer**
(Dialog), **filter dropdowns** (Select/Popover) and **section accordions** (Accordion).
Everything else is plain markup.

### Existing components

`PublicHeader`, `PublicFooter`, `VenueCard`, `ArticleCard`, `VenueFilters`,
`HeroVenueSearch`, `VenueGallery`, `PackageTable`, `WhatsappCTA` and `StaticPage` are
all rewritten against the tokens. `PublicHeader`'s `overlay` variant is retired — the
new header sits above the hero rather than on top of it, so the white/transparent
duplication goes away.

## Pages

### Header

Two rows. Top: logo, wordmark with the "18 years" line as a proper sub-label, then
rating pill and "Book Consultation" pushed right. Bottom: nav (Venue · Vendors ·
Packages · Articles · Why Us) with a gold underline on the active item.

On scroll the two rows collapse into a single sticky bar. Below `md`, the nav row is
replaced by a hamburger opening a `bits-ui` drawer.

This fixes the current header, where the logo, tagline, nav, rating pill and CTA all
compete for one line and visibly overlap at common viewport widths.

### Homepage (`/`)

Full-bleed hero photo with a dark gradient scrim, headline, subhead and the `SearchBar`
overlaid. Below: top venues grid (4-up), packages strip, testimonials, featured
articles, footer.

The hero image is the LCP element — it must be `fetchpriority="high"`, correctly sized,
and served as WebP with a JPEG fallback. The scrim is required, not decorative: white
text on an uncontrolled photo fails contrast.

### Venue detail (`/wedding-venue/[city]/[slug]`)

1. Breadcrumb
2. `PhotoMosaic` — 1 large + 4 small, "See all (n)" on the last tile
3. Title block — venue name, location, star rating
4. Sticky section tabs (Photos · About · Packages · Location) with scroll-spy
5. Two columns:
   - **Left** — highlight chips, description (`Prose`), package cards from the API, location/map
   - **Right** — sticky enquiry card: name, WhatsApp number, wedding date, gold "Check Availability", WhatsApp button

### Venue search (`/wedding-venue/search`)

Structure is already right — filter rail plus card grid — so this is a restyle. Filters
become tokenised inputs and `bits-ui` selects; cards get the new treatment. URL-driven
filter state is preserved exactly as-is.

### Remaining routes

`/articles`, `/artikel/[category]/[slug]`, `/about`, `/contact`, `/our-vendors`,
`/privacy`, `/terms` are restyled to the token set. Article detail gains the `Prose`
scale. `StaticPage` is retokenised once and the four static routes inherit it.

### Footer

Four columns on the white base: brand and contact, venue links by city, company links,
legal. Replaces the current single-band layout.

## Content integrity

The venue detail page currently renders a significant amount of invented data. The
redesign renders **only what the API actually returns**.

Already removed (2026-08-01, ahead of this spec):

- `ratingLabel` — `stars >= 5 ? '4.9' : ...`, an invented review score
- `reviewCount` — `stars >= 5 ? 128 : 84`, an invented review count
- `aggregateRating` in the JSON-LD, which emitted both to Google as structured data

`starRating` remains in the JSON-LD: `venue.stars` is the real hotel star rating from
the database, not a review score.

Still to remove as part of this work:

| Symbol | Renders | Problem |
|---|---|---|
| `PACKAGES` | 3 package cards | Identical for every venue; the real `venue.packages` is never rendered |
| `COMPARE` | Package comparison table | Hardcoded feature matrix, identical everywhere |
| `VENDORS` / `VENDOR_CATS` | Vendor logo grid + filter | Hardcoded list |
| `venueStats` | "32+ vendor partners", "1 hr consult reply time" | Invented figures |
| `weddingCount` | "140+ weddings hosted with 7Magic" | `stars >= 5 ? 140 : 90` |
| `PLACEHOLDER_PHOTOS` | "Grand Ballroom", "Garden terrace"… | Filler gallery labels |
| `whatsappHref` | WhatsApp link | Number is the placeholder `6281234567890` |

**Assumption pending confirmation:** these are removed rather than stubbed, matching the
decision already taken on reviews. The packages section renders real `venue.packages`
(`{name, price, pax, note}`); the vendor grid and stats bands are dropped from the venue
page. If instead you want them kept as hidden-until-populated components, that changes
the component list above and should be settled before the plan is written.

Sections The Knot has that 7Magic has no field for — reviews, amenities, room/sq-ft
capacity, awards, availability, pricing breakdown — are **out of scope**. Adding them
would be an API plus CMS project, not a redesign.

## Risks

**Venue photos — verified available (2026-08-01).** A prior R2 migration had rewritten
image URLs without copying the files; that backfill has since been run. Re-checked
against the live database and R2: **1143 photos across 122 venues, 117 of them with 5 or
more, and 80 of 80 randomly sampled URLs return HTTP 200.** The photo-led layout is safe
to build.

One implementation note: `venue_photos.cdn_url` and `.thumbnail_url` are **NULL for all
1143 rows**. Real URLs live in the `webp_srcset`/`jpeg_srcset` columns and the
`webp_variants`/`jpeg_variants` JSON. `_photo_image_urls()` in
`apps/api/app/services/venues.py` already resolves this correctly, so `apps/web` should
keep consuming the API's `gallery[]` shape and must not read `cdn_url` directly.

`PhotoMosaic` still needs a degraded state for the 5 venues with fewer than 5 photos —
collapse to the available tiles rather than rendering empty ones.

**Contrast on the hero.** White text over an arbitrary venue photo is the most likely
accessibility failure in this design. The gradient scrim is a requirement.

**Scope size.** Every public route changes. The work should land as a token layer and
component library first, then page-by-page, so the site is never half-migrated between
two visual systems.

## Testing

- `pnpm --filter @7magic/web run check` clean after each page migration
- Visual pass at 375px, 768px, 1280px, 1920px for every migrated route
- Contrast audit on gold-on-white, pink-on-white, both `-dark`-on-`-soft` pairs, and
  hero text over the scrim
- Keyboard-only pass on the lightbox, mobile drawer, filter selects and enquiry form
- Lighthouse on `/` and one venue detail page — LCP must not regress against current
- Confirm no fabricated value survives: grep the venue detail route for the symbols
  listed above

## Out of scope

- Any `apps/api` or `apps/cms` change
- New venue data fields (reviews, amenities, capacity)
- Content rewriting
- The standalone `7Magic Venue Detail page/` prototype folder, which stays as reference
