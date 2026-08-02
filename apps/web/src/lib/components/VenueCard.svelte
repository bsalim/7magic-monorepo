<script lang="ts">
  import MapPinIcon from '@lucide/svelte/icons/map-pin';
  import StarIcon from '@lucide/svelte/icons/star';
  import UsersIcon from '@lucide/svelte/icons/users';
  import * as Card from '$lib/components/ui/card';
  import ResponsiveImage from './ResponsiveImage.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import type { VenueCard } from '$lib/api';
  import { formatPrice } from '$lib/utils';

  let { venue }: { venue: VenueCard } = $props();

  // Cards sit in a 1-to-4 column grid, so the rendered width tracks the
  // viewport rather than the container's max width.
  const cardSizes = '(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 100vw';
</script>

<Card.Root class="gap-0 overflow-hidden py-0 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
  <a href={venue.path_url}>
    <ResponsiveImage
      image={venue.cover_photo}
      sizes={cardSizes}
      class="h-48 w-full object-cover"
    />
  </a>
  <Card.Content class="p-5">
    <div class="flex items-start justify-between gap-3">
      <h3 class="font-semibold leading-snug">
        <a href={venue.path_url}>{venue.name}</a>
      </h3>
      <span class="inline-flex items-center gap-1 text-sm font-semibold text-amber-500">
        <StarIcon size={16} fill="currentColor" />
        {venue.stars}
      </span>
    </div>
    <p class="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
      <MapPinIcon size={15} />
      {venue.district}, {venue.city}
    </p>
    <p class="mt-4 text-lg font-semibold">{formatPrice(venue.price_start_from)}</p>
    <!-- Zero pax means the package size is unknown, not that the venue seats
         nobody. Venues outside Jakarta mostly have no package data yet. -->
    {#if venue.price_for_total_pax > 0}
      <p class="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
        <UsersIcon size={15} />
        {m.card_package_for_guests({ count: venue.price_for_total_pax })}
      </p>
    {/if}
  </Card.Content>
</Card.Root>
