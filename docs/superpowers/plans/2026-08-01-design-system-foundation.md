# Design System Re-theme + Global Chrome — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-theme the existing shadcn-svelte install in `apps/web` to the approved palette, typography and radius, then rewrite the site header and footer against it.

**Architecture:** `apps/web` already has shadcn-svelte with 12 component families and a token layer in `app.css`. Rather than hand-building parallel primitives, this plan **retargets the existing shadcn CSS variables** (`--primary`, `--background`, `--radius`, …) at the 7Magic palette and adds gold/pink/whatsapp variants to `buttonVariants`. Every consumer of those tokens inherits the new look for free.

**Tech Stack:** SvelteKit 2 + Svelte 5 (runes), Tailwind CSS v4, shadcn-svelte 1.3, bits-ui, tailwind-variants, paraglide i18n, @fontsource/poppins + @fontsource-variable/jost, Vitest.

**Spec:** `docs/superpowers/specs/2026-08-01-public-site-redesign-design.md`

---

## Revision note (2026-08-01)

This plan replaces an earlier version that assumed `apps/web` had no component library. A concurrent session installed full shadcn-svelte, which invalidated that approach. **Changed:** no hand-built `Button`/`Badge`/`Card`/`Input` primitives (they exist), no new `cn()` (exists in `$lib/utils.ts`), and `app.css` is retargeted rather than replaced — replacing it would break all 12 shadcn families at once.

**Constraints discovered during survey that the plan must respect:**

- `PublicHeader.svelte` uses **paraglide i18n** (`m.nav_venues()` etc.) and renders `LanguageSwitcher`. Both must survive the rewrite. Hardcoding English strings is a regression.
- The venue detail route owns a **1341-line `venue-detail.css`** declaring `--ff-sans: 'Hanken Grotesk'` and `--ff-serif: 'Cormorant Garamond'`, loaded from Google Fonts in that route's `<svelte:head>`. That is a third font system and must be retargeted, not ignored.
- `--radius` is already `0.375rem` (6px), which matches the approved input radius. No change needed there.
- The site uses `@lucide/svelte` (not `lucide-svelte`) in newer components.

---

## File Structure

**Created:**

| File | Responsibility |
|---|---|
| `apps/web/vitest-setup.ts` | Registers jest-dom matchers |

**Modified:**

| File | Change |
|---|---|
| `apps/web/package.json` | Add fonts + vitest toolchain, `test` script |
| `apps/web/vite.config.ts` | Add vitest config block |
| `apps/web/src/app.css` | Retarget colour tokens, add font tokens, import fonts |
| `apps/web/src/lib/components/ui/button/button.svelte` | Add `gold`/`pink`/`whatsapp` variants, pill radius |
| `apps/web/src/routes/wedding-venue/[city]/[slug]/venue-detail.css` | Point `--ff-sans`/`--ff-serif` at the new fonts |
| `apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte` | Drop the Google Fonts `<link>` |
| `apps/web/src/lib/components/PublicHeader.svelte` | Two-row layout, sticky collapse; keep i18n + LanguageSwitcher + Sheet |
| `apps/web/src/lib/components/PublicFooter.svelte` | Four-column layout on white |

---

### Task 1: Install fonts and the test toolchain

**Files:**
- Modify: `apps/web/package.json`

- [ ] **Step 1: Add the fonts**

```bash
cd apps/web
pnpm add @fontsource/poppins@^5.3.0 @fontsource-variable/jost@^5.3.0
```

Poppins is **not** a variable font — `@fontsource-variable/poppins` does not exist on npm. It ships as static weights. Jost is variable.

- [ ] **Step 2: Add the test toolchain**

```bash
cd apps/web
pnpm add -D vitest@^3.2.4 @testing-library/svelte@^5.2.8 @testing-library/jest-dom@^6.6.3 @testing-library/user-event@^14.6.1 jsdom@^26.1.0
```

- [ ] **Step 3: Add test scripts**

In `apps/web/package.json`, add to `"scripts"`:

