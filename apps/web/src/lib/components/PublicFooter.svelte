<script lang="ts">
  import CameraIcon from '@lucide/svelte/icons/camera';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import { Separator } from '$lib/components/ui/separator';
  import VenuePartners from './VenuePartners.svelte';
  import { INSTAGRAM_URL } from '$lib/contact';
  import { OFFICES } from '$lib/offices';
  import { m } from '$lib/paraglide/messages.js';
  import { localizeHref } from '$lib/paraglide/runtime';
  import {
    ALL_VENUES_HREF,
    companyLinks,
    eventLinks,
    inspirationLinks,
    legalLinks,
    packageLinks,
    tourLinks,
    venueRegions,
    type NavLink
  } from '$lib/site-nav';

  // The footer is the site map a person can read: every page in sitemap.xml
  // that is not a single article, venue or showcase is linked from here, in
  // the same groups as the header. Those three are reached through their index
  // pages, as on any catalogue site -- listing hundreds of them here would bury
  // the rest.
  const regions = venueRegions();

  // Columns hold one or two groups so seven groups fit four tracks without the
  // short ones (Events, Legal) standing alone in a tall empty column.
  const columns: { id: string; heading: string; links: NavLink[] }[][] = [
    [
      {
        id: 'venues',
        heading: m.nav_wedding_venue(),
        links: [
          ...regions.flatMap((region) => region.venues),
          { href: ALL_VENUES_HREF, label: m.footer_all_venues() }
        ]
      }
    ],
    [
      {
        id: 'packages',
        heading: m.nav_packages(),
        links: [...regions.flatMap((region) => region.packages), ...packageLinks(), ...tourLinks()]
      }
    ],
    [
      { id: 'inspiration', heading: m.nav_inspiration(), links: inspirationLinks() },
      { id: 'events', heading: m.nav_events(), links: eventLinks() }
    ],
    [
      { id: 'company', heading: m.footer_company(), links: companyLinks() },
      { id: 'legal', heading: m.footer_legal(), links: legalLinks() }
    ]
  ];

  // `placeholder` greys out an office whose address is not confirmed yet; all
  // three are confirmed today.
  const offices = [
    { city: m.footer_office_jakarta(), lines: OFFICES.jakarta, placeholder: false },
    { city: m.footer_office_bali(), lines: OFFICES.bali, placeholder: false },
    { city: m.footer_office_singapore(), lines: OFFICES.singapore, placeholder: false }
  ];

  // The range starts the year 7Magic began; the end year follows the clock so
  // the footer never needs a January edit.
  const FOUNDED = 2007;
  const year = new Date().getFullYear();
</script>

<!-- Sits outside <footer> on purpose: partner credits are page content, not
     footer navigation, and every page that renders the footer wants them. -->
<VenuePartners />

<footer class="border-t border-border bg-background px-5 py-14 lg:px-8">
  <!-- The brand block takes the wider first track; the four link columns share
       the rest evenly. -->
  <div
    class="mx-auto grid max-w-7xl gap-10 sm:grid-cols-2 lg:grid-cols-[minmax(0,1.3fr)_repeat(4,minmax(0,1fr))] lg:gap-8"
  >
    <div class="sm:col-span-2 lg:col-span-1">
      <!-- A link home, so the footer covers the one sitemap page it otherwise
           would not. The logo is a 129x48 wordmark; size it by height so it is
           not squashed. -->
      <a href={localizeHref('/')} class="inline-block">
        <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-11 w-auto object-contain" />
      </a>
      <p class="mt-4 max-w-xs text-sm leading-6 text-muted-foreground">
        {m.footer_tagline()}
      </p>
      <div class="mt-5 grid gap-2.5 text-sm text-muted-foreground">
        <!-- Handle text tracks the destination account: labelling this
             @7magicwedding while linking to /7magicorganizer/ would misstate
             where the link goes. -->
        <a
          href={INSTAGRAM_URL}
          target="_blank"
          rel="noopener noreferrer"
          class="flex w-fit items-center gap-2 transition hover:text-foreground"
        >
          <CameraIcon size={15} /> @7magicorganizer
        </a>
      </div>
    </div>

    {#each columns as column, index (index)}
      <div class="grid content-start gap-8">
        <!-- A labelled <nav> per group with a real heading and list, so a
             screen reader's landmark and heading menus show the site map's
             structure rather than a run of anonymous links. -->
        {#each column as group (group.id)}
          <nav aria-labelledby="footer-nav-{group.id}">
            <h2
              id="footer-nav-{group.id}"
              class="font-display text-sm font-semibold text-foreground"
            >
              {group.heading}
            </h2>
            <ul class="mt-4 grid gap-2.5 text-sm">
              {#each group.links as link (link.href)}
                <li>
                  <a
                    href={localizeHref(link.href)}
                    class="text-muted-foreground transition hover:text-foreground"
                  >
                    {link.label}
                  </a>
                </li>
              {/each}
            </ul>
          </nav>
        {/each}
      </div>
    {/each}
  </div>

  <Separator class="mx-auto mt-12 max-w-7xl" />

  <div class="mx-auto mt-8 max-w-7xl">
    <h2 class="font-display text-sm font-semibold text-foreground">{m.footer_offices()}</h2>
    <div class="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {#each offices as office (office.city)}
        <div class="rounded-card border border-border p-4">
          <p class="flex items-center gap-2 font-display text-sm font-semibold text-foreground">
            <MapPinIcon size={15} class="text-brand-gold" />
            {office.city}
          </p>
          <address
            class="mt-2 text-sm not-italic leading-6 {office.placeholder
              ? 'text-muted-foreground/60 italic'
              : 'text-muted-foreground'}"
          >
            {#each office.lines as line (line)}
              <span class="block">{line}</span>
            {/each}
          </address>
        </div>
      {/each}
    </div>
  </div>

  <Separator class="mx-auto mt-10 max-w-7xl" />

  <div class="mx-auto mt-5 max-w-7xl text-xs text-muted-foreground">
    © {FOUNDED}–{year} 7Magic Wedding. {m.footer_rights()}
  </div>
</footer>
