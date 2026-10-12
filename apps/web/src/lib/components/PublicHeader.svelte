<script lang="ts">
  import type { Component, Snippet } from 'svelte';
  import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
  import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
  import LandmarkIcon from '@lucide/svelte/icons/landmark';
  import MenuIcon from '@lucide/svelte/icons/menu';
  import ShipIcon from '@lucide/svelte/icons/ship';
  import { Button } from '$lib/components/ui/button';
  import * as Sheet from '$lib/components/ui/sheet';
  import LanguageSwitcher from './LanguageSwitcher.svelte';
  import ConsultationModal from './ConsultationModal.svelte';
  import SgFlag from './SgFlag.svelte';
  import BaliTempleIcon from './BaliTempleIcon.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { deLocalizeHref, localizeHref } from '$lib/paraglide/runtime';
  import { page } from '$app/state';
  import {
    ALL_VENUES_HREF,
    VENDORS_HREF,
    eventLinks,
    inspirationLinks,
    packageLinks,
    venueRegions,
    type NavLink,
    type VenueRegion
  } from '$lib/site-nav';
  import { cn } from '$lib/utils';

  // pathname is injectable so the header renders in tests without a router.
  let { pathname = undefined }: { pathname?: string } = $props();

  // De-localized before comparing: the nav hrefs below are plain canonical paths
  // while the pathname carries the /en prefix, so on an English page nothing ever
  // matched and no nav item was ever highlighted.
  let current = $derived(deLocalizeHref(pathname ?? page.url?.pathname ?? '/'));
  let scrolled = $state(false);
  let consultOpen = $state(false);

  // One key at a time, so opening a menu closes its sibling.
  let openMenu = $state<string | null>(null);
  // The panels also open by CSS alone (hover, keyboard focus), so the menu works
  // on a page whose JavaScript never started. That needs an off switch: after a
  // link is followed the pointer is still over the panel, and CSS would hold it
  // open across the navigation. Cleared when the pointer leaves.
  let cssOpenSuppressed = $state(false);

  // The header is h-18 (72px) tall above the nav row and pins with exactly that
  // much of itself above the viewport, so 72 is the point where the brand row
  // has just scrolled out and the compact logo/CTA should take over. The lower
  // release point is plain hysteresis, so resting right on the boundary does
  // not flip the swap back and forth.
  function onScroll() {
    scrolled = window.scrollY > (scrolled ? 56 : 72);
  }

  // Beside Kontak rather than in the nav row: the brand row stays pinned on
  // desktop, so the tour CTA is reachable at any scroll position instead of
  // scrolling away with the nav row. Outline, not gold -- two gold buttons side
  // by side split the eye, and Kontak is still the primary action.
  const TOUR_HREF = '/tour';

  // The row reads Wedding Venue, Paket & Layanan, Vendor, Inspirasi, Events.
  // Venue and Vendor are the marketplace's two catalogues, so Vendor stays a
  // plain link; everything else is a group, so a new landing page is one more
  // item in a menu rather than another top-level link.
  const regions = $derived(venueRegions());
  const allVenues = $derived({ href: ALL_VENUES_HREF, label: m.nav_all_venues() });
  const menus = $derived({
    packages: { key: 'packages', label: m.nav_packages(), items: packageLinks() },
    inspiration: { key: 'inspiration', label: m.nav_inspiration(), items: inspirationLinks() },
    events: { key: 'events', label: m.nav_events(), items: eventLinks() }
  });

  // Keyed by region so the icons stay a header concern; the footer lists the
  // same regions as plain text.
  const regionIcons: Record<VenueRegion['key'], { icon: Component<{ class?: string }>; class: string }> = {
    jabodetabek: { icon: LandmarkIcon, class: 'size-4 shrink-0 text-brand-gold' },
    bali: { icon: BaliTempleIcon, class: 'size-4 shrink-0 text-brand-gold' },
    batam: { icon: ShipIcon, class: 'size-4 shrink-0 text-brand-gold' },
    singapore: { icon: SgFlag, class: 'h-3 w-[18px] shrink-0 rounded-[2px]' }
  };

  function isActive(href: string) {
    return current === href || current.startsWith(`${href}/`);
  }

  // Any venue page lights the menu, not only the cities it lists: a city the
  // catalogue adds later still belongs under Wedding Venue.
  let venuesActive = $derived(
    current.startsWith('/wedding-venue/') ||
      regions.some((region) => region.packages.some((link) => isActive(link.href)))
  );

  function closeMenus() {
    openMenu = null;
    cssOpenSuppressed = true;
  }

  function panelVisibility(key: string) {
    if (openMenu === key) return 'block';
    return cssOpenSuppressed ? 'hidden' : 'hidden group-focus-within:block group-hover:block';
  }
