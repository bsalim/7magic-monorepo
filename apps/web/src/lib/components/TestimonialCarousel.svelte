<script lang="ts">
  import ChevronLeft from '@lucide/svelte/icons/chevron-left';
  import ChevronRight from '@lucide/svelte/icons/chevron-right';
  import Heart from '@lucide/svelte/icons/heart';
  import type { Testimonial } from '$lib/api';
  import ResponsiveImage from './ResponsiveImage.svelte';

  /**
   * The couples' reviews as a row that scrolls sideways.
   *
   * Native scroll-snap does the work, so a phone swipes through without any
   * script and the buttons only nudge the same scroll position. Seventeen cards
   * would make a grid taller than the rest of the homepage put together.
   */
  let {
    items,
    labels
  }: {
    items: Testimonial[];
    labels: { previous: string; next: string };
  } = $props();

  let track = $state<HTMLUListElement>();

  function scrollByCard(direction: 1 | -1) {
    if (!track) return;
    const card = track.querySelector('li');
    const step = card ? card.getBoundingClientRect().width + 20 : track.clientWidth * 0.8;
    track.scrollBy({ left: direction * step, behavior: 'smooth' });
  }
</script>

<div class="relative">
  <ul
    bind:this={track}
    class="-mx-5 flex snap-x snap-mandatory gap-5 overflow-x-auto scroll-smooth px-5 pb-4 [scrollbar-width:thin] lg:mx-0 lg:px-0"
  >
    {#each items as item (item.couple)}
      <li class="w-[78%] shrink-0 snap-start sm:w-[46%] lg:w-[calc((100%-3.75rem)/4)]">
        <figure class="flex h-full flex-col rounded-md border border-border bg-white p-4 shadow-sm">
          <ResponsiveImage
            image={item.photo}
            class="aspect-square w-full rounded object-cover"
            sizes="(max-width: 640px) 78vw, (max-width: 1024px) 46vw, 300px"
          />
          <blockquote class="mt-4 flex-1 text-[15px] leading-7 text-slate-700">"{item.message}"</blockquote>
          <figcaption class="mt-4 flex items-center gap-2 font-semibold">
            <Heart size={16} class="text-rose-500" aria-hidden="true" />
            {item.couple}
          </figcaption>
        </figure>
      </li>
    {/each}
  </ul>

  <div class="mt-4 flex justify-end gap-2">
    <button
      type="button"
      aria-label={labels.previous}
      onclick={() => scrollByCard(-1)}
      class="flex size-10 items-center justify-center rounded-full border border-border bg-white transition hover:border-accent-foreground/50 focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <ChevronLeft size={18} aria-hidden="true" />
    </button>
    <button
      type="button"
      aria-label={labels.next}
      onclick={() => scrollByCard(1)}
      class="flex size-10 items-center justify-center rounded-full border border-border bg-white transition hover:border-accent-foreground/50 focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <ChevronRight size={18} aria-hidden="true" />
    </button>
  </div>
</div>
