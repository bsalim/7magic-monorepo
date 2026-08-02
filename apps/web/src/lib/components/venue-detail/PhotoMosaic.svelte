<script lang="ts">
  import Images from '@lucide/svelte/icons/images';
  import PhotoLightbox from './PhotoLightbox.svelte';
  import { m } from '$lib/paraglide/messages.js';
  import type { DisplayPhoto } from './photos';

  let { photos, venueName }: { photos: DisplayPhoto[]; venueName: string } = $props();

  // Placeholder entries carry no src; they would render as broken tiles.
  let usable = $derived(photos.filter((photo) => photo.real && photo.src));
  let tiles = $derived(usable.slice(0, 5));
  let hasHidden = $derived(usable.length > tiles.length);

  let lightboxOpen = $state(false);
  let lightboxIndex = $state(0);

  function openAt(index: number) {
    lightboxIndex = index;
    lightboxOpen = true;
  }
</script>

{#if tiles.length}
  <div class="mosaic">
    {#each tiles as photo, index (photo.src)}
      <button
        type="button"
        class="tile"
        class:tile-lead={index === 0}
        aria-label={m.vd_view_photo({ label: photo.label })}
        onclick={() => openAt(index)}
      >
        <img
          src={photo.src}
          alt={`${venueName} — ${photo.label}`}
          loading={index === 0 ? 'eager' : 'lazy'}
          fetchpriority={index === 0 ? 'high' : 'auto'}
          decoding="async"
        />

        {#if hasHidden && index === tiles.length - 1}
          <span class="see-all">
            <Images size={16} />
            {m.vd_see_all_photos({ count: usable.length })}
          </span>
        {/if}
      </button>
    {/each}
  </div>

  <PhotoLightbox
    photos={usable}
    {venueName}
    bind:open={lightboxOpen}
    bind:index={lightboxIndex}
  />
{/if}

<style>
  .mosaic {
    display: grid;
    gap: 8px;
    grid-template-columns: 2fr 1fr 1fr;
    grid-template-rows: repeat(2, minmax(0, 1fr));
    height: 420px;
  }

  /* Below the two-column breakpoint the mosaic reads better as a simple pair. */
  @media (max-width: 720px) {
    .mosaic {
      grid-template-columns: 1fr 1fr;
      height: 300px;
    }
  }

  .tile {
    position: relative;
    overflow: hidden;
    border-radius: var(--radius-card, 10px);
    padding: 0;
    border: none;
    background: var(--muted);
    cursor: pointer;
  }

  .tile-lead {
    grid-row: span 2;
  }

  .tile img {
    height: 100%;
    width: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .tile:hover img {
    transform: scale(1.03);
  }

  .tile:focus-visible {
    outline: 2px solid var(--ring);
    outline-offset: 2px;
  }

  .see-all {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    background: rgb(0 0 0 / 45%);
    color: #fff;
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 600;
  }
</style>
