<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { localizeHref } from '$lib/paraglide/runtime';
  import { canonicalUrl } from '$lib/seo/schema';
  import PlausibleAnalytics from '$lib/components/PlausibleAnalytics.svelte';
  import PromotionPopup from '$lib/components/PromotionPopup.svelte';

  let { children, data } = $props();

  // `localizeHref` rewrites the path structure, which is the whole story for
  // every page whose URL is the same words in both languages. Articles are not
  // one of those: their category and slug segments are translated content, so a
  // localized path built here would point at a URL that does not exist. Those
  // pages return an `alternates` map from the API and it wins.
  let alternates = $derived(page.data.alternates as Record<string, string> | undefined);

  // Absolute, because a relative hreflang annotation is ignored outright.
  //
  // A page that supplies its own `alternates` may list only one locale -- an
  // article with no English translation does -- and then only that one is
  // announced. Claiming an English version that does not exist sends English
  // searchers to Indonesian text.
  let hreflangs = $derived.by(() => {
    const map = alternates ?? {
      id: localizeHref(page.url.pathname, { locale: 'id' }),
      en: localizeHref(page.url.pathname, { locale: 'en' })
    };
    const links = Object.entries(map).map(([locale, href]) => ({
      locale,
      href: canonicalUrl(href)
    }));
    // Indonesian is x-default: it lives at the root and is the canonical content.
    if (map.id) links.push({ locale: 'x-default', href: canonicalUrl(map.id) });
    return links;
  });
</script>

<svelte:head>
  <link rel="icon" href="/favicons/favicon.ico" sizes="any" />
  {#each hreflangs as link (link.locale)}
    <link rel="alternate" hreflang={link.locale} href={link.href} />
  {/each}
</svelte:head>

<PlausibleAnalytics />

{@render children()}

<PromotionPopup promotion={data.promotion} />
