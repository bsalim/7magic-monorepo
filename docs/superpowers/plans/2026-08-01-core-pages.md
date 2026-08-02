# Core Pages — Implementation Plan (Plan 2 of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the venue detail and venue search pages onto the approved layout — photo mosaic with lightbox, sticky section tabs, tokenised search — and remove the last synthetic claim.

**Architecture:** Builds on Plan 1's token layer and shadcn re-theme. New presentational pieces go in `src/lib/components/venue-detail/`; the lightbox uses the already-installed shadcn `Dialog`. No new dependencies.

**Tech Stack:** SvelteKit 2 + Svelte 5 runes, Tailwind v4 tokens, shadcn-svelte, paraglide i18n, Vitest.

**Spec:** `docs/superpowers/specs/2026-08-01-public-site-redesign-design.md`

---

## Content decisions (confirmed with the user, 2026-08-01)

An earlier pass characterised six things as "fabricated". On inspection that was too broad, and the plan reflects the corrected reading:

| Item | Verdict | Action |
|---|---|---|
| `weddingCount` | **Synthetic.** `stars >= 5 ? 140 : 90` — asserts a wedding count that varies by hotel star rating. | Remove |
| `PACKAGES` / `COMPARE` | **Real business content.** 7Magic's own service tiers; identical across venues because they genuinely are. | Keep |
| `VENDORS` | **Real.** 33 partners with real logo assets. | Keep |
| `venueStats` "32+ vendor partners" | **Accurate** — there are 33. But hardcoded, so it silently rots. | Derive from the list |
| `venueStats` "18 yrs", "1 hr", "Private" | Real company facts / service promises, not per-venue claims. | Keep |
| `PLACEHOLDER_PHOTOS` | Dead path — reachable only when a venue has zero photos; 121 of 122 have 5+. | Keep as fallback, stop inventing labels |

The packages and vendor lists remaining hardcoded in components is a **content-management** problem, not a truthfulness one. Moving them into the CMS is deliberate future work, out of scope here.

---

### Task 1: Remove the synthetic wedding count

**Files:**
- Modify: `apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte`
- Modify: `apps/web/src/lib/components/venue-detail/VenueHero.svelte`

- [ ] **Step 1: Drop the derived value**

In `+page.svelte`, delete:

```ts
  const weddingCount = $derived(venue.stars >= 5 ? 140 : 90);
```

and remove `{weddingCount}` from the `<VenueHero ... />` call.

- [ ] **Step 2: Drop the prop and its markup**

In `VenueHero.svelte`, remove `weddingCount` from both the destructured props and the props type, then delete these two lines from `.hero-meta`:

```svelte
        <span class="dot-sep"></span>
        <span class="muted">{weddingCount}+ weddings hosted with 7Magic</span>
```

- [ ] **Step 3: Verify**

Run: `cd apps/web && grep -rn "weddingCount" src/`
Expected: no output.

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

- [ ] **Step 4: Commit**

```bash
git add "apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte" apps/web/src/lib/components/venue-detail/VenueHero.svelte
git commit -m "fix(web): drop the synthetic weddings-hosted count"
```

---

### Task 2: Derive the vendor count from the real list

`VENDORS` lives inside `VenueVendors.svelte`, so `venueStats` cannot see it and hardcodes "32+". Extracting the list to a module makes the stat self-maintaining.

**Files:**
- Create: `apps/web/src/lib/components/venue-detail/vendors.ts`
- Modify: `apps/web/src/lib/components/venue-detail/VenueVendors.svelte`
- Modify: `apps/web/src/lib/components/venue-detail/VenueOverview.svelte`
- Test: `apps/web/src/lib/components/venue-detail/vendors.test.ts`

- [ ] **Step 1: Write the failing test**

`apps/web/src/lib/components/venue-detail/vendors.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { VENDORS, VENDOR_CATS, vendorCount } from './vendors';

describe('vendors', () => {
  it('exposes the full partner list', () => {
    expect(VENDORS.length).toBeGreaterThan(30);
  });

  it('reports a count that matches the list', () => {
    expect(vendorCount).toBe(VENDORS.length);
  });

  it('starts its category list with All', () => {
    expect(VENDOR_CATS[0]).toBe('All');
  });

  it('only uses categories declared in VENDOR_CATS', () => {
    const known = new Set(VENDOR_CATS);
    for (const vendor of VENDORS) {
      expect(known.has(vendor.cat)).toBe(true);
    }
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/web && pnpm exec vitest run src/lib/components/venue-detail/vendors.test.ts`
Expected: FAIL — `Failed to resolve import "./vendors"`.

