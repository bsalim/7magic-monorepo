<script lang="ts">
  import type { ImageRef } from '$lib/api';

  /**
   * Renders a venue image at the width the browser actually needs.
   *
   * Imported photos carry five widths in both webp and jpeg, so we emit a
   * <picture> with a webp source ahead of the jpeg fallback. Photos without
   * variants (direct CMS uploads) degrade to a plain <img>, which is why the
   * srcset attributes are conditional rather than always present -- an empty
   * srcset would override src and render nothing.
   */
  let {
    image,
    class: className = '',
    sizes,
    loading = 'lazy',
    fetchpriority,
    fallback = '/img/wedding-venue-deal-768.jpg'
  }: {
    image: ImageRef;
    class?: string;
    sizes?: string;
    loading?: 'lazy' | 'eager';
    fetchpriority?: 'high' | 'low' | 'auto';
    fallback?: string;
  } = $props();

  // The caller's sizes hint wins: it knows the slot's real width, whereas the
  // stored attribute describes the layout the image was imported for.
  const sizesAttr = $derived(sizes ?? image.sizes ?? undefined);

  function handleError(event: Event) {
    const element = event.currentTarget as HTMLImageElement;
    if (element.src.endsWith(fallback)) return;
    // Drop the srcset too, or the browser keeps re-picking a broken candidate.
    element.srcset = '';
    element.src = fallback;
  }
</script>

<picture>
  {#if image.webp_srcset}
    <source type="image/webp" srcset={image.webp_srcset} sizes={sizesAttr} />
  {/if}
  {#if image.jpeg_srcset}
    <source type="image/jpeg" srcset={image.jpeg_srcset} sizes={sizesAttr} />
  {/if}
  <img
    src={image.small_url || fallback}
    alt={image.alt}
    class={className}
    width={image.width ?? undefined}
    height={image.height ?? undefined}
    {loading}
    decoding="async"
    {fetchpriority}
    onerror={handleError}
  />
</picture>
