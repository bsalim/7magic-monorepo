<script lang="ts">
  import { page } from '$app/state';
  import { getLocale } from '$lib/paraglide/runtime';
  import { absoluteUrl, canonicalUrl } from '$lib/seo/schema';

  /**
   * Open Graph and Twitter card tags: the preview a link gets when it is pasted
   * into WhatsApp, Instagram, Facebook or X. Shares in family WhatsApp groups are
   * how a venue shortlist or a celebrity wedding piece actually travels, and with
   * no tags at all those links arrived as a bare URL.
   *
   * Per page rather than in the layout: the layout cannot see the title a page
   * sets, and a scraper reads the first og:image it meets, so a layout-level
   * default would beat the page's own photo.
   */
  let {
    title,
    description,
    image,
    imageAlt,
    type = 'website',
    url,
    publishedTime,
    modifiedTime,
    section
  }: {
    title: string;
    description: string;
    image?: string | null;
    imageAlt?: string | null;
    type?: 'website' | 'article';
    /** Defaults to the current path; pass the page's canonical where it has one. */
    url?: string;
    publishedTime?: string | null;
    modifiedTime?: string | null;
    section?: string | null;
  } = $props();

  // 1200x630, the size every major scraper crops to, and kept under WhatsApp's
  // ~300 KB ceiling, above which it drops the thumbnail silently. A venue photo
  // rather than the homepage promo banners, which carry prices that go stale.
  const DEFAULT_IMAGE = '/img/og-default.jpg';

  const locale = $derived(getLocale() === 'en' ? 'en_US' : 'id_ID');
  const alternateLocale = $derived(locale === 'en_US' ? 'id_ID' : 'en_US');
  const imageUrl = $derived(absoluteUrl(image || DEFAULT_IMAGE));
  const pageUrl = $derived(canonicalUrl(url ?? page.url.pathname));
</script>

<svelte:head>
  <meta property="og:site_name" content="7Magic Wedding" />
  <meta property="og:type" content={type} />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:url" content={pageUrl} />
  <meta property="og:locale" content={locale} />
  <meta property="og:locale:alternate" content={alternateLocale} />
  <meta property="og:image" content={imageUrl} />
  {#if !image}
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
  {/if}
  {#if imageAlt}
    <meta property="og:image:alt" content={imageAlt} />
  {/if}
  {#if type === 'article'}
    {#if publishedTime}
      <meta property="article:published_time" content={publishedTime} />
    {/if}
    {#if modifiedTime}
      <meta property="article:modified_time" content={modifiedTime} />
    {/if}
    {#if section}
      <meta property="article:section" content={section} />
    {/if}
  {/if}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={title} />
  <meta name="twitter:description" content={description} />
  <meta name="twitter:image" content={imageUrl} />
</svelte:head>