- [ ] **Step 3: Extract the module**

Create `vendors.ts` exporting `Vendor`, `VENDOR_CATS`, `VENDORS` and `vendorCount`. Move the `type Vendor`, `VENDOR_CATS` and `VENDORS` declarations **verbatim** out of `VenueVendors.svelte` — do not retype the 33 entries, copy them, and keep every `logo` path byte-identical. Append:

```ts
/** Kept in sync automatically so the "vendor partners" stat cannot drift. */
export const vendorCount = VENDORS.length;
```

- [ ] **Step 4: Import them back in `VenueVendors.svelte`**

Replace the removed declarations with:

```ts
  import { VENDORS, VENDOR_CATS, type Vendor } from './vendors';
```

Leave the rest of the component untouched.

- [ ] **Step 5: Use the derived count in `VenueOverview.svelte`**

Add `import { vendorCount } from './vendors';` and change the last stat from the hardcoded `'32+'` to:

```ts
    { value: `${vendorCount}`, label: 'Vendor partners' }
```

- [ ] **Step 6: Verify**

Run: `cd apps/web && pnpm exec vitest run src/lib/components/venue-detail/vendors.test.ts && pnpm run check`
Expected: 4 tests pass; `0 errors, 0 warnings`.

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/lib/components/venue-detail/
git commit -m "refactor(web): extract the vendor list and derive its count"
```

---

### Task 3: PhotoMosaic with lightbox

Replaces the single hero image plus thumbnail strip with the approved 1-large + 4-small mosaic and a "See all (n)" overlay opening a lightbox.

**Files:**
- Create: `apps/web/src/lib/components/venue-detail/PhotoMosaic.svelte`
- Create: `apps/web/src/lib/components/venue-detail/PhotoLightbox.svelte`
- Test: `apps/web/src/lib/components/venue-detail/PhotoMosaic.test.ts`

- [ ] **Step 1: Write the failing test**

`apps/web/src/lib/components/venue-detail/PhotoMosaic.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import PhotoMosaic from './PhotoMosaic.svelte';
import type { DisplayPhoto } from './photos';

const photo = (n: number): DisplayPhoto => ({
  src: `/p${n}.jpg`,
  thumb: `/t${n}.jpg`,
  label: `Photo ${n}`,
  real: true
});

const make = (n: number) => Array.from({ length: n }, (_, i) => photo(i + 1));

describe('PhotoMosaic', () => {
  it('renders five tiles when five or more photos exist', () => {
    render(PhotoMosaic, { props: { photos: make(10), venueName: 'JW Marriott' } });
    expect(screen.getAllByRole('img')).toHaveLength(5);
  });

  it('collapses to the photos available when there are fewer than five', () => {
    render(PhotoMosaic, { props: { photos: make(2), venueName: 'JW Marriott' } });
    expect(screen.getAllByRole('img')).toHaveLength(2);
  });

  it('shows the remaining count on the last tile', () => {
    render(PhotoMosaic, { props: { photos: make(10), venueName: 'JW Marriott' } });
    expect(screen.getByText(/See all \(10\)/)).toBeInTheDocument();
  });

  it('omits the see-all control when everything is already visible', () => {
    render(PhotoMosaic, { props: { photos: make(4), venueName: 'JW Marriott' } });
    expect(screen.queryByText(/See all/)).toBeNull();
  });

  it('renders nothing when there are no real photos', () => {
    const { container } = render(PhotoMosaic, { props: { photos: [], venueName: 'JW Marriott' } });
    expect(container.querySelector('img')).toBeNull();
  });
});
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/web && pnpm exec vitest run src/lib/components/venue-detail/PhotoMosaic.test.ts`
Expected: FAIL — unresolved import.

- [ ] **Step 3: Implement `PhotoMosaic.svelte`**

Grid of `2fr 1fr 1fr` with the first tile spanning both rows; render `Math.min(5, photos.length)` tiles; when `photos.length > 5`, overlay the last tile with a "See all (n)" button that opens `PhotoLightbox`. Every tile is a `<button>` that opens the lightbox at that index. Images use `loading="lazy"` except the first, which takes `fetchpriority="high"` as the LCP element. Alt text is `` `${venueName} — ${photo.label}` ``. Tiles use `rounded-card` and `object-cover`.

Guard the empty case: if `photos.length === 0`, render nothing.

- [ ] **Step 4: Implement `PhotoLightbox.svelte`**

Wrap shadcn `Dialog` (`$lib/components/ui/dialog`), which supplies focus trapping and Escape-to-close. Props: `photos`, `venueName`, `open` (bindable), `index` (bindable). Provide previous/next controls with `aria-label`s, wrap the index at both ends, and bind arrow keys via `<svelte:window onkeydown>` guarded on `open`.

- [ ] **Step 5: Run the tests and watch them pass**

Run: `cd apps/web && pnpm exec vitest run src/lib/components/venue-detail/PhotoMosaic.test.ts`
Expected: `5 passed`.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/lib/components/venue-detail/
git commit -m "feat(web): add PhotoMosaic and PhotoLightbox"
```

