<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { localizeHref } from '$lib/paraglide/runtime';
  import PlausibleAnalytics from '$lib/components/PlausibleAnalytics.svelte';
  import PromotionPopup from '$lib/components/PromotionPopup.svelte';

  let { children, data } = $props();

  // Indonesian is x-default: it lives at the root and is the canonical content.
  let idHref = $derived(localizeHref(page.url.pathname, { locale: 'id' }));
  let enHref = $derived(localizeHref(page.url.pathname, { locale: 'en' }));
</script>

<svelte:head>
  <link rel="icon" href="/favicons/favicon.ico" sizes="any" />
  <link rel="alternate" hreflang="id" href={idHref} />
  <link rel="alternate" hreflang="en" href={enHref} />
  <link rel="alternate" hreflang="x-default" href={idHref} />
</svelte:head>

<PlausibleAnalytics />

{@render children()}

<PromotionPopup promotion={data.promotion} />
