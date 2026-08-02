<script lang="ts">
  import { onMount } from 'svelte';
  import PublicFooter from '$lib/components/PublicFooter.svelte';
  import PublicHeader from '$lib/components/PublicHeader.svelte';
  import VenueClosingCta from '$lib/components/venue-detail/VenueClosingCta.svelte';
  import VenueHero from '$lib/components/venue-detail/VenueHero.svelte';
  import VenueOverview from '$lib/components/venue-detail/VenueOverview.svelte';
  import VenuePackages from '$lib/components/venue-detail/VenuePackages.svelte';
  import VenueQuoteModal from '$lib/components/venue-detail/VenueQuoteModal.svelte';
  import VenueStickyBar from '$lib/components/venue-detail/VenueStickyBar.svelte';
  import VenueVendors from '$lib/components/venue-detail/VenueVendors.svelte';
  import { normalizePhotos } from '$lib/components/venue-detail/photos';
  import type { VenueDetail } from '$lib/api';
  import { page } from '$app/state';
  import { getLocale } from '$lib/paraglide/runtime';
  import {
    absoluteUrl,
    breadcrumbList,
    graph,
    jsonLdScript,
    organization,
    venueNode,
    venuePackageNode,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { m } from '$lib/paraglide/messages.js';
  import { titleCase } from '$lib/utils';
  import { whatsappHref as buildWhatsappHref } from '$lib/whatsapp';
  import './venue-detail.css';

  let { data }: { data: { venue: VenueDetail } } = $props();

  let venue = $derived(data.venue);
  let modalOpen = $state(false);
  let submitted = $state(false);
  let showSticky = $state(false);
  let bookingCard: HTMLElement | undefined = $state();

  const cityLabel = $derived(titleCase(venue.city));
  const paxLabel = $derived(`${venue.price_for_total_pax.toLocaleString('id-ID')} pax`);
  const whatsappHref = $derived(
    buildWhatsappHref(m.vd_wa_message({ venue: venue.name }))
  );
  const photos = $derived(normalizePhotos(venue));

  // Only a real gallery photo is worth advertising as the venue's image;
  // normalizePhotos pads the gallery with placeholders to fill the mosaic.
  const primaryPhoto = $derived(photos.find((photo) => photo.real)?.src);

  const jsonLd = $derived(
    jsonLdScript(
      graph(
        organization(),
        website(),
        // The venue's description and packages are already the localized copy:
        // the loader passes ?locale, and the API overlays the venue_translations
        // row over the Indonesian base. The page node is what declares which
        // language that copy is in.
        webPageNode({
          url: page.url.pathname,
          name: venue.seo?.title ?? `${venue.name} | 7Magic Wedding`,
          description: venue.seo?.meta_description ?? venue.description,
          locale: getLocale(),
          about: `${absoluteUrl(venue.path_url)}#venue`,
          image: primaryPhoto
        }),
        venueNode(venue, { image: primaryPhoto }),
        // Absent for venues priced on request, which have no offer to describe.
        venuePackageNode(venue),
        breadcrumbList([
          { name: m.breadcrumb_home(), path: '/' },
          { name: m.breadcrumb_venues(), path: '/wedding-venue/search' },
          { name: cityLabel, path: `/wedding-venue/search?city=${venue.city}` },
          { name: venue.name }
        ])
      )
    )
  );

  function openQuote() {
    modalOpen = true;
    submitted = false;
  }

  function closeQuote() {
    modalOpen = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && modalOpen) {
      closeQuote();
    }
  }

  onMount(() => {
    if (!bookingCard) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        showSticky = !entry.isIntersecting && entry.boundingClientRect.top < 0;
      },
      { threshold: 0 }
    );

    observer.observe(bookingCard);
    return () => observer.disconnect();
  });
</script>

<svelte:head>
  <title>{venue.seo?.title ?? `${venue.name} | 7Magic Wedding`}</title>
  <meta name="description" content={venue.seo?.meta_description ?? venue.description} />
  <link rel="canonical" href={absoluteUrl(venue.seo?.canonical_url ?? venue.path_url)} />
  <link rel="icon" href="/img/7magic-logo.png" />
  <!-- {@html} rather than a plain expression: Svelte parses script contents as
       raw text, so `{jsonLd}` inside the tag would ship those nine characters
       verbatim instead of the structured data. -->
  {@html jsonLd}
</svelte:head>

<svelte:window onkeydown={handleKeydown} />

<PublicHeader />

<main class="venue-detail">
  <VenueHero
    {venue}
    {cityLabel}
    {paxLabel}
    {whatsappHref}
    {photos}
    bind:bookingCard
    onQuote={openQuote}
  />

  <VenueOverview {venue} {cityLabel} {paxLabel} />

  <VenuePackages {whatsappHref} onQuote={openQuote} />

  <VenueVendors />

  <VenueClosingCta venueName={venue.name} {whatsappHref} onQuote={openQuote} />

  <PublicFooter />

  <VenueStickyBar
    venueName={venue.name}
    {whatsappHref}
    show={showSticky}
    onQuote={openQuote}
  />

  <VenueQuoteModal
    venueName={venue.name}
    venueId={venue.id}
    venueSlug={venue.slug}
    open={modalOpen}
    bind:submitted
    onClose={closeQuote}
  />
</main>
