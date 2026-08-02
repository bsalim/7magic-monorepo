<script lang="ts">
  import ChevronLeft from '@lucide/svelte/icons/chevron-left';
  import ChevronRight from '@lucide/svelte/icons/chevron-right';
  import * as Dialog from '$lib/components/ui/dialog';
  import { m } from '$lib/paraglide/messages.js';
  import type { DisplayPhoto } from './photos';

  let {
    photos,
    venueName,
    open = $bindable(false),
    index = $bindable(0)
  }: {
    photos: DisplayPhoto[];
    venueName: string;
    open?: boolean;
    index?: number;
  } = $props();

  let current = $derived(photos[index] ?? photos[0]);

  function step(delta: number) {
    if (!photos.length) return;
    // Wrap at both ends so the arrows never dead-end.
    index = (index + delta + photos.length) % photos.length;
  }

  function onKeydown(event: KeyboardEvent) {
    if (!open) return;
    if (event.key === 'ArrowRight') step(1);
    if (event.key === 'ArrowLeft') step(-1);
  }
</script>

<svelte:window onkeydown={onKeydown} />

<Dialog.Root bind:open>
  <Dialog.Content class="max-w-5xl border-none bg-transparent p-0 shadow-none">
    <Dialog.Header class="sr-only">
      <Dialog.Title>{m.vd_photos_of({ venue: venueName })}</Dialog.Title>
    </Dialog.Header>

    {#if current}
      <figure class="relative">
        <img
          src={current.src}
          alt={`${venueName} — ${current.label}`}
          class="max-h-[80vh] w-full rounded-card object-contain"
        />

        {#if photos.length > 1}
          <button
            type="button"
            aria-label={m.vd_prev_photo()}
            class="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-background/90 p-2.5 text-foreground shadow-md transition hover:bg-background"
            onclick={() => step(-1)}
          >
            <ChevronLeft size={20} />
          </button>
          <button
            type="button"
            aria-label={m.vd_next_photo()}
            class="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-background/90 p-2.5 text-foreground shadow-md transition hover:bg-background"
            onclick={() => step(1)}
          >
            <ChevronRight size={20} />
          </button>
        {/if}

        <figcaption
          class="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-pill bg-background/90 px-3.5 py-1.5 text-xs text-muted-foreground"
        >
          {index + 1} / {photos.length}
        </figcaption>
      </figure>
    {/if}
  </Dialog.Content>
</Dialog.Root>
