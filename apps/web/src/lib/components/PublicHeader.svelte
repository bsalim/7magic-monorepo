<script lang="ts">
  import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
  import MenuIcon from '@lucide/svelte/icons/menu';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import * as Sheet from '$lib/components/ui/sheet';
  import LanguageSwitcher from './LanguageSwitcher.svelte';
  import ConsultationModal from './ConsultationModal.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { deLocalizeHref, localizeHref } from '$lib/paraglide/runtime';
  import { page } from '$app/state';
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
  let menusEl = $state<HTMLElement | undefined>(undefined);

  // The header is h-18 (72px) tall above the nav row and pins with exactly that
  // much of itself above the viewport, so 72 is the point where the brand row
  // has just scrolled out and the compact logo/CTA should take over. The lower
  // release point is plain hysteresis, so resting right on the boundary does
  // not flip the swap back and forth.
  function onScroll() {
    scrolled = window.scrollY > (scrolled ? 56 : 72);
  }

  const links = $derived([
    { href: '/wedding-venue/search', label: m.nav_venues() },
    { href: '/wedding-showcases', label: m.nav_showcases() },
    { href: '/paket-sangjit', label: m.service_sangjit() },
    { href: '/artikel', label: m.nav_articles() },
    { href: '/our-vendors', label: m.nav_vendors() },
    { href: '/about', label: m.nav_about() }
  ]);

  // Beside Kontak rather than in `links`: the brand row stays pinned on desktop,
  // so the tour CTA is reachable at any scroll position instead of scrolling away
  // with the nav row. Outline, not gold -- two gold buttons side by side split the
  // eye, and Kontak is still the primary action.
  const TOUR_HREF = '/tour';

  // The standalone acquisition landing pages, grouped behind dropdowns rather
  // than added as top-level links: it keeps the marketplace nav short, and it
  // stops these pages being orphaned from the site's internal linking.
  //
  // Sangjit is the exception, promoted to a top-level link. Layanan holds the
  // lines that are not wedding-day work.
  const menus = $derived([
    {
      key: 'services',
      label: m.nav_services(),
      items: [
        {
          href: '/bali-wedding-planning',
          label: m.service_bali_wedding(),
          desc: m.service_bali_wedding_desc()
        },
        { href: '/perjanjian-pranikah', label: m.service_prenup(), desc: m.service_prenup_desc() },
        {
          href: '/bali-event-organizer',
          label: m.service_bali_event(),
          desc: m.service_bali_event_desc()
        }
      ]
    }
  ]);

  function isActive(href: string) {
    return current === href || current.startsWith(`${href}/`);
  }

  function menuActive(menu: { items: { href: string }[] }) {
    return menu.items.some((item) => isActive(item.href));
  }
</script>

<svelte:window
  onscroll={onScroll}
  onpointerdown={(event) => {
    // Click-outside close. The triggers live inside menusEl, so their own
    // clicks never reach this branch and the toggles keep working.
    if (openMenu && menusEl && !menusEl.contains(event.target as Node)) {
      openMenu = null;
    }
  }}
  onkeydown={(event) => {
    if (event.key === 'Escape') openMenu = null;
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
{#snippet actions()}
  <LanguageSwitcher />
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
        <Sheet.Content side="right" class="w-72">
          <Sheet.Header>
            <Sheet.Title>7Magic Wedding</Sheet.Title>
          </Sheet.Header>
          <nav class="grid gap-1 px-4">
            {#each links as link (link.href)}
              <a
                href={localizeHref(link.href)}
                aria-current={isActive(link.href) ? 'page' : undefined}
                class={cn(
                  'rounded-md px-3 py-2 text-sm font-medium hover:bg-muted',
                  isActive(link.href) && 'bg-muted text-foreground'
                )}
              >
                {link.label}
              </a>
            {/each}

            <!-- Section headings rather than nested disclosures: the sheet has
                 room, and it saves a tap to reach a landing page. -->
            {#each menus as menu (menu.key)}
              <p
                class="mt-3 px-3 pb-1 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground"
              >
                {menu.label}
              </p>
              {#each menu.items as item (item.href)}
                <a
                  href={localizeHref(item.href)}
                  aria-current={isActive(item.href) ? 'page' : undefined}
                  class={cn(
                    'rounded-md px-3 py-2 text-sm font-medium hover:bg-muted',
                    isActive(item.href) && 'bg-muted text-foreground'
                  )}
                >
                  {item.label}
                </a>
              {/each}
            {/each}

            <div class="mt-1"><LanguageSwitcher /></div>
            <!-- Spelled out here rather than rendered from `links`: the tour CTA
                 moved out of the nav row and into the actions pair, so the sheet no
                 longer inherits it. -->
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
       with the bottom border. -->
  <div class="mx-auto hidden h-12 max-w-7xl items-stretch gap-7 px-5 md:flex lg:px-8">
    {#if scrolled}
      <a href={localizeHref('/')} class="mr-2 flex items-center">
        <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-8 w-auto object-contain" />
      </a>
    {/if}

    {#each links as link (link.href)}
      <a
        href={localizeHref(link.href)}
        aria-current={isActive(link.href) ? 'page' : undefined}
        class={cn(
          'flex items-center border-b-2 text-[15px] transition',
          isActive(link.href)
            ? 'border-brand-gold font-semibold text-foreground'
            : 'border-transparent text-muted-foreground hover:text-foreground'
        )}
      >
        {link.label}
      </a>
    {/each}

    <!-- role="presentation": this wrapper only groups the triggers and their
         panels and exists to scope the hover handlers and the click-outside
         test; the semantics live on the buttons and links inside it. -->
    <div class="flex items-stretch gap-7" role="presentation" bind:this={menusEl}>
      {#each menus as menu (menu.key)}
        <!-- Opens on hover for pointer users and on click for touch, since
             this row is visible from md up and that includes tablets. -->
        <div
          class="relative flex"
          role="presentation"
          onmouseenter={() => (openMenu = menu.key)}
          onmouseleave={() => (openMenu = null)}
        >
          <button
            type="button"
            aria-expanded={openMenu === menu.key}
            aria-haspopup="true"
            onclick={() => (openMenu = menu.key)}
            class={cn(
              'flex items-center gap-1.5 border-b-2 text-[15px] transition',
              menuActive(menu)
                ? 'border-brand-gold font-semibold text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            {menu.label}
            <ChevronDownIcon
              size={15}
              class={cn('transition', openMenu === menu.key && 'rotate-180')}
            />
          </button>

          {#if openMenu === menu.key}
            <div
              class="absolute left-0 top-full z-40 w-[19rem] rounded-md border border-border bg-background p-2 shadow-lg"
            >
              {#each menu.items as item (item.href)}
                <a
                  href={localizeHref(item.href)}
                  onclick={() => (openMenu = null)}
                  aria-current={isActive(item.href) ? 'page' : undefined}
                  class={cn(
                    'block rounded-md px-3 py-2.5 transition hover:bg-muted',
                    isActive(item.href) && 'bg-muted'
                  )}
                >
                  <span class="block text-sm font-medium text-foreground">{item.label}</span>
                  <span class="mt-0.5 block text-xs leading-5 text-muted-foreground">
                    {item.desc}
                  </span>
                </a>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>

    {#if scrolled}
      <div class="ml-auto flex items-center gap-3">
        {@render actions()}
      </div>
    {/if}
  </div>
</header>

<ConsultationModal bind:open={consultOpen} />