---

### Task 4: Wire the mosaic into VenueHero

**Files:**
- Modify: `apps/web/src/lib/components/venue-detail/VenueHero.svelte`
- Modify: `apps/web/src/routes/wedding-venue/[city]/[slug]/venue-detail.css`

- [ ] **Step 1: Swap the gallery block**

Replace the `.gallery` div (the `.g-main` image plus the `.thumbs` strip) with `<PhotoMosaic {photos} venueName={venue.name} />`. Keep the `.hero-grid` two-column structure and the booking `<aside>` exactly as they are.

The `activePhoto` prop becomes unused once the thumbnail strip is gone — remove it from `VenueHero`'s props, from the `<VenueHero>` call in `+page.svelte`, and delete the now-unused `activePhoto` state and `currentPhoto` derived value from `+page.svelte`. `currentPhoto` is still referenced by the JSON-LD `image` field, so replace that with `photos[0]?.src ?? venue.cover_photo.small_url`.

- [ ] **Step 2: Remove the dead CSS**

Delete the `.g-main`, `.thumbs`, `.thumb`, `.g-count` and `.g-badges` rules from `venue-detail.css` — grep each selector first and only delete those with no remaining consumer.

- [ ] **Step 3: Verify**

Run: `cd apps/web && pnpm run check && pnpm test`
Expected: `0 errors, 0 warnings`; all suites pass.

- [ ] **Step 4: Visual check**

Run `pnpm dev` and open `/wedding-venue/jakarta/jw-marriott-hotel-jakarta`. Confirm: five tiles in a 1-large + 4-small mosaic, "See all (10)" on the last tile, clicking any tile opens the lightbox at that photo, arrow keys move between photos, Escape closes, and focus returns to the trigger.

- [ ] **Step 5: Commit**

```bash
git add "apps/web/src/routes/wedding-venue/[city]/[slug]/" apps/web/src/lib/components/venue-detail/
git commit -m "feat(web): lead the venue detail page with the photo mosaic"
```

---

### Task 5: Sticky section tabs

**Files:**
- Create: `apps/web/src/lib/components/venue-detail/VenueSectionNav.svelte`
- Modify: `apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte`
- Test: `apps/web/src/lib/components/venue-detail/VenueSectionNav.test.ts`

- [ ] **Step 1: Confirm the section ids that already exist**

Run: `cd apps/web && grep -rn 'id="' src/lib/components/venue-detail/*.svelte`

Use only ids that exist; add an `id` to a section rather than inventing a link target that goes nowhere.

- [ ] **Step 2: Write the failing test**

`apps/web/src/lib/components/venue-detail/VenueSectionNav.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import VenueSectionNav from './VenueSectionNav.svelte';

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'packages', label: 'Packages' },
  { id: 'vendors', label: 'Vendors' }
];

describe('VenueSectionNav', () => {
  it('links each section by anchor', () => {
    render(VenueSectionNav, { props: { sections } });
    expect(screen.getByRole('link', { name: 'Overview' })).toHaveAttribute('href', '#overview');
    expect(screen.getByRole('link', { name: 'Packages' })).toHaveAttribute('href', '#packages');
  });

  it('marks the active section', () => {
    render(VenueSectionNav, { props: { sections, activeId: 'packages' } });
    const active = screen.getAllByRole('link').filter((a) => a.getAttribute('aria-current') === 'true');
    expect(active).toHaveLength(1);
    expect(active[0]).toHaveAttribute('href', '#packages');
  });
});
```