```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 4: Verify**

Run: `cd apps/web && pnpm list @fontsource/poppins @fontsource-variable/jost vitest`
Expected: all three resolve with versions, no `UNMET DEPENDENCY`.

- [ ] **Step 5: Commit**

```bash
git add apps/web/package.json pnpm-lock.yaml
git commit -m "chore(web): add Poppins, Jost and the vitest toolchain"
```

---

### Task 2: Wire up Vitest

**Files:**
- Modify: `apps/web/vite.config.ts`
- Create: `apps/web/vitest-setup.ts`

- [ ] **Step 1: Read the current Vite config**

Run: `cat apps/web/vite.config.ts`

It has plugins for tailwind, sveltekit and paraglide. **Preserve every existing plugin** — only add the `test` block and swap the `defineConfig` import.

- [ ] **Step 2: Create the setup file**

`apps/web/vitest-setup.ts`:

```ts
import '@testing-library/jest-dom/vitest';
```

- [ ] **Step 3: Add the vitest block**

Change the import at the top of `apps/web/vite.config.ts` from `vite` to `vitest/config`:

```ts
import { defineConfig } from 'vitest/config';
```

Then add this key to the config object, leaving `plugins` exactly as it was:

```ts
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest-setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts}'],
    // Svelte 5 components must resolve to their browser build under jsdom.
    resolve: {
      conditions: ['browser']
    }
  }
```

- [ ] **Step 4: Add a temporary smoke test and run it**

`apps/web/src/lib/smoke.test.ts`:

```ts
import { describe, expect, it } from 'vitest';

