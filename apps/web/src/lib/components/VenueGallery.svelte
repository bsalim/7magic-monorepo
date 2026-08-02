<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import { m } from '$lib/paraglide/messages.js';
  import type { VenueDetail } from '$lib/api';

  let { venue }: { venue: VenueDetail } = $props();

  let photos = $derived(
    venue.gallery.length
      ? venue.gallery
      : [
          {
            webp: venue.cover_photo.small_url,
            fallback: venue.cover_photo.small_url
          }
        ]
  );
</script>

<div class="grid gap-3 md:grid-cols-[1.4fr_0.6fr]">
  <Dialog.Root>
    <Dialog.Trigger class="block">
      <img
        src={photos[0]?.fallback ?? venue.cover_photo.small_url}
        alt={venue.cover_photo.alt}
        class="h-[320px] w-full rounded-md object-cover md:h-[460px]"
      />
    </Dialog.Trigger>
    <Dialog.Content class="max-w-4xl">
      <Dialog.Title class="sr-only">{venue.cover_photo.alt}</Dialog.Title>
      <img
        src={photos[0]?.fallback ?? venue.cover_photo.small_url}
        alt={venue.cover_photo.alt}
        class="w-full rounded-md object-contain"
      />
    </Dialog.Content>
  </Dialog.Root>

  <div class="grid grid-cols-2 gap-3 md:grid-cols-1">
    {#each photos.slice(1, 3) as photo}
      <Dialog.Root>
        <Dialog.Trigger class="block">
          <img
            src={photo.thumbFallback ?? photo.fallback ?? venue.cover_photo.small_url}
            alt={venue.cover_photo.alt}
            class="h-36 w-full rounded-md object-cover md:h-[222px]"
          />
        </Dialog.Trigger>
        <Dialog.Content class="max-w-4xl">
          <Dialog.Title class="sr-only">{venue.cover_photo.alt}</Dialog.Title>
          <img
            src={photo.fallback ?? venue.cover_photo.small_url}
            alt={venue.cover_photo.alt}
            class="w-full rounded-md object-contain"
          />
        </Dialog.Content>
      </Dialog.Root>
    {/each}

    {#if photos.length === 1}
      <img
        src={venue.cover_photo.small_url}
        alt={venue.cover_photo.alt}
        class="h-36 w-full rounded-md object-cover md:h-[222px]"
      />
      <div
        class="flex h-36 items-center justify-center rounded-md border border-dashed border-input bg-background text-sm font-semibold text-accent-foreground md:h-[222px]"
      >
        {m.gallery_coming_soon()}
      </div>
    {/if}
  </div>
</div>
