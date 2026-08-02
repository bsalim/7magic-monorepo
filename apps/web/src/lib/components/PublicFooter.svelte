<script lang="ts">
  import CameraIcon from '@lucide/svelte/icons/camera';
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import { Separator } from '$lib/components/ui/separator';
  import VenuePartners from './VenuePartners.svelte';
  import { m } from '$lib/paraglide/messages.js';

  // City names are proper nouns and stay untranslated; only the catch-all
  // link needs a message.
  const venues = [
    { href: '/wedding-venue/search?city=jakarta', label: 'Jakarta' },
    { href: '/wedding-venue/search?city=bali', label: 'Bali' },
    { href: '/wedding-venue/search?city=singapore', label: 'Singapore' },
    { href: '/wedding-venue/search', label: m.footer_all_venues() }
  ];

  const company = [
    { href: '/about', label: m.nav_about() },
    { href: '/our-vendors', label: m.nav_vendors() },
    { href: '/articles', label: m.nav_articles() },
    { href: '/contact', label: m.nav_contact() }
  ];

  // Mirrors the "Our Services" dropdown in PublicHeader. Also the only
  // crawlable link to these landing pages from the rest of the site.
  const services = [
    { href: '/perjanjian-pranikah', label: m.service_prenup() },
    { href: '/paket-sangjit', label: m.service_sangjit() },
    { href: '/bali-event-organizer', label: m.service_bali_event() }
  ];

  const legal = [
    { href: '/privacy', label: m.footer_privacy() },
    { href: '/terms', label: m.footer_terms() }
  ];

  // Bali is a placeholder until the address is confirmed.
  const offices = [
    {
      city: m.footer_office_jakarta(),
      lines: ['Jalan Gajah Mada No. 10', 'Jakarta, Indonesia 10130'],
      placeholder: false
    },
    { city: m.footer_office_bali(), lines: ['Sunday Arshika Hotel - Lobby, Sunset Road Kuta - Bali', 'Bali, 80612, Indonesia'], placeholder: false },
    { city: m.footer_office_singapore(), lines: ['110 Pasir Ris Street 11', 'Singapore 510110'], placeholder: false }
  ];

  const year = new Date().getFullYear();
</script>

<!-- Sits outside <footer> on purpose: partner credits are page content, not
     footer navigation, and every page that renders the footer wants them. -->
<VenuePartners />

<footer class="border-t border-border bg-background px-5 py-14 lg:px-8">
  <!-- Six tracks, not five: the brand block takes two so the four link
       columns each keep enough width that no item wraps mid-label. -->
  <div class="mx-auto grid max-w-7xl gap-10 md:grid-cols-2 lg:grid-cols-6 lg:gap-8">
    <div class="lg:col-span-2">
      <!-- The logo is a 129x48 wordmark; size it by height so it is not squashed. -->
      <img src="/img/7magic-logo.png" alt="7Magic Wedding" class="h-11 w-auto object-contain" />
      <p class="mt-4 max-w-xs text-sm leading-6 text-muted-foreground">
        {m.footer_tagline()}
      </p>
      <div class="mt-5 grid gap-2.5 text-sm text-muted-foreground">
        <!-- Handle text tracks the destination account: labelling this
             @7magicwedding while linking to /7magicorganizer/ would misstate
             where the link goes. -->
        <a
          href="https://www.instagram.com/7magicorganizer/"
          target="_blank"
          rel="noopener noreferrer"
          class="flex w-fit items-center gap-2 transition hover:text-foreground"
        >
          <CameraIcon size={15} /> @7magicorganizer
        </a>
      </div>
    </div>

    <div>
      <p class="font-display text-sm font-semibold text-foreground">{m.footer_wedding_venues()}</p>
      <div class="mt-4 grid gap-2.5 text-sm">
        {#each venues as item (item.href)}
          <a href={item.href} class="text-muted-foreground transition hover:text-foreground">
            {item.label}
          </a>
        {/each}
      </div>
    </div>

    <div>
      <p class="font-display text-sm font-semibold text-foreground">{m.footer_company()}</p>
      <div class="mt-4 grid gap-2.5 text-sm">
        {#each company as item (item.href)}
          <a href={item.href} class="text-muted-foreground transition hover:text-foreground">
            {item.label}
          </a>
        {/each}
      </div>
    </div>

    <div>
      <p class="font-display text-sm font-semibold text-foreground">{m.footer_services()}</p>
      <div class="mt-4 grid gap-2.5 text-sm">
        {#each services as item (item.href)}
          <a
            href={item.href}
            class="whitespace-nowrap text-muted-foreground transition hover:text-foreground"
          >
            {item.label}
          </a>
        {/each}
      </div>
    </div>

    <div>
      <p class="font-display text-sm font-semibold text-foreground">{m.footer_legal()}</p>
      <div class="mt-4 grid gap-2.5 text-sm">
        {#each legal as item (item.href)}
          <a href={item.href} class="text-muted-foreground transition hover:text-foreground">
            {item.label}
          </a>
        {/each}
      </div>
    </div>
  </div>

  <Separator class="mx-auto mt-12 max-w-7xl" />

  <div class="mx-auto mt-8 max-w-7xl">
    <p class="font-display text-sm font-semibold text-foreground">{m.footer_offices()}</p>
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
    © {year} 7Magic Wedding. {m.footer_rights()}
  </div>
</footer>
