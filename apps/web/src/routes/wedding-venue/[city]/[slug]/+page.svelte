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
    canonicalUrl,
    graph,
    jsonLdScript,
    organization,
    venueNode,
    venuePackageNode,
    webPageNode,
    website
  } from '$lib/seo/schema';
  import { m } from '$lib/paraglide/messages.js';
  import { trackEvent } from '$lib/analytics';
  import { titleCase } from '$lib/utils';
  import { localizeHref } from '$lib/paraglide/runtime';
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
  // Through the branch picker rather than straight at a branch: the branch is who
  // handles the booking, and guessing one from the venue's city would be wrong for
  // the cities that have no branch of their own. The venue id rides along so it is
  // already selected when the form opens.
  const tourHref = $derived(localizeHref(`/tour?venue=${venue.id}`));
  const photos = $derived(normalizePhotos(venue));

  // One event per venue view, alongside the automatic pageview. The pageview
  // already counts the URL; this carries the name and city so the numbers can
  // be read without decoding slugs. Re-runs on a client-side move to another
  // venue, which is when the reads below change.
  $effect(() => {
    trackEvent('Venue Viewed', {
      venue: venue.name,
      city: cityLabel,
      stars: venue.stars
    });
  });

  const trackQuoteRequest = () =>
    trackEvent('Venue Quote Requested', { venue: venue.name, city: cityLabel });

  // Only a real gallery photo is worth advertising as the venue's image;
  // normalizePhotos pads the gallery with placeholders to fill the mosaic.
  const primaryPhoto = $derived(photos.find((photo) => photo.real)?.src);
  // Only the real ones: normalizePhotos pads the mosaic with placeholders, and a
  // placeholder in structured data is a broken image to a crawler.
  const galleryImages = $derived(photos.filter((photo) => photo.real).map((photo) => photo.src));

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
        venueNode(venue, { image: primaryPhoto, images: galleryImages }),
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
  <!-- Localized: an unprefixed canonical on /en names the Indonesian URL, which
       tells Google the English page is a duplicate not to index -- while the
       hreflang tags next to it say they are alternates. The canonical wins, so
       the English venue pages were being dropped. -->
  <link
    rel="canonical"
    href={canonicalUrl(localizeHref(venue.seo?.canonical_url ?? venue.path_url))}
  />
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
    {tourHref}
    {photos}
    bind:bookingCard
    onQuote={openQuote}
  />

  <VenueOverview {venue} {cityLabel} {paxLabel} />

  <VenuePackages {whatsappHref} onQuote={openQuote} />

  <VenueVendors />

  <VenueClosingCta venueName={venue.name} {whatsappHref} {tourHref} onQuote={openQuote} />

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
    onSubmitted={trackQuoteRequest}
  />
</main>
