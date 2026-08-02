# Component Standardization (shadcn + bits-ui) & Dual-Language Support — Design

**Date:** 2026-07-30
**Branch:** `feature/shadcn-i18n` (worktree, based on `feature/session-auth` @ `eed9ee4`)
**Status:** Approved by user

## Goal

1. **Phase 1:** Standardize UI components across both SvelteKit apps on shadcn-svelte + bits-ui. The CMS is already on it; the public web app is converted while keeping its existing brand look.
2. **Phase 2:** Make the platform dual-language — Indonesian (default) and English — covering venue content, articles, and static page copy, with editing managed from the CMS.

Explicitly out of scope: translating the CMS admin chrome (stays English), redesigning the public site's visuals, adding locales beyond `id`/`en`.

## Current State

- `apps/cms`: shadcn-svelte 1.3 + bits-ui 2.18, Tailwind v4, "vega" style, 19 ui primitives under `$lib/components/ui`. All routes already compose them. Stragglers outside the system: `Stars.svelte`, `PageHeader.svelte`, `venues/VenuePhotoDropzone.svelte`, `venues/cover-cell.svelte`, `venues/sortable-header.svelte`. Both `lucide-svelte` (stale) and `@lucide/svelte` are installed.
- `apps/web`: plain Tailwind v4, hand-rolled `:root` CSS (cream `#fbf8f3` background, ink `#172033` text), 10 custom components, ~2,850 lines of Svelte total, with one 1,955-line venue detail page. No component library.
- API: FastAPI + SQLAlchemy. `venues` has single-language `description`, `ballrooms`, `packages` (JSON). `articles` has single-language `title/slug/summary/content_html` with no locale concept. Content today is Indonesian (public article route is `/artikel/...`).

## Phase 1 — Component Standardization

### Architecture decision

**Per-app shadcn installs** (user-approved). shadcn's copy-in model means each app owns its `components.json`, theme, and generated primitives. No shared `packages/ui` workspace package — the apps intentionally have different themes, and a shared package fights shadcn's update workflow.

### apps/web setup

- Dependencies: `bits-ui`, `shadcn-svelte`, `clsx`, `tailwind-merge`, `tailwind-variants`, `tw-animate-css`, `@lucide/svelte` (aligning versions with the CMS).
- `components.json` mirroring the CMS aliases (`ui` → `$lib/components/ui`, `utils` → `$lib/utils`, etc.), style "vega", icon library lucide.
- `src/lib/utils.ts` gains the standard `cn()` helper (the existing `src/lib/utils` content is preserved/merged).
- `app.css` rebuilt on shadcn theme tokens with the **brand palette mapped onto them**: `--background` from `#fbf8f3`, `--foreground` from `#172033`, `--primary`/`--accent` extracted from the accent colors currently used across the pages, radii/typography matching current look. Light mode only (public site has no dark mode today; `.dark` block included but unused).
- Visual outcome: pages look the same. Only the underlying components change.

### apps/web conversion

Generate only the primitives the site uses: `button`, `card`, `input`, `select`, `badge`, `separator`, `sheet` (mobile nav), `dialog` (gallery lightbox), `table` (packages), `skeleton`. Then convert:

| Existing component | Converts to |
|---|---|
| `PublicHeader` | nav built from Button variants + Sheet for mobile menu |
| `PublicFooter` | layout + Separator |
| `HeroVenueSearch` | Input + Select + Button |
| `VenueCard`, `ArticleCard` | Card composition + Badge |
| `PackageTable` | Table |
| `VenueFilters` | Select + Button + Badge |
| `VenueGallery` | Dialog-based lightbox |
| `WhatsappCTA` | Button variant |
| `StaticPage` | typography wrapper (kept custom, uses tokens) |

Routes are updated to compose these. The venue detail page (`wedding-venue/[city]/[slug]/+page.svelte`, 1,955 lines) is **split into focused section components** under `$lib/components/venue-detail/` (hero/gallery, info, ballrooms, packages, CTA, related) as part of the conversion — the one structural cleanup in this phase.

### apps/cms cleanup (light)

- `Stars`, `PageHeader`, `sortable-header`, `cover-cell`, `VenuePhotoDropzone`: keep as app components but align internals with ui primitives/tokens where sensible (e.g. `sortable-header` uses Button ghost variant). No visual changes.
- Remove the stale `lucide-svelte` dependency; standardize on `@lucide/svelte`.

### Phase 1 error handling / testing

- `svelte-check` must stay at 0 errors in both apps.
- API tests untouched and green.
- Manual visual smoke of each converted page via dev server against the live DB.

## Phase 2 — Dual Language (id default, en secondary)

### Storage decision

**Translation tables** (user-approved). Base tables keep the canonical Indonesian content; English lives in translation rows. Missing translation ⇒ fall back to Indonesian.

### Database schema

- `venue_translations`: `id`, `venue_id` (FK, cascade delete), `locale` (`'en'` only in practice, but modeled as a string for future locales), `description` (Text), `packages` (JSON). Unique on `(venue_id, locale)`. Alembic migration.
- `articles`: add `locale` (String(5), default `'id'`, indexed) and `translation_group_id` (UUID, default per-article) — the id/en versions of an article are separate rows sharing a `translation_group_id`, unique on `(translation_group_id, locale)`. Existing rows backfill `locale='id'` and their own group id.
- `article_categories`: `category` name gets an optional `category_en` column (single label, not worth a table).

### API

- Public venue/article endpoints accept `?locale=id|en` (default `id`). The service layer resolves translations with fallback and returns one merged shape — response contracts keep their current field names, so existing consumers are unaffected.
- CMS endpoints: `PUT /venues/{id}/translations/{locale}` upsert; article create accepts `locale` + optional `translation_group_id` to link an English version; article list exposes locale + sibling-translation info.

### CMS editing UX

- Venue form: translatable fields (`description`, packages) get an **ID / EN tab switcher** (bits-ui Tabs); EN tab edits the translation row, empty state shows "falls back to Indonesian".
- Articles: list shows a locale badge and translation-link state; an article without an English sibling gets an "Add English version" action that opens the editor pre-linked via `translation_group_id`.

### Web (Paraglide JS)

- `@inlang/paraglide-js` with the SvelteKit adapter; messages in `messages/id.json` and `messages/en.json`.
- URL strategy: Indonesian at root (unchanged URLs), English under `/en/...` prefix, via Paraglide's URL-based strategy + reroute hook.
- All static copy extracted to messages: header nav, footer, hero text, about/contact/privacy/terms pages, buttons/labels.
- Language switcher in `PublicHeader`; `<link rel="alternate" hreflang>` pairs emitted in the root layout head; `lang` attribute set per request.
- Data loads pass the active locale to the API.

### Phase 2 testing

- pytest: translation fallback (en missing ⇒ id content), upsert endpoint auth + validation, article translation linking, contract tests updated for `locale` param.
- `svelte-check` clean; manual smoke: `/` vs `/en/`, venue detail in both locales, CMS tab editing round-trip.

## Sequencing

Phase 1 fully lands (checks green, committed) before Phase 2 begins, per user instruction ("once you're done"). Each phase gets its own implementation plan section with independent verification.

## Risks

- The main checkout has uncommitted `feature/session-auth` edits touching some web components; merging this branch later may need light reconciliation.
- Venue `packages` JSON is structural; translating it as a whole JSON blob in `venue_translations` keeps the shape identical but duplicates non-linguistic values (prices). Accepted trade-off for simplicity: the EN packages JSON is a full copy edited in the CMS; no per-field merging of prices from the base row is attempted.