</script>

<svelte:window
  onscroll={onScroll}
  onpointerdown={(event) => {
    // Click-outside close, scoped to the open menu's own group so its trigger
    // and panel keep working; pressing a sibling trigger closes this one first.
    const target = event.target as Element | null;
    if (openMenu && !target?.closest?.(`[data-menu="${openMenu}"]`)) {
      openMenu = null;
    }
  }}
  onkeydown={(event) => {
    if (event.key === 'Escape') closeMenus();
  }}
/>

<!--
  The header collapses to a single bar by pinning itself one brand row (-top-18)
  above the viewport, never by removing the brand row. It is sticky and so still
  occupies its full height in normal flow: shrinking it would reflow the whole
  page below it, and the scroll compensation for that reflow drags scrollY back
  across the threshold — collapse, reflow, expand, reflow, forever. Keeping the
  height constant means the scrolled state cannot feed back into the scroll
  position at all. Mobile keeps top-0, where there is no nav row to collapse to.
-->
<!-- One snippet for the pair, because it renders twice: once in the brand row and
     again in the nav row once scrolled. Two copies drift. -->
{#snippet actions(withLanguage = true)}
  <!-- The scrolled nav row leaves the switcher out: it is the one item there
       that is not a destination, and the row has no room for it. It stays in
       the brand row and the mobile sheet. -->
  {#if withLanguage}<LanguageSwitcher />{/if}
  <!-- The tour is the funnel, so it carries the one solid CTA and Kontak sits
       beside it as an outline. Two solid buttons here read as two primaries,
       which is the same as none. -->
  <Button
    href={localizeHref(TOUR_HREF)}
    variant="gold"
    size="sm"
    class="font-semibold"
    aria-current={isActive(TOUR_HREF) ? 'page' : undefined}
  >
    {m.nav_free_venue_tour()}
  </Button>
  <Button variant="outline" size="sm" class="font-semibold" onclick={() => (consultOpen = true)}>
    {m.nav_contact()}
  </Button>
{/snippet}

{#snippet regionHeading(region: VenueRegion, extraClass = '')}
  {@const Icon = regionIcons[region.key].icon}
  <p
    class={cn(
      'flex items-center gap-2 px-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground',
      extraClass
    )}
  >
    <Icon class={regionIcons[region.key].class} />
    {region.label}
  </p>
{/snippet}

<!-- A trigger and its panel. The venue menu passes `wide` and its own panel
     body; the others list their items with a one-line description each. -->
{#snippet menuGroup(
  key: string,
  label: string,
  active: boolean,
  items: NavLink[],
  wide = false,
  body: Snippet | undefined = undefined
)}
  <!-- Opens on hover for pointer users and on click for touch, since this row
       is visible from md up and that includes tablets. The wide panel is
       positioned against the whole row rather than its trigger, so it cannot
       run off the right edge once the compact logo pushes the trigger along. -->
  <div
    class={cn('group flex', !wide && 'relative')}
    role="presentation"
    data-menu={key}
    onmouseenter={() => (openMenu = key)}
    onmouseleave={() => {
      openMenu = null;
      cssOpenSuppressed = false;
    }}
  >
    <button
      type="button"
      aria-expanded={openMenu === key}
      aria-haspopup="true"
      onclick={() => (openMenu = key)}
      class={cn(
        'flex items-center gap-1.5 whitespace-nowrap border-b-2 transition',
        scrolled ? 'text-[14px]' : 'text-[15px]',
        active
          ? 'border-brand-gold font-semibold text-foreground'
          : 'border-transparent text-muted-foreground hover:text-foreground'
      )}
    >
      {label}
      <ChevronDownIcon size={15} class={cn('transition', openMenu === key && 'rotate-180')} />
    </button>

    <!-- Always rendered, shown by state or by CSS: the links are in the server
         HTML for crawlers, and hover still opens the menu when hydration
         failed. -->
    <div
      class={cn(
        'absolute top-full z-40 rounded-md border border-border bg-background shadow-lg',
        wide
          ? 'left-5 w-[min(54rem,calc(100%-2.5rem))] p-4 lg:left-8 lg:w-[min(54rem,calc(100%-4rem))]'
          : 'left-0 w-[19rem] p-2',
        panelVisibility(key)
      )}
    >
      {#if body}
        {@render body()}
      {:else}
        {#each items as item (item.href)}
          <a
            href={localizeHref(item.href)}
            onclick={closeMenus}
            aria-current={isActive(item.href) ? 'page' : undefined}
            class={cn(
              'block rounded-md px-3 py-2.5 transition hover:bg-muted',
              isActive(item.href) && 'bg-muted'
            )}
          >
            <span class="block text-sm font-medium text-foreground">{item.label}</span>
            {#if item.desc}
              <span class="mt-0.5 block text-xs leading-5 text-muted-foreground">{item.desc}</span>
            {/if}
          </a>
        {/each}
      {/if}
    </div>
  </div>
{/snippet}

{#snippet venuePanel()}
  <div class="grid gap-x-4 gap-y-5 md:grid-cols-2 lg:grid-cols-4">
    {#each regions as region (region.key)}
      <div>
        {@render regionHeading(region)}
        <ul class="mt-2 grid gap-0.5">
          <!-- The region's landing page leads, set in the darker ink: it is the
               page that sells something, and the city hubs below it are lists. -->
          {#each [...region.packages, ...region.venues] as link (link.href)}
            <li>
              <a
                href={localizeHref(link.href)}
                onclick={closeMenus}
                aria-current={isActive(link.href) ? 'page' : undefined}
                class={cn(
                  'block rounded-md px-3 py-1.5 text-sm transition hover:bg-muted hover:text-foreground',
                  region.packages.includes(link)
                    ? 'font-medium text-foreground'
                    : 'text-muted-foreground',
                  isActive(link.href) && 'bg-muted text-foreground'
                )}
              >
                {link.label}
              </a>
            </li>
          {/each}
        </ul>
      </div>
    {/each}
  </div>
  <div class="mt-4 border-t border-border pt-3">
    <a
      href={localizeHref(allVenues.href)}
      onclick={closeMenus}
      aria-current={isActive(allVenues.href) ? 'page' : undefined}
      class="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-semibold text-foreground transition hover:bg-muted"
    >
      {allVenues.label}
      <ArrowRightIcon size={15} />
    </a>
  </div>
{/snippet}

{#snippet sheetHeading(label: string)}
  <p
    class="mt-4 px-3 pb-1 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground"
  >
    {label}
  </p>
{/snippet}

{#snippet sheetLink(link: NavLink, extraClass = '')}
  <a
    href={localizeHref(link.href)}
    aria-current={isActive(link.href) ? 'page' : undefined}
    class={cn(
      'rounded-md px-3 py-2 text-sm font-medium hover:bg-muted',
      isActive(link.href) && 'bg-muted text-foreground',
      extraClass
    )}
  >
    {link.label}
  </a>
{/snippet}

<header
  class="sticky top-0 z-30 border-b border-border bg-background/95 backdrop-blur md:-top-18"
>
  <!-- Brand row — fixed height; it scrolls out of view rather than unmounting. -->
  <div class="mx-auto flex h-18 max-w-7xl items-center gap-3 px-5 lg:px-8">
    <a href={localizeHref('/')} class="flex items-center gap-3">
      <!-- The logo is a 129x48 wordmark reading "7Magic Wedding", so it carries the
           accessible name and no repeated text sits beside it. -->
      <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-12 w-auto object-contain" />
      <span
        class="hidden border-l border-border pl-3 text-[10px] uppercase leading-tight tracking-[0.14em] text-muted-foreground sm:block"
      >
        {m.brand_tagline()}
      </span>
    </a>

    <div class="ml-auto hidden items-center gap-3 md:flex">
      {@render actions()}
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
        <!-- Scrolls: with the venue regions spelled out the list is taller
             than a phone screen. -->
        <Sheet.Content side="right" class="w-72 overflow-y-auto">
          <Sheet.Header>
            <Sheet.Title>7Magic Wedding</Sheet.Title>
          </Sheet.Header>
          <!-- Section headings rather than nested disclosures: the sheet has
               room, and it saves a tap to reach a landing page. Same groups,
               same order as the desktop row. -->
          <nav class="grid gap-1 px-4 pb-6" aria-label={m.nav_main()}>
            {@render sheetHeading(m.nav_wedding_venue())}
            {#each regions as region (region.key)}
              {@render regionHeading(region, 'mt-2 py-1 normal-case tracking-normal text-xs text-foreground')}
              {#each [...region.packages, ...region.venues] as link (link.href)}
                {@render sheetLink(link, 'pl-9')}
              {/each}
            {/each}
            {@render sheetLink(allVenues, 'mt-1 font-semibold')}

            {@render sheetHeading(menus.packages.label)}
            {#each menus.packages.items as item (item.href)}{@render sheetLink(item)}{/each}

            {@render sheetLink({ href: VENDORS_HREF, label: m.nav_vendors() }, 'mt-3')}

            {#each [menus.inspiration, menus.events] as menu (menu.key)}
              {@render sheetHeading(menu.label)}
              {#each menu.items as item (item.href)}{@render sheetLink(item)}{/each}
            {/each}

            <div class="mt-3"><LanguageSwitcher /></div>
            <!-- Spelled out here rather than rendered from the nav groups: the
                 tour CTA lives in the actions pair, so the sheet does not
                 inherit it. -->
            <Button
              href={localizeHref(TOUR_HREF)}
              variant="gold"
              size="sm"
              class="mt-2 font-semibold"
              aria-current={isActive(TOUR_HREF) ? 'page' : undefined}
            >
              {m.nav_free_venue_tour()}
            </Button>
            <Button
              variant="outline"
              size="sm"
              class="mt-2 font-semibold"
              onclick={() => (consultOpen = true)}
            >
              {m.nav_contact()}
            </Button>
          </nav>
        </Sheet.Content>
      </Sheet.Root>
    </div>
  </div>

  <!-- Nav row — h-12 rather than sized by its contents, so swapping the
       collapsed-state logo and CTA in and out cannot change the header's
       height. Items stretch to the row so the active underline stays flush
       with the bottom border. `relative` anchors the wide venue panel. -->
  <!-- The scrolled row also carries the logo and the actions, so its gaps
       tighten to keep every label on one line. -->
  <nav
    aria-label={m.nav_main()}
    class={cn(
      'relative mx-auto hidden h-12 max-w-7xl items-stretch px-5 md:flex lg:px-8',
      scrolled ? 'gap-4' : 'gap-8'
    )}
  >
    {#if scrolled}
      <a href={localizeHref('/')} class="mr-2 flex shrink-0 items-center">
        <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-8 w-auto object-contain" />
      </a>
    {/if}

    {@render menuGroup('venues', m.nav_wedding_venue(), venuesActive, [], true, venuePanel)}
    {@render menuGroup(
      menus.packages.key,
      menus.packages.label,
      menus.packages.items.some((item) => isActive(item.href)),
      menus.packages.items
    )}

    <a
      href={localizeHref(VENDORS_HREF)}
      aria-current={isActive(VENDORS_HREF) ? 'page' : undefined}
      class={cn(
        'flex items-center whitespace-nowrap border-b-2 transition',
        scrolled ? 'text-[14px]' : 'text-[15px]',
        isActive(VENDORS_HREF)
          ? 'border-brand-gold font-semibold text-foreground'
          : 'border-transparent text-muted-foreground hover:text-foreground'
      )}
    >
      {m.nav_vendors()}
    </a>

    {#each [menus.inspiration, menus.events] as menu (menu.key)}
      {@render menuGroup(
        menu.key,
        menu.label,
        menu.items.some((item) => isActive(item.href)),
        menu.items
      )}
    {/each}

    {#if scrolled}
      <div class="ml-auto flex items-center gap-3">
        {@render actions(false)}
      </div>
    {/if}
  </nav>
</header>

<ConsultationModal bind:open={consultOpen} />