- [ ] **Step 3: Run it and watch it fail**

Run: `cd apps/web && pnpm exec vitest run src/lib/components/venue-detail/VenueSectionNav.test.ts`
Expected: FAIL — unresolved import.

- [ ] **Step 4: Implement**

A `sticky` bar that sits below the site header (`top-[var(--header-h)]` or a fixed offset matching the collapsed header), horizontally scrollable on small screens, with a gold underline on the active item. Props: `sections: {id, label}[]` and an optional `activeId`. Scroll-spy lives in the page, not the component, so the component stays pure and testable — the page owns an `IntersectionObserver` over the section ids and passes `activeId` down.

- [ ] **Step 5: Wire it into the page**

Insert `<VenueSectionNav {sections} {activeId} />` between `<VenueHero>` and `<VenueOverview>`, and add the `IntersectionObserver` in the existing `onMount` alongside the sticky-bar observer. Disconnect both on teardown.

- [ ] **Step 6: Verify and commit**

Run: `cd apps/web && pnpm run check && pnpm test`
Expected: clean.

```bash
git add apps/web/src/lib/components/venue-detail/ "apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte"
git commit -m "feat(web): add sticky section tabs to the venue detail page"
```

---

### Task 6: Restyle the venue search page

Structure (filter rail + card grid) is already right; this is a token pass.

**Files:**
- Modify: `apps/web/src/routes/wedding-venue/search/+page.svelte`
- Modify: `apps/web/src/lib/components/VenueFilters.svelte`
- Modify: `apps/web/src/lib/components/VenueCard.svelte`

- [ ] **Step 1: Replace hardcoded colours in `VenueCard.svelte`**

Swap `border-[#eadfce]` for `border-border`, `text-amber-500` for `text-brand-gold`, `text-slate-500` for `text-muted-foreground`, and `rounded-md` for `rounded-card`. Give the title `font-display`. Keep the `onerror` fallback and the existing `VenueCard` prop shape untouched.

- [ ] **Step 2: Replace hardcoded colours in the search page and filters**

Same substitutions: `bg-[#fbf8f3]` → `bg-background`, `border-[#eadfce]` → `border-border`, `text-[#966d3f]` → `text-brand-gold-hover`, `bg-[#c99d65]` → use `buttonVariants({ variant: 'gold' })`.

- [ ] **Step 3: Verify no hardcoded hex remains on these three files**

Run: `cd apps/web && grep -nE '#[0-9a-fA-F]{6}' src/routes/wedding-venue/search/+page.svelte src/lib/components/VenueFilters.svelte src/lib/components/VenueCard.svelte`
Expected: no output.

- [ ] **Step 4: Verify and commit**

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

```bash
git add apps/web/src/routes/wedding-venue/search/ apps/web/src/lib/components/VenueFilters.svelte apps/web/src/lib/components/VenueCard.svelte
git commit -m "feat(web): restyle venue search onto the design tokens"
```

---

## Self-Review

**Spec coverage.** `PhotoMosaic` (Task 3, including the fewer-than-5 degraded state the spec called for), `Lightbox` (Task 3), sticky section tabs (Task 5), venue search restyle (Task 6). The spec's `SearchBar` belongs to the homepage hero and moves to Plan 3 with the rest of the homepage — the homepage is a larger job than the two pages here and splitting it keeps each plan independently shippable.

**Deferred to Plan 3:** homepage hero and `SearchBar`, articles, article detail, `Prose`, static routes, and the WCAG contrast audit across the gold/pink pairs.

**Not doing, deliberately:** moving `PACKAGES`/`COMPARE`/`VENDORS` into the CMS. Confirmed with the user as real content; relocating it is a separate API + CMS project.

**Type consistency.** `DisplayPhoto` comes from the existing `./photos` module and is unchanged. `Vendor` moves to `./vendors` and is re-imported by `VenueVendors.svelte` under the same name. `PhotoMosaic` and `PhotoLightbox` share the `photos` / `venueName` prop names.