describe('vitest', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

Run: `cd apps/web && pnpm test`
Expected: `1 passed`.

- [ ] **Step 5: Delete the smoke test and commit**

```bash
rm apps/web/src/lib/smoke.test.ts
git add apps/web/vite.config.ts apps/web/vitest-setup.ts
git commit -m "chore(web): configure vitest with jsdom and testing-library"
```

---

### Task 3: Re-theme the token layer

Retarget the existing shadcn variables. Do **not** delete `@import 'shadcn-svelte/tailwind.css'`, the `@theme inline` block or the `@layer base` block — the component families depend on all three.

**Files:**
- Modify: `apps/web/src/app.css`

- [ ] **Step 1: Import the fonts**

At the top of `apps/web/src/app.css`, directly after the three existing `@import` lines, add:

```css
/* Poppins is a static font — import only the weights the type scale uses. */
@import '@fontsource/poppins/400.css';
@import '@fontsource/poppins/500.css';
@import '@fontsource/poppins/600.css';
@import '@fontsource/poppins/700.css';
@import '@fontsource-variable/jost';
```

- [ ] **Step 2: Retarget the colour variables**

In the `:root` block, replace the existing colour values with these. Keep `--radius: 0.375rem` — it is already the approved 6px input radius.

```css
  --background: #ffffff;
  --foreground: #141414;

  --card: #ffffff;
  --card-foreground: #141414;
  --popover: #ffffff;
  --popover-foreground: #141414;

  --primary: #b08542;
  --primary-foreground: #ffffff;

  --secondary: #fbf7f0;
  --secondary-foreground: #141414;

  --muted: #fbf7f0;
  --muted-foreground: #6b6b6b;

  --accent: #fdf1f6;
  --accent-foreground: #b8306a;

  --destructive: #b3261e;

  --border: #e8e8e8;
  --input: #e8e8e8;
  --ring: #b08542;
```

- [ ] **Step 3: Retarget and extend the brand extras**

Replace the `/* Brand extras ... */` group with:

```css
  /* Brand extras not covered by shadcn's token set. */
  --brand-gold: #b08542;
  --brand-gold-hover: #8a6524;
  --brand-gold-soft: #fbf6ec;
  --brand-pink: #e5568e;
  --brand-pink-deep: #b8306a;
  --brand-pink-soft: #fdf1f6;
  --brand-whatsapp: #128c7e;
  --brand-dark: #161a24;
  --brand-dark-accent: #d4b27f;
  --brand-success: #1f8f5f;
  --brand-success-hover: #18764e;
  --brand-ink: #141414;
  --brand-warm: #fbf7f0;
  --brand-warm-deep: #f2e4cc;
```

`--brand-gold-hover` deliberately changes from `#b8884d` to the darker `#8a6524`, and `--brand-pink` from `#d6607f` to `#e5568e`, to match the approved palette.

- [ ] **Step 4: Expose the new tokens to Tailwind**

In the `@theme inline` block, replace the `--color-brand-*` group with:

```css
  --color-brand-gold: var(--brand-gold);
  --color-brand-gold-hover: var(--brand-gold-hover);
  --color-brand-gold-soft: var(--brand-gold-soft);
  --color-brand-pink: var(--brand-pink);
  --color-brand-pink-deep: var(--brand-pink-deep);
  --color-brand-pink-soft: var(--brand-pink-soft);
  --color-brand-whatsapp: var(--brand-whatsapp);
  --color-brand-dark: var(--brand-dark);
  --color-brand-dark-accent: var(--brand-dark-accent);
  --color-brand-success: var(--brand-success);
  --color-brand-success-hover: var(--brand-success-hover);
  --color-brand-ink: var(--brand-ink);
  --color-brand-warm: var(--brand-warm);
  --color-brand-warm-deep: var(--brand-warm-deep);

  --font-display: 'Poppins', ui-sans-serif, system-ui, sans-serif;
  --font-body: 'Jost Variable', 'Jost', ui-sans-serif, system-ui, sans-serif;
```

- [ ] **Step 5: Apply the fonts in the base layer**

In `@layer base`, replace the `body` rule's `font-family` declaration with `font-family: var(--font-body);` and add a heading rule after it:

```css
  h1,
  h2,
  h3,
  h4 {
    font-family: var(--font-display);
    letter-spacing: -0.01em;
  }
```

- [ ] **Step 6: Verify nothing broke**

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

Run: `cd apps/web && pnpm dev`, open `http://localhost:5180`. Expected: white page background (not cream), body copy in Jost, headings in Poppins, buttons gold, **no request to `fonts.googleapis.com` on the homepage**.

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/app.css
git commit -m "feat(web): retarget shadcn tokens to the gold/pink palette and Poppins/Jost"
```

---

### Task 4: Add brand button variants

**Files:**
- Modify: `apps/web/src/lib/components/ui/button/button.svelte`
- Test: `apps/web/src/lib/components/ui/button/button.test.ts`

- [ ] **Step 1: Write the failing test**

`apps/web/src/lib/components/ui/button/button.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import { createRawSnippet } from 'svelte';
import Button from './button.svelte';

const label = (text: string) =>
  createRawSnippet(() => ({ render: () => `<span>${text}</span>` }));

describe('Button brand variants', () => {
  it('renders the gold variant as a button', () => {
    render(Button, { props: { variant: 'gold', children: label('Book') } });
    const el = screen.getByRole('button', { name: 'Book' });
    expect(el.className).toContain('bg-brand-gold');
  });

  it('renders the whatsapp variant', () => {
    render(Button, { props: { variant: 'whatsapp', children: label('Chat') } });
    expect(screen.getByRole('button', { name: 'Chat' }).className).toContain('brand-whatsapp');
  });

  it('renders as an anchor when href is given', () => {
    render(Button, { props: { variant: 'gold', href: '/contact', children: label('Contact') } });
    expect(screen.getByRole('link', { name: 'Contact' })).toHaveAttribute('href', '/contact');
  });
});
```

This asserts on class names, which normally restates the implementation — here it is the only observable difference between variants, and the point is to catch a variant silently disappearing from `tv()`.

- [ ] **Step 2: Run it and watch it fail**

Run: `cd apps/web && pnpm vitest run src/lib/components/ui/button/button.test.ts`
Expected: FAIL — `gold` is not a known variant, so no `bg-brand-gold` class.

- [ ] **Step 3: Add the variants**

In the `buttonVariants` `tv({...})` call in `apps/web/src/lib/components/ui/button/button.svelte`, add these three entries to the `variant` map, after `link`:

```ts
				gold: "bg-brand-gold text-white hover:bg-brand-gold-hover",
				pink: "border-brand-pink bg-background text-brand-pink hover:bg-brand-pink-soft",
				whatsapp: "border-brand-whatsapp bg-background text-brand-whatsapp hover:bg-brand-gold-soft/40",
```

- [ ] **Step 4: Make the buttons pill-shaped**

The approved radius scale keeps buttons pill while inputs stay at 6px. In the same `tv()` call:

- In `base`, change `rounded-md` to `rounded-full`.
- In the `size` map, change every `rounded-[min(var(--radius-md),8px)]` and `rounded-[min(var(--radius-md),10px)]` to `rounded-full`. Leave the `in-data-[slot=button-group]:rounded-md` fragments alone — those apply only inside a button group, where square edges are correct.

- [ ] **Step 5: Run the test and watch it pass**

Run: `cd apps/web && pnpm vitest run src/lib/components/ui/button/button.test.ts`
Expected: `3 passed`.

- [ ] **Step 6: Check the whole app still compiles**

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/lib/components/ui/button/
git commit -m "feat(web): add gold, pink and whatsapp button variants with pill radius"
```

---

### Task 5: Unify the venue detail fonts

The venue detail route loads Hanken Grotesk and Cormorant Garamond from Google Fonts — a third font system, and a render-blocking third-party request on the highest-value SEO page.

**Files:**
- Modify: `apps/web/src/routes/wedding-venue/[city]/[slug]/venue-detail.css`
- Modify: `apps/web/src/routes/wedding-venue/[city]/[slug]/+page.svelte`

- [ ] **Step 1: Retarget the font variables**

In `venue-detail.css` lines 22–23, replace both declarations:

```css
  --ff-sans: var(--font-body);
  --ff-serif: var(--font-display);
```

Every `font-family: var(--ff-serif)` rule in the file (lines 459, 524, 544, 605, 667, 859, 901, 1141, 1223) then resolves to Poppins, and `--ff-sans` to Jost. No other edit to this file is needed.

- [ ] **Step 2: Remove the Google Fonts request**

In `+page.svelte`, delete these four lines from `<svelte:head>` (currently lines 108–113):

```svelte
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link
    href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&family=Cormorant+Garamond:wght@500;600;700&display=swap"
    rel="stylesheet"
  />
```

- [ ] **Step 3: Verify**

Run: `cd apps/web && grep -rn "fonts.googleapis" src/`
Expected: no output.

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

- [ ] **Step 4: Visual check**

Run `pnpm dev`, open a venue detail page. Expected: headings render in Poppins and body in Jost — the serif display face is gone. Confirm in DevTools Network that no `fonts.googleapis.com` request fires.

- [ ] **Step 5: Commit**

```bash
git add "apps/web/src/routes/wedding-venue/[city]/[slug]/"
git commit -m "feat(web): unify venue detail typography on Poppins/Jost, drop Google Fonts"
```

---

### Task 6: Rewrite PublicHeader as two rows

**Files:**
- Modify: `apps/web/src/lib/components/PublicHeader.svelte`
- Test: `apps/web/src/lib/components/PublicHeader.test.ts`

**Must preserve:** paraglide messages (`m.nav_venues()` etc.), `LanguageSwitcher`, and the shadcn `Sheet` mobile drawer. Do not hardcode English strings.

- [ ] **Step 1: Confirm the available message keys**

Run: `cd apps/web && grep -rn "nav_" src/lib/paraglide/messages.js | head -20`

Use only keys that exist. If a two-row header needs a label with no message key (for example a tagline), add it to the source message files rather than hardcoding it.

- [ ] **Step 2: Write the failing test**

`apps/web/src/lib/components/PublicHeader.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';
import PublicHeader from './PublicHeader.svelte';

describe('PublicHeader', () => {
  it('links the venue nav item to the search route', () => {
    render(PublicHeader);
    const venues = screen
      .getAllByRole('link')
      .find((a) => a.getAttribute('href') === '/wedding-venue/search');
    expect(venues).toBeDefined();
  });

  it('marks the active nav item with aria-current', () => {
    render(PublicHeader, { props: { pathname: '/articles' } });
    const active = screen
      .getAllByRole('link')
      .filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(1);
    expect(active[0].getAttribute('href')).toBe('/articles');
  });

  it('renders no aria-current when the path matches nothing', () => {
    render(PublicHeader, { props: { pathname: '/nowhere' } });
    const active = screen
      .getAllByRole('link')
      .filter((a) => a.getAttribute('aria-current') === 'page');
    expect(active).toHaveLength(0);
  });
});
```

- [ ] **Step 3: Run it and watch it fail**

Run: `cd apps/web && pnpm vitest run src/lib/components/PublicHeader.test.ts`
Expected: FAIL — there is no `pathname` prop and nothing sets `aria-current`.

- [ ] **Step 4: Rewrite the component**

Keep the existing `<script>` imports (`MenuIcon`, `Button`, `buttonVariants`, `Sheet`, `LanguageSwitcher`, `m`, `cn`) and the `links` array exactly as they are. Replace the `variant` prop with `pathname`, add the scroll state, and restructure the markup into two rows:

```svelte
<script lang="ts">
  import MenuIcon from '@lucide/svelte/icons/menu';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import * as Sheet from '$lib/components/ui/sheet';
  import LanguageSwitcher from './LanguageSwitcher.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { page } from '$app/state';
  import { cn } from '$lib/utils';

  // pathname is injectable so the component renders in tests without a router.
  let { pathname = undefined }: { pathname?: string } = $props();

  let current = $derived(pathname ?? page.url?.pathname ?? '/');
  let scrolled = $state(false);

  const links = $derived([
    { href: '/wedding-venue/search', label: m.nav_venues() },
    { href: '/articles', label: m.nav_articles() },
    { href: '/our-vendors', label: m.nav_vendors() },
    { href: '/about', label: m.nav_about() }
  ]);

  function isActive(href: string) {
    return current === href || current.startsWith(`${href}/`);
  }
</script>

<svelte:window onscroll={() => (scrolled = window.scrollY > 40)} />

<header class="sticky top-0 z-30 border-b border-border bg-background/95 backdrop-blur">
  <!-- Brand row — hidden once scrolled so the header collapses to one bar. -->
  <div class={cn('mx-auto max-w-7xl px-5 lg:px-8', scrolled ? 'hidden' : 'flex items-center gap-3 py-3')}>
    <a href="/" class="flex items-center gap-3">
      <img src="/img/7magic-logo.png" alt="" class="h-10 w-10 rounded-md object-contain" />
      <span class="leading-tight">
        <span class="block font-display text-base font-bold tracking-wide text-foreground">
          7MAGIC WEDDING
        </span>
        <span class="block text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
          {m.brand_tagline?.() ?? '18 years of wedding excellence'}
        </span>
      </span>
    </a>

    <div class="ml-auto hidden items-center gap-3 md:flex">
      <LanguageSwitcher />
      <a href="/contact" class={cn(buttonVariants({ variant: 'gold', size: 'sm' }), 'font-semibold')}>
        {m.nav_contact()}
      </a>
    </div>

    <div class="ml-auto md:hidden">
      <Sheet.Root>
        <Sheet.Trigger>
          {#snippet child({ props })}
            <Button {...props} variant="ghost" size="icon" aria-label={m.nav_open_menu()}>
              <MenuIcon />
            </Button>
          {/snippet}
        </Sheet.Trigger>
        <Sheet.Content side="right" class="w-72">
          <Sheet.Header>
            <Sheet.Title>7Magic Wedding</Sheet.Title>
          </Sheet.Header>
          <nav class="grid gap-1 px-4">
            {#each links as link (link.href)}
              <a href={link.href} class="rounded-md px-3 py-2 text-sm font-medium hover:bg-muted">
                {link.label}
              </a>
            {/each}
            <div class="mt-1"><LanguageSwitcher /></div>
            <a
              href="/contact"
              class={cn(buttonVariants({ variant: 'gold', size: 'sm' }), 'mt-2 font-semibold')}
            >
              {m.nav_contact()}
            </a>
          </nav>
        </Sheet.Content>
      </Sheet.Root>
    </div>
  </div>

  <!-- Nav row -->
  <div class="mx-auto hidden max-w-7xl items-center gap-7 px-5 md:flex lg:px-8">
    {#if scrolled}
      <a href="/" class="mr-2 flex items-center gap-2 py-3">
        <img src="/img/7magic-logo.png" alt="" class="h-7 w-7 rounded-md object-contain" />
        <span class="font-display text-sm font-bold text-foreground">7MAGIC</span>
      </a>
    {/if}

    {#each links as link (link.href)}
      <a
        href={link.href}
        aria-current={isActive(link.href) ? 'page' : undefined}
        class={cn(
          'border-b-2 py-3 text-[15px] transition',
          isActive(link.href)
            ? 'border-brand-gold font-semibold text-foreground'
            : 'border-transparent text-muted-foreground hover:text-foreground'
        )}
      >
        {link.label}
      </a>
    {/each}

    {#if scrolled}
      <div class="ml-auto flex items-center gap-3 py-2">
        <LanguageSwitcher />
        <a href="/contact" class={cn(buttonVariants({ variant: 'gold', size: 'sm' }), 'font-semibold')}>
          {m.nav_contact()}
        </a>
      </div>
    {/if}
  </div>
</header>
```

If `m.brand_tagline` does not exist, add it to the paraglide message sources for both locales rather than leaving the `??` fallback in place.

- [ ] **Step 5: Run the test and watch it pass**

Run: `cd apps/web && pnpm vitest run src/lib/components/PublicHeader.test.ts`
Expected: `3 passed`.

- [ ] **Step 6: Clear the `overlay` callers**

Run: `cd apps/web && grep -rn 'variant="overlay"' src/`

For every hit, remove the prop — the new header is opaque and sits above the hero. `LanguageSwitcher` also takes a `variant` prop; if it is only ever `overlay` from the header, leave its own default intact and simply stop passing it.

- [ ] **Step 7: Verify and commit**

Run: `cd apps/web && pnpm run check && pnpm test`
Expected: `0 errors, 0 warnings`; all suites pass.

```bash
git add apps/web/src/lib/components/PublicHeader.svelte apps/web/src/lib/components/PublicHeader.test.ts apps/web/src/routes/
git commit -m "feat(web): rewrite PublicHeader as a two-row collapsing header"
```

---

### Task 7: Rewrite PublicFooter

**Files:**
- Modify: `apps/web/src/lib/components/PublicFooter.svelte`

- [ ] **Step 1: Read the current footer and note its message keys**

Run: `cat apps/web/src/lib/components/PublicFooter.svelte`

If it uses paraglide messages, keep them. Reuse existing keys; add new ones to the message sources rather than hardcoding strings.

- [ ] **Step 2: Rewrite as four columns on the white base**

Structure: brand + blurb, venue links by city, company links, legal links, with a bottom bar carrying the copyright. Use `text-muted-foreground` for links, `text-foreground` for column headings with `font-display`, and `border-border` for the dividers — all already-themed tokens, so no new colour values appear in this file.

- [ ] **Step 3: Verify**

Run: `cd apps/web && pnpm run check`
Expected: `0 errors, 0 warnings`.

- [ ] **Step 4: Visual check at three widths**

Run `pnpm dev` and confirm at 375px, 768px and 1280px:
- Header shows two rows and nothing overlaps at any width
- Scrolling past 40px collapses it to one row with the compact logo
- Below `md` the hamburger opens the Sheet; Escape closes it
- The language switcher is reachable in both the desktop header and the drawer
- Footer is four columns on desktop, stacked on mobile
- Body copy in Jost, headings and buttons in Poppins

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/PublicFooter.svelte
git commit -m "feat(web): rewrite PublicFooter as a four-column layout"
```

---

## Self-Review

**Spec coverage.** The spec's colour, radius and typography tables are all realised in Task 3, mapped onto shadcn's variable names instead of bespoke ones. The spec's `Button` variants land in Task 4. Header and footer are Tasks 6–7.

**Divergence from the spec, deliberate:** the spec named hand-built primitives in `src/lib/components/ui/` and `bits-ui` for interactive parts only. shadcn-svelte is already installed and supplies both. The visual outcome is unchanged; only the implementation route differs. The spec's component table should be read as a list of required *capabilities*, not files to create.

**Deferred to the page plans:** `PhotoMosaic` (with its fewer-than-5-photos degraded state), `Lightbox`, `SearchBar`, `Prose`, and removal of the fabricated `PACKAGES` / `COMPARE` / `VENDORS` / `venueStats` / `weddingCount` / placeholder WhatsApp number now living in `src/lib/components/venue-detail/`.

**Contrast check** still outstanding: `--accent-foreground` `#b8306a` on `--accent` `#fdf1f6`, and `--brand-gold-hover` `#8a6524` on `--brand-gold-soft` `#fbf6ec`, must be measured against WCAG AA before the page plans close.

**Type consistency.** `pathname` is the prop name in both the `PublicHeader` test and implementation. `cn` is imported from `$lib/utils` throughout, matching the existing convention. Variant names `gold`/`pink`/`whatsapp` are used identically in Task 4's `tv()` map and Task 6's `buttonVariants({ variant: 'gold' })` calls.
