<script lang="ts">
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import StarIcon from '@lucide/svelte/icons/star';
  import * as Card from '$lib/components/ui/card';
  import ResponsiveImage from './ResponsiveImage.svelte';
  import VenueInquiryDialog from './VenueInquiryDialog.svelte';
  import { trackEvent } from '$lib/analytics';
  import { m } from '$lib/paraglide/messages.js';
  import type { VenueCard } from '$lib/api';
  import { titleCase } from '$lib/utils';
  import { localizeHref } from '$lib/paraglide/runtime';

  let { venue }: { venue: VenueCard } = $props();

  // Cards sit in a 1-to-4 column grid, so the rendered width tracks the
  // viewport rather than the container's max width.
  const cardSizes = '(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 100vw';

  // Always mounted, never lazily on click: a dialog created inside the opening
  // click reads that click's own pointerup as an outside press and shuts at once.
  // Closed, bits-ui renders no content, so a grid of these costs next to nothing.
  let inquiryOpen = $state(false);
</script>

<Card.Root class="gap-0 overflow-hidden py-0 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
  <a href={localizeHref(venue.path_url)}>
    <ResponsiveImage
      image={venue.cover_photo}
      sizes={cardSizes}
      class="h-48 w-full object-cover"
    />
  </a>
  <Card.Content class="p-5">
    <div class="flex items-start justify-between gap-3">
      <h3 class="font-semibold leading-snug">
        <a href={localizeHref(venue.path_url)}>{venue.name}</a>
      </h3>
      <span class="inline-flex items-center gap-1 text-sm font-semibold text-amber-500">
        <StarIcon size={16} fill="currentColor" />
        {venue.stars}
      </span>
    </div>
    <p class="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
      <MapPinIcon size={15} />
      <!-- `city` is not consistently capitalized in the catalogue -- Jakarta's
           rows carry "jakarta" -- so it is cased here rather than trusted. -->
      {venue.district}, {titleCase(venue.city)}
    </p>
    <!-- No figure on the card, priced or not: a quote depends on the date and
         the guest count, so every venue asks the team for this venue instead. -->
    <button
      type="button"
      class="mt-4 text-left text-lg font-semibold text-accent-foreground hover:underline"
      onclick={() => (inquiryOpen = true)}
    >
      {m.card_contact_for_price()}
    </button>
  </Card.Content>
</Card.Root>

<VenueInquiryDialog
  {venue}
  bind:open={inquiryOpen}
  onSubmitted={() =>
    trackEvent('Venue Quote Requested', { venue: venue.name, city: titleCase(venue.city) })}
/>
